
import strawberry
from strawberry.scalars import JSON as JSONScalar
from django.db.models import Sum
from django.db.models import Avg


# ============================================================
# GraphQL TYPES
# ============================================================

@strawberry.type
class RegionType:
    id: int
    name: str
    description: str | None = None


@strawberry.type
class SpecialtyRegionAdmissionType:
    """Hünäriň etrap boýunça giriş maglumatlary."""
    id: int
    region_id: int
    region_name: str
    admission_capacity: int
    applications_count: int
    exam_start_at: str | None = None


@strawberry.type
class UserType:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    rating: int
    subscription_rank: int
    region_id: int | None = None
    region_name: str | None = None


@strawberry.type
class UniversityType:
    id: int
    name: str
    city: str
    description: str
    exam_info: str | None = None
    about: str | None = None
    image_url: str | None = None


@strawberry.type
class FacultyType:
    id: int
    university_id: int
    name: str
    description: str


@strawberry.type
class SpecialtyType:
    id: int
    faculty_id: int
    name: str
    description: str
    required_documents: str | None = None
    application_deadline: str | None = None
    region_admissions: list[SpecialtyRegionAdmissionType]


@strawberry.type
class EntranceExamType:
    id: int
    specialty_id: int
    title: str
    description: str


@strawberry.type
class SubjectType:
    id: int
    exam_ids: list[int]
    name: str
    max_score: int
    image_url: str | None = None


@strawberry.type
class QuestionType:
    id: int
    subject_id: int
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty_level: str


@strawberry.type
class LectureTopicType:
    id: int
    subject_id: int
    title: str
    description: str
    order: int


@strawberry.type
class LectureType:
    id: int
    lecture_id: int
    title: str
    content_type: str
    content_text: str
    image_url: str | None = None
    pdf_url: str | None = None
    audio_url: str | None = None
    video_url: str | None = None
    order: int
    topics_count: int


@strawberry.type
class ExamResultType:
    id: int
    user_id: int
    exam_id: int | None = None
    subject_id: int | None = None
    score: int
    correct_count: int
    incorrect_count: int
    total_count: int
    duration_seconds: int


@strawberry.type
class SubscriptionType:
    id: int
    user_id: int
    plan: str
    is_active: bool


@strawberry.type
class RatingEntry:
    rank: int
    user_id: int
    username: str
    rating: int
    discount: str | None = None


@strawberry.type
class QuestionAnswerDetail:
    question_id: int
    text: str
    difficulty_level: str
    user_answer: str
    correct_answer: str
    is_correct: bool


@strawberry.type
class SubmitAnswerResult:
    correct_count: int
    incorrect_count: int
    total_count: int
    score: int
    duration_seconds: int
    rating: int
    details: list[QuestionAnswerDetail]


# ============================================================
# QUERY
# ============================================================

@strawberry.type
class Query:

    # --------------------------------------------------------
    # REGIONS
    # --------------------------------------------------------

    @strawberry.field(description="Ähli etraplaryŋ sanawyny getirýer.")
    def regions(self) -> list[RegionType]:
        from app.infrastructure.database.models import Region

        regions = Region.objects.all().order_by("id")

        return [
            RegionType(
                id=r.id,
                name=r.name,
                description=r.description or None,
            )
            for r in regions
        ]

    @strawberry.field(description="Etrap ID-sine göre etrapyŋ jikme-jig maglumatlaryny getirýer.")
    def region(self, id: int) -> RegionType | None:
        from app.infrastructure.database.models import Region

        try:
            r = Region.objects.get(pk=id)
        except Region.DoesNotExist:
            return None

        return RegionType(
            id=r.id,
            name=r.name,
            description=r.description or None,
        )

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    @strawberry.field(description="Ähli ulanyjylaryŋ sanawyny reýting boýunça getirýer.")
    def users(self) -> list[UserType]:
        from app.infrastructure.database.models import User, ExamResult

        users_with_stats = []
        for user in User.objects.all():
            total_rating = 0
            total_duration = 0
            for result in ExamResult.objects.filter(user=user):
                duration_minutes = result.duration_seconds / 60.0
                time_bonus = max(0, 10 - duration_minutes)
                test_rating = min(100, round(result.score + time_bonus))
                total_rating += test_rating
                total_duration += result.duration_seconds
            users_with_stats.append((user, total_rating, total_duration))

        users_with_stats.sort(key=lambda x: (-x[1], x[2], x[0].id))

        return [
            UserType(
                id=u.id,
                username=u.username,
                email=u.email,
                first_name=u.first_name,
                last_name=u.last_name,
                full_name=u.full_name,
                rating=rating,
                subscription_rank=u.subscription_rank,
                region_id=u.region_id,
                region_name=u.region.name if u.region else None,
            )
            for u, rating, total_duration in users_with_stats
        ]

    # --------------------------------------------------------
    # UNIVERSITIES
    # --------------------------------------------------------

    @strawberry.field(description="Ähli uniwersitetleriŋ sanawyny getirýer.")
    def universities(self) -> list[UniversityType]:
        from app.infrastructure.database.models import University

        universities = University.objects.all().order_by("id")

        return [
            UniversityType(
                id=u.id,
                name=u.name,
                city=u.city,
                description=u.description,
                exam_info=u.exam_info or None,
                about=u.about or None,
                image_url=u.image.url if u.image else None,
            )
            for u in universities
        ]

    # --------------------------------------------------------
    # FACULTIES
    # --------------------------------------------------------

    @strawberry.field(description="Ähli fakultetleriŋ sanawyny getirýer.")
    def faculties(self) -> list[FacultyType]:
        from app.infrastructure.database.models import Faculty

        faculties = Faculty.objects.all().order_by("id")

        return [
            FacultyType(
                id=f.id,
                university_id=f.university_id,
                name=f.name,
                description=f.description,
            )
            for f in faculties
        ]

    # --------------------------------------------------------
    # SPECIALTIES
    # --------------------------------------------------------

    @strawberry.field(description="Ähli hünärleriŋ sanawyny getirýer. Etrap boýunça filtr için region argümentini ulanyň.")
    def specialties(self, region_id: int | None = None) -> list[SpecialtyType]:
        from app.infrastructure.database.models import Specialty

        specialties = Specialty.objects.all().prefetch_related(
            "region_admissions",
            "region_admissions__region",
        ).order_by("id")

        if region_id is not None:
            specialties = specialties.filter(region_admissions__region_id=region_id).distinct()

        result = []
        for s in specialties:
            admissions = [
                SpecialtyRegionAdmissionType(
                    id=ra.id,
                    region_id=ra.region_id,
                    region_name=ra.region.name,
                    admission_capacity=ra.admission_capacity,
                    applications_count=ra.applications_count,
                    exam_start_at=(
                        ra.exam_start_at.isoformat()
                        if ra.exam_start_at
                        else None
                    ),
                )
                for ra in s.region_admissions.all().order_by("region_id")
            ]
            result.append(
                SpecialtyType(
                    id=s.id,
                    faculty_id=s.faculty_id,
                    name=s.name,
                    description=s.description,
                    required_documents=s.required_documents or None,
                    application_deadline=(
                        s.application_deadline.isoformat()
                        if s.application_deadline
                        else None
                    ),
                    region_admissions=admissions,
                )
            )
        return result

    @strawberry.field(description="Etrap ID-sine göre hündirleriŋ (hünärleriŋ) etrap adıtlık maglumatlaryny görmek üçin region boýunça filtrleme.")
    def specialties_by_region(
        self,
        region_id: int,
    ) -> list[SpecialtyType]:
        from app.infrastructure.database.models import Specialty

        specialties = (
            Specialty.objects
            .filter(region_admissions__region_id=region_id)
            .prefetch_related(
                "region_admissions",
                "region_admissions__region",
            )
            .distinct()
            .order_by("id")
        )

        result = []
        for s in specialties:
            admissions = [
                SpecialtyRegionAdmissionType(
                    id=ra.id,
                    region_id=ra.region_id,
                    region_name=ra.region.name,
                    admission_capacity=ra.admission_capacity,
                    applications_count=ra.applications_count,
                    exam_start_at=(
                        ra.exam_start_at.isoformat()
                        if ra.exam_start_at
                        else None
                    ),
                )
                for ra in s.region_admissions.filter(region_id=region_id).order_by("region_id")
            ]
            result.append(
                SpecialtyType(
                    id=s.id,
                    faculty_id=s.faculty_id,
                    name=s.name,
                    description=s.description,
                    required_documents=s.required_documents or None,
                    application_deadline=(
                        s.application_deadline.isoformat()
                        if s.application_deadline
                        else None
                    ),
                    region_admissions=admissions,
                )
            )
        return result

    # --------------------------------------------------------
    # EXAMS
    # --------------------------------------------------------

    @strawberry.field(description="Ähli giriş synaglarynyŋ sanawyny getirýer.")
    def exams(self) -> list[EntranceExamType]:
        from app.infrastructure.database.models import EntranceExam

        exams = EntranceExam.objects.all().order_by("id")

        return [
            EntranceExamType(
                id=e.id,
                specialty_id=e.specialty_id,
                title=e.title,
                description=e.description,
            )
            for e in exams
        ]

    # --------------------------------------------------------
    # EXAMS BY SPECIALTY
    # --------------------------------------------------------

    @strawberry.field(description="Hünär ID-si boýunça synatların sanawyny getirýer.")
    def exams_by_specialty(
        self,
        specialty_id: int,
    ) -> list[EntranceExamType]:
        from app.infrastructure.database.models import EntranceExam

        exams = (
            EntranceExam.objects
            .filter(specialty_id=specialty_id)
            .order_by("id")
        )

        return [
            EntranceExamType(
                id=e.id,
                specialty_id=e.specialty_id,
                title=e.title,
                description=e.description,
            )
            for e in exams
        ]

    # --------------------------------------------------------
    # SUBJECTS
    # --------------------------------------------------------

    @strawberry.field(description="Ähli dersleriŋ sanawyny getirýer.")
    def subjects(self) -> list[SubjectType]:
        from app.infrastructure.database.models import Subject

        subjects = Subject.objects.all().order_by("id")

        return [
            SubjectType(
                id=s.id,
                exam_ids=list(s.exams.values_list('id', flat=True)),
                name=s.name,
                max_score=s.max_score,
                image_url=s.image.url if s.image else None,
            )
            for s in subjects
        ]

    # --------------------------------------------------------
    # SUBJECTS BY EXAM
    # --------------------------------------------------------

    @strawberry.field(description="Synat ID-si boýunça dersleriŋ sanawyny getirýer.")
    def subjects_by_exam(
        self,
        exam_id: int,
    ) -> list[SubjectType]:
        from app.infrastructure.database.models import Subject

        subjects = (
            Subject.objects
            .filter(exams__id=exam_id)
            .order_by("id")
        )

        return [
            SubjectType(
                id=s.id,
                exam_ids=list(s.exams.values_list('id', flat=True)),
                name=s.name,
                max_score=s.max_score,
                image_url=s.image.url if s.image else None,
            )
            for s in subjects
        ]

    # --------------------------------------------------------
    # SUBJECTS BY SPECIALTY
    # --------------------------------------------------------

    @strawberry.field(description="Hünär ID-si boýunça dersleriŋ sanawyny getirýer.")
    def subjects_by_specialty(
        self,
        specialty_id: int,
    ) -> list[SubjectType]:
        from app.infrastructure.database.models import (
            Subject,
            EntranceExam,
        )

        subjects = (
            Subject.objects
            .filter(exams__specialty_id=specialty_id)
            .order_by("id")
        )

        return [
            SubjectType(
                id=s.id,
                exam_ids=list(s.exams.values_list('id', flat=True)),
                name=s.name,
                max_score=s.max_score,
                image_url=s.image.url if s.image else None,
            )
            for s in subjects
        ]

    # --------------------------------------------------------
    # TOPICS BY SUBJECT
    # --------------------------------------------------------

    @strawberry.field(description="Ders ID-si boýunça leksiyä temalary getirýer.")
    def topics_by_subject(
        self,
        subject_id: int,
    ) -> list[LectureTopicType]:
        from app.infrastructure.database.models import LectureTopic

        topics = (
            LectureTopic.objects
            .filter(lecture__subject_id=subject_id)
            .select_related("lecture")
            .order_by("order", "id")
        )

        return [
            LectureTopicType(
                id=t.id,
                subject_id=t.lecture.subject_id,
                title=t.title,
                description=t.description,
                order=t.order,
            )
            for t in topics
        ]

    # --------------------------------------------------------
    # LECTURES BY TOPIC
    # --------------------------------------------------------

    @strawberry.field(description="Tema ID-si boýunça leksiyalary getirýer.")
    def lectures_by_topic(
        self,
        topic_id: int,
    ) -> list[LectureType]:
        from app.infrastructure.database.models import Lecture

        lectures = (
            Lecture.objects
            .filter(topics__id=topic_id)
            .distinct()
            .order_by("order", "id")
        )

        return [
            LectureType(
                id=l.id,
                lecture_id=l.id,
                title=l.title,
                content_type=l.content_type,
                content_text=l.content_text,
                image_url=l.image.url if l.image else None,
                pdf_url=l.pdf_file.url if l.pdf_file else None,
                audio_url=l.audio.url if l.audio else None,
                video_url=l.video.url if l.video else None,
                order=l.order,
                topics_count=l.topics_count,
            )
            for l in lectures
        ]

    # --------------------------------------------------------
    # QUESTIONS BY SUBJECT
    # --------------------------------------------------------

    @strawberry.field(description="Ders ID-si boýunça soragları getirýer. difficulty argümentini ulanyň: easy, medium, hard.")
    def questions_by_subject(
        self,
        subject_id: int,
        difficulty: str | None = None,
    ) -> list[QuestionType]:
        from app.infrastructure.database.models import Question

        questions = (
            Question.objects
            .filter(subject_id=subject_id)
            .order_by("id")
        )

        if difficulty is not None:
            questions = questions.filter(difficulty_level=difficulty)

        return [
            QuestionType(
                id=q.id,
                subject_id=q.subject_id,
                text=q.text,
                option_a=q.option_a,
                option_b=q.option_b,
                option_c=q.option_c,
                option_d=q.option_d,
                difficulty_level=q.difficulty_level,
            )
            for q in questions
        ]

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    @strawberry.field(description="Ähli synat netijeleriniŋ sanawyny getirýer. subject_id bilen süzmek bolýar.")
    def results(self, subject_id: int | None = None) -> list[ExamResultType]:
        from app.infrastructure.database.models import ExamResult

        results = (
            ExamResult.objects
            .all()
            .order_by("-score", "id")
        )

        if subject_id is not None:
            results = results.filter(subject_id=subject_id)

        return [
            ExamResultType(
                id=r.id,
                user_id=r.user_id,
                exam_id=r.exam_id,
                subject_id=r.subject_id,
                score=r.score,
                correct_count=r.correct_count,
                incorrect_count=r.incorrect_count,
                total_count=r.total_count,
                duration_seconds=r.duration_seconds,
            )
            for r in results
        ]

    # --------------------------------------------------------
    # SUBSCRIPTIONS
    # --------------------------------------------------------

    @strawberry.field(description="Ähli abunalaryŋ sanawyny getirýer.")
    def subscriptions(self) -> list[SubscriptionType]:
        from app.infrastructure.database.models import Subscription

        subscriptions = (
            Subscription.objects
            .all()
            .order_by("id")
        )

        return [
            SubscriptionType(
                id=s.id,
                user_id=s.user_id,
                plan=s.plan,
                is_active=s.is_active,
            )
            for s in subscriptions
        ]

    # --------------------------------------------------------
    # RATING
    # --------------------------------------------------------

    @strawberry.field(description="Ulanyjylaryŋ reýting tabilisany getirýer. Reýting dogrylyk baly + wagt bonusy boýunça. Deŋ reýtingde çalt gutaran öŋde. Top 3-e 50%, 30%, 20% yenillik.")
    def rating(self) -> list[RatingEntry]:
        from app.infrastructure.database.models import User, ExamResult

        discount_map = {
            1: "50%",
            2: "30%",
            3: "20%",
        }

        users_with_stats = []
        for user in User.objects.all():
            total_rating = 0
            total_duration = 0
            for result in ExamResult.objects.filter(user=user):
                duration_minutes = result.duration_seconds / 60.0
                time_bonus = max(0, 10 - duration_minutes)
                test_rating = min(100, round(result.score + time_bonus))
                total_rating += test_rating
                total_duration += result.duration_seconds
            users_with_stats.append((user, total_rating, total_duration))

        users_with_stats.sort(key=lambda x: (-x[1], x[2], x[0].id))

        return [
            RatingEntry(
                rank=index + 1,
                user_id=user.id,
                username=user.username,
                rating=rating,
                discount=discount_map.get(index + 1),
            )
            for index, (user, rating, total_duration) in enumerate(users_with_stats)
        ]


# ============================================================
# MUTATION
# ============================================================

@strawberry.type
class Mutation:

    @strawberry.mutation(description="Soragları çözer we netijäni hasaplaýar. Ulanyjy ID, ders ID we geçen wagt (duration_seconds, sekunt) hökmany.")
    def submit_answer(
        self,
        user_id: int,
        subject_id: int,
        answers: JSONScalar,
        duration_seconds: int = 0,
    ) -> SubmitAnswerResult:

        """
        answers mysal:

        {
            "1": "B",
            "2": "A",
            "3": "C"
        }
        """

        from app.infrastructure.database.models import (
            User,
            Question,
            ExamResult,
        )

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        user = User.objects.get(pk=user_id)

        # ----------------------------------------------------
        # QUESTIONS
        # ----------------------------------------------------

        questions = list(
            Question.objects
            .filter(subject_id=subject_id)
            .order_by("id")
        )

        total = len(questions)
        correct_count = 0

        details: list[QuestionAnswerDetail] = []

        # ----------------------------------------------------
        # CHECK ANSWERS
        # ----------------------------------------------------

        for question in questions:

            answer = answers.get(str(question.id))

            user_answer = (
                str(answer).strip().upper()
                if answer is not None
                else ""
            )

            correct_answer = (
                str(question.correct_answer).strip().upper()
            )

            is_correct = (
                bool(user_answer)
                and user_answer == correct_answer
            )

            if is_correct:
                correct_count += 1

            details.append(
                QuestionAnswerDetail(
                    question_id=question.id,
                    text=question.text,
                    difficulty_level=question.difficulty_level,
                    user_answer=user_answer,
                    correct_answer=correct_answer,
                    is_correct=is_correct,
                )
            )

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        score = (
            round((correct_count / total) * 100)
            if total > 0
            else 0
        )

        incorrect_count = total - correct_count

        # ----------------------------------------------------
        # EXAM
        # ----------------------------------------------------

        exams = (
            list(questions[0].subject.exams.all())
            if questions
            else []
        )

        # ----------------------------------------------------
        # SAVE RESULT
        # ----------------------------------------------------

        if exams:
            for exam in exams:
                try:
                    ExamResult.objects.update_or_create(
                        user=user,
                        exam=exam,
                        subject=questions[0].subject if questions else None,
                        defaults={
                            "score": score,
                            "correct_count": correct_count,
                            "incorrect_count": incorrect_count,
                            "total_count": total,
                            "duration_seconds": duration_seconds,
                        },
                    )
                except ExamResult.MultipleObjectsReturned:
                    ExamResult.objects.filter(
                        user=user,
                        exam=exam,
                        subject=questions[0].subject if questions else None,
                    ).delete()
                    ExamResult.objects.create(
                        user=user,
                        exam=exam,
                        subject=questions[0].subject if questions else None,
                score=score,
                correct_count=correct_count,
                incorrect_count=incorrect_count,
                total_count=total,
                duration_seconds=duration_seconds,
                    )
        elif questions:
            ExamResult.objects.create(
                user=user,
                exam=None,
                subject=questions[0].subject,
                score=score,
                correct_count=correct_count,
                total_count=total,
            )
        else:
            ExamResult.objects.create(
                user=user,
                exam=None,
                subject=None,
                score=score,
                correct_count=correct_count,
                total_count=total,
            )

        # ----------------------------------------------------
        # UPDATE USER RATING
        # ----------------------------------------------------

        all_results = (
            ExamResult.objects
            .filter(user=user)
        )

        total_rating = 0
        for result in all_results:
            duration_minutes = result.duration_seconds / 60.0
            time_bonus = max(0, 10 - duration_minutes)
            test_rating = min(100, round(result.score + time_bonus))
            total_rating += test_rating

        user.rating = total_rating

        user.save(update_fields=["rating"])

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return SubmitAnswerResult(
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            total_count=total,
            score=score,
            duration_seconds=duration_seconds,
            rating=getattr(user, "rating", 0),
            details=details,
        )


# ============================================================
# GRAPHQL SCHEMA
# ============================================================

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
