from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from app.infrastructure.database.models import Question, Subject, ExamResult, User, Subscription
from app.presentation.rest.v1.serializers import (
    QuestionSerializer, SubmitAnswerSerializer, SubmitAnswerResponseSerializer,
    QuestionAnswerDetailSerializer,
)
from app.presentation.rest.v1.pagination import PAGE_PARAMS, StandardPagination


DIFFICULTY_PARAM = openapi.Parameter(
    'difficulty', openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description='Kynlygy boýunça filtr: easy (Kolay), medium (Orta), hard (Kyn)',
    required=False,
)

SUBJECT_ID_PARAM = openapi.Parameter(
    'subject_id', openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description='Dersiň ID-si boýunça filtr',
    required=False,
)


def _get_test_rating_points(score, duration_seconds):
    """
    Her test üçin reýting balyny hasaplaýar.
    Esasy bal dogry jogaplaryň sanyna görä (0-100).
    Wagt bonusy: test näçe çalt tamamlansa, şonça köp bonus (iň köp +10).
    """
    duration_minutes = duration_seconds / 60.0
    time_bonus = max(0, 10 - duration_minutes)
    return min(100, round(score + time_bonus))


def _recalculate_user_rating(user):
    """
    Ulanyjynyň ähli test netijelerinden reýtingini täzeden hasaplaýar.
    Reýting = ähli testleriň rating_points jemi.
    """
    total_rating = 0
    for result in ExamResult.objects.filter(user=user):
        total_rating += _get_test_rating_points(result.score, result.duration_seconds)
    user.rating = total_rating
    user.save()
    return total_rating


def _save_exam_result(user, exam, subject, score, correct_count, total_count, duration_seconds):
    incorrect_count = total_count - correct_count
    try:
        ExamResult.objects.update_or_create(
            user=user,
            exam=exam,
            subject=subject,
            defaults={
                'score': score,
                'correct_count': correct_count,
                'incorrect_count': incorrect_count,
                'total_count': total_count,
                'duration_seconds': duration_seconds,
            }
        )
    except ExamResult.MultipleObjectsReturned:
        ExamResult.objects.filter(
            user=user,
            exam=exam,
            subject=subject,
        ).delete()
        ExamResult.objects.create(
            user=user,
            exam=exam,
            subject=subject,
            score=score,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            total_count=total_count,
            duration_seconds=duration_seconds,
        )


def _has_active_subscription(user):
    try:
        sub = user.subscription
        return sub.is_active
    except Exception:
        return False


class QuestionListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=(
            "Ähli soraglaryň sanawyny getirýär (paginated). "
            "Abunasy bolan ulanyjy üçin ähli soraglar gaýtarýär, abunasy ýoksa şözüňizde 3 sany sorag preview hölmünde gaýtarýär (dogry jogaplar ýok). "
            "Soraglar subject we order (tarip) boýunça sortirlenýär: ilki ders, ondan soň order=1, order=2, ... "
            "difficulty parametri bilen kynlyk derejesine göre (easy=Kolay, medium=Orta, hard=Kyn) süzmek bolýar. "
            "subject_id parametri bilen ders boýunça süzmek bolýar. "
            "Her sorag: id, subject, order (tarip), title (soragyň kysa ady), text (sorag), "
            "option_a, option_b, option_c, option_d, difficulty_level, formula (kimyawy formula)."
        ),
        manual_parameters=PAGE_PARAMS + [DIFFICULTY_PARAM, SUBJECT_ID_PARAM],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Soraglar sanawy gaýtarýär (paginated). Abunasy ýoksa preview rejimi.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            403: openapi.Response(description="Token ýok ýa-da ýalňyş. Token bilen gaýryň."),
        },
    )
    def get(self, request):
        if not _has_active_subscription(request.user):
            # Preview mode: show only first 3 questions, no correct_answer
            questions = Question.objects.all().order_by('subject', 'order', 'id')[:3]
            serializer = QuestionSerializer(questions, many=True)
            return Response({
                'preview': True,
                'preview_count': 3,
                'total_count': Question.objects.count(),
                'detail': 'Testi açmak üçin abuna alyň. Şözüňizde 3 sany sorag preview hölmünde gösterilýär.',
                'results': serializer.data,
            })

        questions = Question.objects.all().order_by('subject', 'order', 'id')
        difficulty = request.query_params.get('difficulty')
        subject_id = request.query_params.get('subject_id')
        if difficulty:
            questions = questions.filter(difficulty_level=difficulty)
        if subject_id:
            questions = questions.filter(subject_id=subject_id)
        pg = StandardPagination()
        page = pg.paginate_queryset(questions, request, view=self)
        serializer = QuestionSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=QuestionSerializer,
        responses={
            201: openapi.Response(description="Üstünlikli sorag döredildi."),
            400: openapi.Response(description="Nädogry maglumat. Bütin meýdanlar doldurylmaly."),
        },
        operation_description=(
            "Täze sorag döredýır. Admin paneli üçin. "
            "Sorag bir derse (subject) bagly bolmaly. "
            "Soragyň mazmuny (text) we 4 sany wariant (option_a, option_b, option_c, option_d) hökmany. "
            "title (soragyň kysa ady) we formula (kimyawy formula) awomatik text-den tapylýar. "
            "difficulty_level (kynlyk derejesi): easy (ýönekeý), medium (Orta), hard (Kyn). Default=medium. "
            "correct_answer: dogry jogap (A, B, C, D). "
            "Dogry jogap şuwede görünmeýär, diňe admin görýär."
        ),
    )
    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  

class QuestionBySubjectView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=(
            "Bir derstiň soraglaryny getirýär (paginated). "
            "subject_id URL param bilen berilýär. "
            "Soraglar order (tarip) boýunça sortirlenýär: order=1, order=2, ... "
            "Abunasy bolan ulanyjy üçin ähli soraglar gaýtarýär, abunasy ýoksa şözüňizde 3 sany sorag preview hölmünde gaýtarýär (dogry jogaplar ýok). "
            "difficulty parametri bilen kynlyk derejesine göre (easy=Kolay, medium=Orta, hard=Kyn) süzmek bolýar. "
            "Her sorag: id, subject, order (tarip), title (soragyň kysa ady), text, option_a, option_b, "
            "option_c, option_d, difficulty_level, formula (kimyawy formula)."
        ),
        manual_parameters=PAGE_PARAMS + [
            openapi.Parameter(
                'subject_id', openapi.IN_PATH,
                description='Dersiň ID-si (mesele: 1=Fizika, 2=Matematika)',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            DIFFICULTY_PARAM,
        ],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Derstiň soraglary gaýtarýär (paginated). Abunasy ýoksa preview rejimi.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            403: openapi.Response(description="Token ýok ýa-da ýalňyş. Token bilen gaýryň."),
        },
    )
    def get(self, request, subject_id):
        if not _has_active_subscription(request.user):
            # Preview mode: show only first 3 questions, no correct_answer
            questions = Question.objects.filter(subject_id=subject_id).order_by('order', 'id')[:3]
            serializer = QuestionSerializer(questions, many=True)
            return Response({
                'preview': True,
                'preview_count': 3,
                'total_count': Question.objects.filter(subject_id=subject_id).count(),
                'detail': 'Testi açmak üçin abuna alyň. Şözüňizde 3 sany sorag preview hölmünde gösterilýär.',
                'results': serializer.data,
            })

        questions = Question.objects.filter(subject_id=subject_id).order_by('order', 'id')
        difficulty = request.query_params.get('difficulty')
        if difficulty:
            questions = questions.filter(difficulty_level=difficulty)
        pg = StandardPagination()
        page = pg.paginate_queryset(questions, request, view=self)
        serializer = QuestionSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)


class SubmitAnswerView(APIView):
    """
    Soraglary çözüp, netijäni hasaplaýar we reytingi täzeläýär.
    POST: {subject_id, answers: {question_id: 'A'}, }
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=SubmitAnswerSerializer,
        responses={
            200: openapi.Response(
                description=(
                    "Üstünlikli test hasablandy. Netije: dogry_jogap_sany, ýalňyş_jogap_sany, "
                    "umumy_sorag_sany, ball (%), geçen_wagt (sekunt), ulanyjynyň täzelenen reýtingi "
                    "we her soragyň dogry/ýalňyş jikme-jigi."
                ),
                schema=SubmitAnswerResponseSerializer,
            ),
            400: openapi.Response(description="Nädogry maglumat. subject_id ýa-da answers ýok."),
            403: openapi.Response(description="Abuna gerek. Abunasy ýoksa test çözmek ýok."),
        },
        operation_description=(
            "Soraglary çözýır we netijäni hasaplaýar. Token gerek. "
            "Abunasy bolan ulanyjy bilen test çözmek bolýar, abunasy ýoksa 403 gaýtarýär. "
            "Body: {\"subject_id\": 1, \"answers\": {\"1\": \"A\", \"2\": \"B\"}}. "
            "Her sorag ID we jogap (A/B/C/D) bilen iberilýär. "
            "Netijede: correct_count (dogry jogap sany), incorrect_count (ýalňyş jogap sany), "
            "total_count (umumy sorag sany), score (netije %), duration_seconds (sekunt), "
            "rating (ulanyjynyň täzelenen reýtingi), details (her soragyň jikme-jigi: question_id, title, text, "
            "difficulty_level, user_answer, correct_answer, is_correct) gaýtarylýar. "
            "duration_seconds body-de iberilýär (testiň näçe wagt dowam edendigi). "
            "Bu netije hem ExamResult bazasyna ýazylýar we ulanyjynyň reýtingi täzelenýär. "
            "Reýting: her testiň dogrylyk baly (0-100) + wagt bonusy (iň köp +10, çalt gutaran saýlaw) jeminden ybarat."
        ),
    )
    def post(self, request):
        has_sub = _has_active_subscription(request.user)
        if not has_sub:
            return Response(
                {'detail': 'Testi çözmek üçin abuna alyň. Abunasyz test çözmek ýok.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        subject_id = request.data.get('subject_id')
        answers = request.data.get('answers', {})
        duration_seconds = request.data.get('duration_seconds', 0) or 0
        user = request.user

        questions = Question.objects.filter(subject_id=subject_id).order_by('order', 'id')
        total = questions.count()
        correct_count = 0

        # Her soragyň netijesi (swaggerde düşnükli görünmek üçin)
        details = []
        for q in questions:
            user_ans = (answers.get(str(q.id)) or '').upper()
            is_correct = bool(user_ans) and user_ans == q.correct_answer
            if is_correct:
                correct_count += 1
            details.append({
                'question_id': q.id,
                'order': q.order,
                'title': q.title,
                'text': q.text,
                'difficulty_level': q.difficulty_level,
                'user_answer': user_ans,
                'correct_answer': q.correct_answer,
                'is_correct': is_correct,
            })

        # Bal hasaplamak (her dogry jogap 100/total bal)
        score = round((correct_count / total) * 100) if total > 0 else 0
        incorrect_count = total - correct_count

        subject = questions.first().subject if total > 0 else None
        if subject is not None:
            exams = list(subject.exams.all())
            if exams:
                for exam in exams:
                    _save_exam_result(
                        user, exam, subject, score, correct_count, total, duration_seconds
                    )
            else:
                _save_exam_result(
                    user, None, subject, score, correct_count, total, duration_seconds
                )
        else:
            ExamResult.objects.create(
                user=user,
                exam=None,
                subject=None,
                score=score,
                correct_count=correct_count,
                incorrect_count=incorrect_count,
                total_count=total,
                duration_seconds=duration_seconds,
            )

        rating = _recalculate_user_rating(user)

        return Response({
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'total_count': total,
            'score': score,
            'duration_seconds': duration_seconds,
            'rating': rating,
            'details': details,
        })


class RandomTestView(APIView):
    """
    Täze test döredýär: umumy soraglardan random edip saylap, çözmek üçin gaýtarýär.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=(
            "Täze test döredýär we çözmek üçin gaýtarýär. Token gerek. "
            "subject_id parametri bilen ders, count parametri bilen sorag sany, "
            "difficulty parametri bilen kynlyk derejesi häsiýetlendirilýär. "
            "order parametri bilen soraglar order (tarip) boýunça ýa-da random edip saýlanýar. "
            "order=true bolsa soraglar 1-den başlap order boýunça gaýtarýär, "
            "order=false bolsa soraglar random edip saýlanýar. "
            "Abunasy ýoksa 403 gaýtarýär. "
            "Her sorag: id, subject, order, title, text, option_a, option_b, option_c, option_d, difficulty_level, formula."
        ),
        manual_parameters=[
            openapi.Parameter(
                'subject_id', openapi.IN_QUERY,
                description='Dersiň ID-si (mesele: 1=Fizika, 2=Matematika)',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                'count', openapi.IN_QUERY,
                description='Sorag sany (1-50)',
                type=openapi.TYPE_INTEGER,
                default=10,
            ),
            openapi.Parameter(
                'difficulty', openapi.IN_QUERY,
                description='Kynlyk derejesi: easy (Kolay), medium (Orta), hard (Kyn)',
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'order', openapi.IN_QUERY,
                description='Soraglar order (tarip) boýunça True/False. Default=True.',
                type=openapi.TYPE_BOOLEAN,
                default=True,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Täze test döredildi.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'test_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Test ID-si"),
                        'subject_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'subject_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'ordered': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Order boýunça saýlandymy?"),
                        'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            403: openapi.Response(description="Abuna gerek. Abunasy ýoksa test dördip biler."),
        },
    )
    def get(self, request):
        if not _has_active_subscription(request.user):
            return Response(
                {'detail': 'Test dörmek üçin abuna alyň.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        import random
        from app.infrastructure.database.models import Subject

        subject_id = request.query_params.get('subject_id')
        count = int(request.query_params.get('count', 10))
        difficulty = request.query_params.get('difficulty')
        order_by_order = request.query_params.get('order', 'true').lower() == 'true'

        qs = Question.objects.filter(subject_id=subject_id)
        if difficulty:
            qs = qs.filter(difficulty_level=difficulty)

        total = qs.count()
        if total == 0:
            return Response(
                {'detail': 'Bu dersde sorag ýok.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        actual_count = min(count, total)
        if order_by_order:
            random_questions = list(qs.order_by('order', 'id')[:actual_count])
        else:
            random_questions = list(qs.order_by('?')[:actual_count])
        serializer = QuestionSerializer(random_questions, many=True)

        try:
            subject = Subject.objects.get(id=subject_id)
            subject_name = subject.name
        except Subject.DoesNotExist:
            subject_name = None

        return Response({
            'test_id': random_questions[0].id if random_questions else 0,
            'subject_id': subject_id,
            'subject_name': subject_name,
            'total_count': actual_count,
            'ordered': order_by_order,
            'questions': serializer.data,
        })
