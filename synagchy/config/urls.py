"""
URL configuration for synagchy project.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from strawberry.django.views import GraphQLView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from app.presentation.rest.v1 import (
    auth,
    users,
    universities,
    exams,
    subjects,
    questions,
    results,
    subscription,
    payment,
    lectures,
    schools,
    tutors,
    videos,
    regions,
)
from app.presentation.graphql.schema import schema
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

# GraphQL
    path('graphql/', csrf_exempt(GraphQLView.as_view(schema=schema)), name='graphql'),

    # Auth
    path('api/v1/auth/register/', auth.RegisterView.as_view(), name='register'),
    path('api/v1/auth/login/', auth.LoginView.as_view(), name='login'),
    path('api/v1/auth/change-password/', auth.ChangePasswordView.as_view(), name='change-password'),
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Users & Rating
path('api/v1/users/', users.UserListView.as_view(), name='user-list'),
    path('api/v1/users/<int:pk>/', users.UserDetailView.as_view(), name='user-detail'),
    path('api/v1/profile/', users.ProfileView.as_view(), name='profile'),
 path('api/v1/rating/', users.RatingListView.as_view(), name='rating'),
    path('api/v1/my-university/', users.MyUniversityView.as_view(), name='my-university'),

# Universities
    path('api/v1/universities/', universities.UniversityListView.as_view(), name='university-list'),
    path('api/v1/universities/<int:pk>/', universities.UniversityDetailView.as_view(), name='university-detail'),

    # Faculties
    path('api/v1/faculties/', universities.FacultyListView.as_view(), name='faculty-list'),
    path('api/v1/faculties/<int:pk>/', universities.FacultyDetailView.as_view(), name='faculty-detail'),

    # Regions (etrap)
    path('api/v1/regions/', regions.RegionListView.as_view(), name='region-list'),
    path('api/v1/regions/<int:pk>/', regions.RegionDetailView.as_view(), name='region-detail'),
    path('api/v1/specialties/<int:specialty_id>/region-admissions/', exams.RegionAdmissionListView.as_view(), name='specialty-region-admissions'),
    path('api/v1/specialty-by-region/', exams.SpecialtyByRegionView.as_view(), name='specialty-by-region'),

    # Lecture topics
    path('api/v1/lecture-topics/', lectures.LectureTopicListView.as_view(), name='lecture-topic-list'),
    path('api/v1/lecture-topics/<int:pk>/', lectures.LectureTopicDetailView.as_view(), name='lecture-topic-detail'),
    path('api/v1/lectures/<int:lecture_id>/topics/', lectures.TopicsByLectureView.as_view(), name='lecture-topic-list-by-lecture'),
    path('api/v1/lecture/<int:lecture_id>/topics/', lectures.TopicsByLectureView.as_view(), name='lecture-topic-list-by-lecture-singular'),
    path('api/v1/subjects/<int:subject_id>/lectures/', lectures.LecturesBySubjectView.as_view(), name='subject-lectures'),
    path('api/v1/subjects/<int:subject_id>/lecturesG/', lectures.LecturesGBySubjectView.as_view(), name='subject-lecturesG'),
    path('api/v1/subjects/<int:subject_id>/lecture-topics/', lectures.TopicsWithLecturesBySubjectView.as_view(), name='subject-lecture-topics'),

    # Lectures
    path('api/v1/lectures/', lectures.LectureListView.as_view(), name='lecture-list'),
    path('api/v1/lectures/<int:pk>/', lectures.LectureDetailView.as_view(), name='lecture-detail'),
    path('api/v1/lecturesG/<int:pk>/', lectures.LectureGDetailView.as_view(), name='lectureG-detail'),

    # Specialties / Hunarler
    path('api/v1/specialties/', exams.SpecialtyListView.as_view(), name='specialty-list'),
    path('api/v1/specialties/<int:pk>/', exams.SpecialtyDetailView.as_view(), name='specialty-detail'),

    # Exams
    path('api/v1/exams/', exams.ExamListView.as_view(), name='exam-list'),
    path('api/v1/exams/<int:pk>/', exams.ExamDetailView.as_view(), name='exam-detail'),

    # Subjects
    path('api/v1/subjects/', subjects.SubjectListView.as_view(), name='subject-list'),
    path('api/v1/subjects/<int:pk>/', subjects.SubjectDetailView.as_view(), name='subject-detail'),
    path('api/v1/schools/', schools.SchoolListView.as_view(), name='school-list'),
    path('api/v1/schools/<int:pk>/', schools.SchoolDetailView.as_view(), name='school-detail'),
    path('api/v1/subjects/<int:subject_id>/exam-pdf/', schools.SubjectExamPdfView.as_view(), name='subject-exam-pdf'),
    path('api/v1/schools/<int:school_id>/classes/', schools.SchoolClassListView.as_view(), name='school-classes'),
    path('api/v1/schools/<int:school_id>/subjects/<int:subject_id>/pdf/', schools.SchoolSubjectPdfView.as_view(), name='school-subject-lecture-pdf'),
    path('api/v1/tutors/', tutors.TutorListView.as_view(), name='tutor-list'),
    path('api/v1/videos/', videos.VideoLessonListView.as_view(), name='video-list'),

    # Questions
    path('api/v1/questions/', questions.QuestionListView.as_view(), name='question-list'),
    path('api/v1/subjects/<int:subject_id>/questions/', questions.QuestionBySubjectView.as_view(), name='subject-questions'),
    path('api/v1/submit-answer/', questions.SubmitAnswerView.as_view(), name='submit-answer'),
    path('api/v1/random-test/', questions.RandomTestView.as_view(), name='random-test'),

    # Results
    path('api/v1/results/', results.ResultListView.as_view(), name='result-list'),
    path('api/v1/my-results/', results.MyResultsView.as_view(), name='my-results'),

# Subscription
    path('api/v1/subscription/', subscription.SubscriptionView.as_view(), name='subscription'),

    # Payment (bank tölegi)
    path('api/v1/payment/', payment.PaymentView.as_view(), name='payment'),
    path('api/v1/payment/confirm/', payment.PaymentConfirmView.as_view(), name='payment-confirm'),

    path("rosetta/", include("rosetta.urls")),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Synagchy API",
        default_version='v1',
        description=(
            "Synagchy — talyp platformasy. Universitetler, fakultetler, hünärler, "
            "giriş synaglary, dersler, soraglar, netijeler, reýting, abuna we bank tölegi."
        ),
        contact=openapi.Contact(email="nepes@example.com"),
    ),
    patterns=urlpatterns,
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    # Swagger (API dokumentasiýasy)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


# Media (surat, audio, wideo, pdf) we static görkezmek
# DEBUG=True bolanda Django media/static hizmetini edýär
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
