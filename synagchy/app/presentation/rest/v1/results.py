from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.infrastructure.database.models import ExamResult
from app.presentation.rest.v1.serializers import ExamResultSerializer
from app.presentation.rest.v1.pagination import PAGE_PARAMS, StandardPagination


SUBJECT_PARAM = openapi.Parameter(
    'subject_id', openapi.IN_QUERY,
    description='Derse görä netijeleri süzmek üçin subject ID',
    type=openapi.TYPE_INTEGER,
    required=False,
)


class ResultListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Ähli synag netijeleriniň sanawyny getirýär (paginated, bal boýunça sortirlen). "
            "subject_id bilen derse görä süzmek bolýar. "
            "Her netije: id, user, exam, exam_title, subject, subject_name, score, "
            "correct_count, incorrect_count, total_count, duration_seconds, created_at."
        ),
        manual_parameters=PAGE_PARAMS + [SUBJECT_PARAM],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Netijeler sanawy (paginated).",
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
        },
    )
    def get(self, request):
        results = ExamResult.objects.all().order_by('-score')
        subject_id = request.query_params.get('subject_id')
        if subject_id:
            results = results.filter(subject_id=subject_id)
        pg = StandardPagination()
        page = pg.paginate_queryset(results, request, view=self)
        serializer = ExamResultSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)


class MyResultsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=(
            "Token bilen diňe ulanyjy özüniň netijelerini getirýär (paginated, wagta görä sortirlen). "
            "subject_id bilen derse görä süzmek bolýar. "
            "Authorization header-da Bearer token hökmany. "
            "Her netije: id, user, exam, exam_title, subject, subject_name, score, "
            "correct_count, incorrect_count, total_count, duration_seconds, created_at. "
            "subject_id berlen wagty şol ders boýunça jemleýji statistikalar hem gaýtarylýar: "
            "tests_count, best_score, average_score, total_duration_seconds, total_correct, total_incorrect."
        ),
        manual_parameters=PAGE_PARAMS + [SUBJECT_PARAM],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Öz netijeleriňiz (paginated) we subject_id bar bolsa statistikalar.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'subject_stats': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="subject_id berlen wagty jemleýji statistikalar",
                            properties={
                                'subject_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'subject_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'tests_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'best_score': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'average_score': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'total_duration_seconds': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'total_correct': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'total_incorrect': openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        ),
                    },
                ),
            ),
            401: openapi.Response(description="Token ýok ýa-da ýalňyş."),
        },
    )
    def get(self, request):
        results = ExamResult.objects.filter(user=request.user).order_by('-created_at')
        subject_id = request.query_params.get('subject_id')
        if subject_id:
            results = results.filter(subject_id=subject_id)
        pg = StandardPagination()
        page = pg.paginate_queryset(results, request, view=self)
        serializer = ExamResultSerializer(page, many=True)

        response_data = dict(pg.get_paginated_response(serializer.data).data)

        if subject_id:
            subject_results = ExamResult.objects.filter(user=request.user, subject_id=subject_id)
            if subject_results.exists():
                subject = subject_results.first().subject
                total_tests = subject_results.count()
                best_score = subject_results.order_by('-score').first().score
                avg_score = round(sum(r.score for r in subject_results) / total_tests, 1)
                total_duration = sum(r.duration_seconds for r in subject_results)
                total_correct = sum(r.correct_count for r in subject_results)
                total_incorrect = sum(r.incorrect_count for r in subject_results)
                response_data['subject_stats'] = {
                    'subject_id': subject.id,
                    'subject_name': subject.name,
                    'tests_count': total_tests,
                    'best_score': best_score,
                    'average_score': avg_score,
                    'total_duration_seconds': total_duration,
                    'total_correct': total_correct,
                    'total_incorrect': total_incorrect,
                }

        return Response(response_data)
