from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from app.infrastructure.database.models import (
    User, University, Faculty, Specialty, SpecialtyRegionAdmission,
    EntranceExam, Subject, Lecture, LectureTopic, Question, ExamResult,
    Subscription, SubscriptionPlanPrice, Payment, Region,
)
from app.infrastructure.database.models import School, SchoolClass, OnlineTutor, VideoLesson
from app.infrastructure.database.models.lecture import LectureG, SchoolSubjectPDF


class SpecialtyRegionAdmissionInline(admin.TabularInline):
    model = SpecialtyRegionAdmission
    extra = 0
    autocomplete_fields = ['region']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rating', 'specialty', 'region', 'subscription_rank', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'specialty', 'region')
    list_filter = ('subscription_rank', 'is_staff', 'is_superuser', 'region')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Talyp maglumatlary', {
            'fields': ('phone', 'rating', 'specialty', 'region', 'subscription_rank'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Talyp maglumatlary', {
            'fields': ('phone', 'specialty', 'region', 'rating', 'subscription_rank'),
        }),
    )


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'exam_info', 'about', 'image')
    search_fields = ('name', 'city', 'exam_info', 'about')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'university')
    search_fields = ('name',)
    list_filter = ('university',)


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'required_documents', 'application_deadline')
    search_fields = ('name', 'required_documents')
    list_filter = ('faculty',)
    inlines = [SpecialtyRegionAdmissionInline]


@admin.register(SpecialtyRegionAdmission)
class SpecialtyRegionAdmissionAdmin(admin.ModelAdmin):
    list_display = ('specialty', 'region', 'admission_capacity', 'applications_count', 'exam_start_at')
    search_fields = ('specialty__name', 'region__name')
    list_filter = ('specialty', 'region')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 0


@admin.register(EntranceExam)
class EntranceExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'specialty')
    search_fields = ('title',)
    list_filter = ('specialty',)
    #inlines = [SubjectInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('order', 'title', 'text', 'formula', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'difficulty_level')
    extra = 0


class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 0
    fields = ('title', 'content_type', 'content_text', 'image', 'pdf_file', 'audio', 'video', 'order')


class LectureTopicInline(admin.TabularInline):
    model = LectureTopic
    fk_name = 'lecture'
    extra = 0


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_score', 'image', 'exam_pdf', 'questions_pdf', 'answers_pdf')
    search_fields = ('name',)
    filter_horizontal = ('exams',)
    inlines = [QuestionInline, LectureInline]
    fields = ('name', 'max_score', 'image', 'exam_pdf', 'questions_pdf', 'answers_pdf', 'exams')


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'subjects_count')
    search_fields = ('name', 'address')
    filter_horizontal = ('subjects',)

    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = "Dersler sany"


@admin.register(OnlineTutor)
class OnlineTutorAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name',)


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')
    search_fields = ('title',)


@admin.register(LectureTopic)
class LectureTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'lecture', 'order')
    search_fields = ('title',)
    list_filter = ('lecture',)


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'content_type', 'topics_count', 'order')
    search_fields = ('title',)
    list_filter = ('subject', 'content_type')
    inlines = [LectureTopicInline]
    fields = ('subject', 'title', 'content_type', 'content_text', 'image', 'pdf_file', 'audio', 'video', 'order')

@admin.register(LectureG)
class LectureGAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject')
    search_fields = ('title',)
    list_filter = ['subject']
    #inlines = [LectureTopicInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'subject', 'difficulty_level', 'correct_answer', 'formula')
    search_fields = ('title', 'text', 'formula')
    list_filter = ('subject', 'difficulty_level')
    fields = ('subject', 'order', 'title', 'text', ('option_a', 'option_b'), ('option_c', 'option_d'),
              ('difficulty_level', 'correct_answer'), 'formula')
    ordering = ['subject', 'order', 'id']


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'subject', 'score', 'correct_count', 'incorrect_count', 'total_count', 'duration_seconds')
    search_fields = ('user__username', 'exam__title', 'subject__name')
    list_filter = ('exam', 'subject')


@admin.register(SubscriptionPlanPrice)
class SubscriptionPlanPriceAdmin(admin.ModelAdmin):
    list_display = ('plan', 'price', 'is_active', 'updated_at')
    list_filter = ('plan', 'is_active')
    search_fields = ('plan', 'description')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active')
    list_filter = ('plan', 'is_active')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'discount_percent',
                    'final_amount', 'status', 'created_at')
    list_filter = ('status', 'plan')
    search_fields = ('user__username', 'bank_ref')


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'subjects_count')
    search_fields = ('name', 'school__name')
    list_filter = ('school',)
    filter_horizontal = ('subjects',)
    fields = ('school', 'name', 'subjects')

    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = "Dersler sany"


@admin.register(SchoolSubjectPDF)
class SchoolSubjectPDFAdmin(admin.ModelAdmin):
    list_display = ('school', 'school_class', 'subject', 'lecture_pdf', 'questions_pdf', 'answers_pdf', 'updated_at')
    search_fields = ('school__name', 'school_class__name', 'subject__name')
    list_filter = ('school', 'school_class', 'subject')
    fields = ('school', 'school_class', 'subject', 'lecture_pdf', 'questions_pdf', 'answers_pdf')
    actions = ['show_pdf_urls']

    def show_pdf_urls(self, request, queryset):
        for obj in queryset:
            urls = []
            if obj.lecture_pdf:
                urls.append(f"Leksiýa: {obj.lecture_pdf.url}")
            if obj.questions_pdf:
                urls.append(f"Soraglar: {obj.questions_pdf.url}")
            if obj.answers_pdf:
                urls.append(f"Jogaplar: {obj.answers_pdf.url}")
            self.message_user(request, f"{obj.school.name} - {obj.subject.name}: {' | '.join(urls)}")
    show_pdf_urls.short_description = "PDF URL-lerini göster"
