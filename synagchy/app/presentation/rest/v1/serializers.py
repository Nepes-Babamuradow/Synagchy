from rest_framework import serializers

from app.infrastructure.database.models import (
    User,
    University,
    Faculty,
    Specialty,
    SpecialtyRegionAdmission,
    EntranceExam,
    Subject,
    LectureTopic,
    Lecture,
    Question,
    ExamResult,
    Subscription,
    Payment,
    Region,
)
from app.infrastructure.database.models import School, OnlineTutor, VideoLesson


class UserSerializer(serializers.ModelSerializer):
    specialty_name = serializers.SerializerMethodField()
    faculty_name = serializers.SerializerMethodField()
    university_name = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True, help_text="Doly ady (first_name + last_name)")
    subscription_rank = serializers.CharField(read_only=True, help_text="Ulanyjynyň abuna derejesi (san ýa-da at)")
    subscription_name = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()
    has_subscription = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'specialty', 'specialty_name',
              'faculty_name', 'university_name', 'region', 'region_name',
              'email', 'first_name', 'last_name', 'full_name',
              'phone', 'rating', 'subscription_rank', 'subscription_name',
              'subscription', 'has_subscription']
        read_only_fields = [
            'id', 'specialty_name', 'faculty_name', 'university_name',
            'region_name', 'rating', 'subscription_rank', 'subscription_name',
            'subscription', 'has_subscription', 'full_name',
        ]

    def get_specialty_name(self, obj):
        if getattr(obj, 'specialty', None):
            return obj.specialty.name
        return None

    def get_faculty_name(self, obj):
        specialty = getattr(obj, 'specialty', None)
        if specialty and getattr(specialty, 'faculty', None):
            return specialty.faculty.name
        return None

    def get_university_name(self, obj):
        specialty = getattr(obj, 'specialty', None)
        if specialty:
            faculty = getattr(specialty, 'faculty', None)
            if faculty and getattr(faculty, 'university', None):
                return faculty.university.name
        return None

    def get_region_name(self, obj):
        if getattr(obj, 'region', None):
            return obj.region.name
        return None

    def get_subscription_name(self, obj):
        try:
            sub = obj.subscription
            return sub.plan if sub else None
        except Exception:
            return None

    def get_subscription(self, obj):
        try:
            sub = obj.subscription
            return sub.is_active if sub else False
        except Exception:
            return False

    def get_has_subscription(self, obj):
        try:
            sub = obj.subscription
            return sub.is_active if sub else False
        except Exception:
            return False


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, help_text="Parol")
    first_name = serializers.CharField(max_length=150, help_text="Ulanyjynyň ady (at)")
    last_name = serializers.CharField(max_length=150, help_text="Ulanyjynyň familýasy")

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'password', 'specialty', 'region']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """
    Profil redaktirleme üçin: diňe at, familiýa, telefon, etrap, hünär ütgetmek bolýar.
    """
    region_name = serializers.SerializerMethodField(read_only=True)
    specialty_name = serializers.SerializerMethodField(read_only=True)
    faculty_name = serializers.SerializerMethodField(read_only=True)
    university_name = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone',
                  'region', 'region_name', 'specialty', 'specialty_name',
                  'faculty_name', 'university_name', 'full_name',
                  'rating', 'subscription_rank']
        read_only_fields = ['id', 'username', 'email', 'region_name', 'specialty_name',
                            'faculty_name', 'university_name', 'full_name',
                            'rating', 'subscription_rank']

    def get_region_name(self, obj):
        if getattr(obj, 'region', None):
            return obj.region.name
        return None

    def get_specialty_name(self, obj):
        if getattr(obj, 'specialty', None):
            return obj.specialty.name
        return None

    def get_faculty_name(self, obj):
        specialty = getattr(obj, 'specialty', None)
        if specialty and getattr(specialty, 'faculty', None):
            return specialty.faculty.name
        return None

    def get_university_name(self, obj):
        specialty = getattr(obj, 'specialty', None)
        if specialty:
            faculty = getattr(specialty, 'faculty', None)
            if faculty and getattr(faculty, 'university', None):
                return faculty.university.name
        return None


class LoginSerializer(serializers.Serializer):
    """Girmek (login) üçin body"""
    username = serializers.CharField(max_length=150, help_text="Ulanyjy ady")
    password = serializers.CharField(write_only=True, help_text="Parol")


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, help_text="Häzirki parol")
    new_password = serializers.CharField(write_only=True, help_text="Täze parol")
    confirm_password = serializers.CharField(write_only=True, help_text="Täze paroly gaýtalaň")

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(
                {'confirm_password': 'Täze parollary birme-bir bolmaly.'}
            )
        return attrs


class SubmitAnswerSerializer(serializers.Serializer):
    """Sorag çözmek üçin body"""
    subject_id = serializers.IntegerField(help_text="Dersiň ID-si")
    answers = serializers.DictField(
        child=serializers.CharField(),
        help_text='Sorag ID we jogap: {"1": "A", "2": "B"}',
    )
    duration_seconds = serializers.IntegerField(
        required=False,
        min_value=0,
        help_text="Testi tamamlamak üçin geçen wagt (sekunt). Frontend tarapyndan iberilýär.",
    )


class SubscriptionPlanSerializer(serializers.Serializer):
    """Abuna satyn almak üçin body"""
    plan = serializers.ChoiceField(
        choices=[('free', 'Free'), ('premium', 'Premium'), ('vip', 'VIP')],
        default='free',
        help_text="Abuna görnüşi",
    )


class PaymentRequestSerializer(serializers.Serializer):
    """Töleg başlatmak üçin body"""
    plan = serializers.ChoiceField(
        choices=[('premium', 'Premium'), ('vip', 'VIP')],
        default='premium',
        help_text="Abuna görnüşi",
    )


class PaymentConfirmSerializer(serializers.Serializer):
    """Töleg tassyknamasy (webhook) üçin body"""
    bank_ref = serializers.CharField(max_length=255, help_text="Bank referans belgisi")
    success = serializers.BooleanField(default=True, help_text="Töleg üstünlikli boldumy?")


class RegionSerializer(serializers.ModelSerializer):
    """Etrap (region) serializer."""
    class Meta:
        model = Region
        fields = ['id', 'name', 'description']


class SpecialtyRegionAdmissionSerializer(serializers.ModelSerializer):
    """Hünäriň etrap boýunça giriş maglumatlary (per-region)."""
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = SpecialtyRegionAdmission
        fields = ['id', 'specialty', 'region', 'region_name',
                  'admission_capacity', 'applications_count', 'exam_start_at']
        read_only_fields = ['specialty']


class UniversitySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    exam_info = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    about = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = University
        fields = ['id', 'name', 'city', 'description', 'exam_info', 'about', 'image']


class FacultySerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = Faculty
        fields = ['id', 'university', 'university_name', 'name', 'description']


class SubjectNestedCreateSerializer(serializers.ModelSerializer):
    """Synag döredilende dersleri bir hatda goşmak üçin."""
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    max_score = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Subject
        fields = ['name', 'max_score']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs


class ExamNestedCreateSerializer(serializers.ModelSerializer):
    """Hünär döredilende synag + dersleri bir hatda goşmak üçin."""
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    subjects = SubjectNestedCreateSerializer(many=True, required=False)

    class Meta:
        model = EntranceExam
        fields = ['title', 'description', 'subjects']

    def create(self, validated_data):
        subjects_data = validated_data.pop('subjects', [])
        title = (validated_data.get('title') or '').strip()
        specialty = validated_data.get('specialty')
        if not title:
            if specialty is not None:
                title = f"{specialty.name} giriş synagy"
            else:
                title = "Giriş synagy"
        validated_data['title'] = title
        exam = EntranceExam.objects.create(**validated_data)
        for s in subjects_data:
            name = (s.get('name') or '').strip()
            if not name:
                continue
            subject = Subject.objects.create(**s)
            subject.exams.add(exam)
        return exam


class SpecialtySerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    university_name = serializers.CharField(
        source='faculty.university.name', read_only=True)
    exams = ExamNestedCreateSerializer(many=True, required=False, write_only=True)
    region_admissions = SpecialtyRegionAdmissionSerializer(many=True, required=False, write_only=True)
    required_documents = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    application_deadline = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Specialty
        fields = ['id', 'faculty', 'faculty_name', 'university_name',
                  'name', 'description', 'required_documents',
                  'application_deadline', 'exams', 'region_admissions']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        exams_data = attrs.get('exams', [])
        non_empty = 0
        for e in exams_data:
            for s in e.get('subjects', []):
                name = (s.get('name') or '').strip()
                if name:
                    non_empty += 1
        if non_empty > 5:
            raise serializers.ValidationError(
                "Hünärde iň köp 5 sany ders birikdirip bolýar.")
        if non_empty < 2:
            raise serializers.ValidationError(
                "Hünäri döretmek üçin iň azyndan 2 sany ders (name) doldurmaly.")
        return attrs

    def create(self, validated_data):
        exams_data = validated_data.pop('exams', [])
        region_admissions_data = validated_data.pop('region_admissions', [])
        specialty = Specialty.objects.create(**validated_data)
        for e in exams_data:
            e['specialty'] = specialty
            ExamNestedCreateSerializer().create(e)
        for ra_data in region_admissions_data:
            SpecialtyRegionAdmission.objects.create(specialty=specialty, **ra_data)
        return specialty

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user_region = None
        if request and request.user.is_authenticated:
            user_region = getattr(request.user, 'region', None)
        if user_region:
            admissions = instance.region_admissions.filter(region=user_region).order_by('region')
            data['region_admissions'] = SpecialtyRegionAdmissionSerializer(admissions, many=True).data
        return data


class EntranceExamSerializer(serializers.ModelSerializer):
    specialty_name = serializers.CharField(source='specialty.name', read_only=True)
    faculty_name = serializers.CharField(
        source='specialty.faculty.name', read_only=True)
    university_name = serializers.CharField(
        source='specialty.faculty.university.name', read_only=True)

    class Meta:
        model = EntranceExam
        fields = ['id', 'specialty', 'specialty_name', 'faculty_name',
                  'university_name', 'title', 'pdf_file','description']


class SubjectSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(help_text="image file URL-si (doly URL)")
    exam_pdf_url = serializers.SerializerMethodField(help_text="Synag PDF faýlyň URL-si")
    questions_pdf_url = serializers.SerializerMethodField(help_text="Soraglar PDF faýlyň URL-si (klasa we ders boýunça)")
    answers_pdf_url = serializers.SerializerMethodField(help_text="Jogaplar PDF faýlyň URL-si (klasa we ders boýunça)")
    exams = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'exams', 'name', 'max_score', 'image', 'image_url',
                  'exam_pdf', 'exam_pdf_url', 'questions_pdf', 'questions_pdf_url',
                  'answers_pdf', 'answers_pdf_url']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_exam_pdf_url(self, obj):
        if obj.exam_pdf:
            return obj.exam_pdf.url
        return None

    def get_questions_pdf_url(self, obj):
        if obj.questions_pdf:
            return obj.questions_pdf.url
        return None

    def get_answers_pdf_url(self, obj):
        if obj.answers_pdf:
            return obj.answers_pdf.url
        return None


class SchoolSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = None  # set at import time to avoid circular import
        fields = ['id', 'name', 'address', 'subjects']


class OnlineTutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ['id', 'name', 'url', 'description']


class VideoLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ['id', 'title', 'url', 'description']


# Bind the models to serializers now that classes are defined
SchoolSerializer.Meta.model = School
OnlineTutorSerializer.Meta.model = OnlineTutor
VideoLessonSerializer.Meta.model = VideoLesson


class LectureTopicSerializer(serializers.ModelSerializer):
    lecture_title = serializers.CharField(source='lecture.title', read_only=True)
    lecture_subject_id = serializers.IntegerField(source='lecture.subject_id', read_only=True)

    class Meta:
        model = LectureTopic
        fields = [
            'id', 'lecture', 'lecture_title', 'lecture_subject_id',
            'title', 'description', 'order',
        ]


class LectureSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topics_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lecture
        fields = [
            'id', 'subject', 'subject_name',
            'title', 'content_type', 'content_text',
            'image', 'pdf_file', 'audio', 'video',
            'order', 'created_at', 'topics_count',
        ]
        read_only_fields = ['created_at', 'topics_count']

class LectureGSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topics_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lecture
        fields = [
            'id', 'subject', 'subject_name',
            'title', 'image', 'pdf_file', 'audio', 'video',
            'topics_count'
        ]
        read_only_fields = ['created_at','topics_count']



class LectureDetailSerializer(LectureSerializer):
    topics = LectureTopicSerializer(many=True, read_only=True)

    class Meta(LectureSerializer.Meta):
        fields = [
            'id', 'subject', 'subject_name', 'title', 'content_type',
            'content_text', 'image', 'pdf_file', 'audio', 'video',
            'order', 'created_at', 'topics_count', 'topics',
        ]


class LectureTopicDetailSerializer(LectureTopicSerializer):
    lecture = LectureSerializer(read_only=True)

    class Meta(LectureTopicSerializer.Meta):
        fields = LectureTopicSerializer.Meta.fields + ['lecture']


class QuestionSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        read_only=True,
        help_text="Soragyň kysa ady (mesele: Nyutonyň 1-nji kanuny). Awomatik tapylýar."
    )
    order = serializers.IntegerField(
        read_only=True,
        help_text="Soragyň dersdäki taribi (1, 2, 3...). Awomatik hasaplanýar."
    )
    difficulty_level = serializers.ChoiceField(
        choices=Question.DIFFICULTY_CHOICES,
        default='medium',
        help_text="Soragyň kynlyk derejesi: easy (Kolay), medium (Orta), hard (Kyn)",
    )
    formula = serializers.CharField(
        required=False, allow_blank=True, allow_null=True,
        help_text="Soragda kimyawy formula (mesele H2SO4). Awomatik tapylýar."
    )

    class Meta:
        model = Question
        fields = ['id', 'subject', 'order', 'title', 'text', 'option_a', 'option_b',
                  'option_c', 'option_d', 'difficulty_level', 'formula']


class ExamResultSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField()
    exam_title = serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = ['id', 'user', 'exam', 'exam_title', 'subject', 'subject_name',
                  'score', 'correct_count', 'incorrect_count', 'total_count',
                  'duration_seconds', 'created_at']

    def get_subject_name(self, obj):
        if obj.subject:
            return obj.subject.name
        return None

    def get_exam_title(self, obj):
        if obj.exam:
            return obj.exam.title
        return None


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'is_active', 'started_at', 'expires_at']


class PaymentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_username', 'plan', 'amount',
                  'discount_percent', 'final_amount', 'bank_ref', 'status',
                  'created_at']
        read_only_fields = ['user', 'amount', 'discount_percent',
                            'final_amount', 'bank_ref', 'status', 'created_at']


# ============================================================
#  RESPONSE (Swagger üçin) SERIALIZER'LER
# ============================================================

class AuthResponseSerializer(serializers.Serializer):
    """Registrasiýa / Login response-y."""
    user = UserSerializer()
    refresh = serializers.CharField(help_text="Refresh token")
    access = serializers.CharField(help_text="Access token")


class QuestionAnswerDetailSerializer(serializers.Serializer):
    """Her bir sorag üçin netije (swaggerde düşnükli görkezmek)."""
    question_id = serializers.IntegerField(help_text="Soragyň ID-si")
    order = serializers.IntegerField(help_text="Soragyň taribi (1, 2, 3...)", required=False, allow_null=True)
    title = serializers.CharField(help_text="Soragyň kysa ady", required=False, allow_null=True)
    text = serializers.CharField(help_text="Soragyň mazmuny")
    difficulty_level = serializers.CharField(help_text="Soragyň kynlyk derejesi (easy/medium/hard)")
    user_answer = serializers.CharField(
        help_text="Ulanyjynyň beren jogaby (A, B, C we D)")
    correct_answer = serializers.CharField(help_text="Dogry jogap (A, B, C, D)")
    is_correct = serializers.BooleanField(help_text="Dogry jogap berildimi?")


class SubmitAnswerResponseSerializer(serializers.Serializer):
    """Sorag çözmek netijesi."""
    correct_count = serializers.IntegerField(help_text="Dogry jogap sany")
    incorrect_count = serializers.IntegerField(help_text="Ýalňyş jogap sany")
    total_count = serializers.IntegerField(help_text="Umumy sorag sany")
    score = serializers.IntegerField(help_text="Netije (%)")
    duration_seconds = serializers.IntegerField(help_text="Testi tamamlamak üçin geçen wagt (sekunt)")
    rating = serializers.IntegerField(help_text="Ulanyjynyň täzelenen reýtingi")
    details = QuestionAnswerDetailSerializer(
        many=True, help_text="Her soragyň netijesi (dogry/ýalňyş)")


class RatingSerializer(serializers.Serializer):
    """Reýting tablisasy (rank we discount bilen)."""
    id = serializers.IntegerField()
    username = serializers.CharField()
    specialty = serializers.IntegerField(source='specialty.id', required=False, allow_null=True, read_only=True)
    specialty_name = serializers.CharField(source='specialty.name', required=False, allow_null=True, read_only=True)
    faculty_name = serializers.CharField(source='specialty.faculty.name', required=False, allow_null=True, read_only=True)
    university_name = serializers.CharField(source='specialty.faculty.university.name', required=False, allow_null=True, read_only=True)
    region = serializers.IntegerField(source='region.id', required=False, allow_null=True, read_only=True)
    region_name = serializers.CharField(source='region.name', required=False, allow_null=True, read_only=True)
    first_name = serializers.CharField(required=False, allow_null=True)
    last_name = serializers.CharField(required=False, allow_null=True)
    full_name = serializers.CharField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)
    rating = serializers.IntegerField(required=False, allow_null=True)
    total_duration_seconds = serializers.IntegerField(required=False, allow_null=True)
    subscription_rank = serializers.IntegerField(required=False, allow_null=True)
    rank = serializers.IntegerField(help_text="Orun (1,2,3,...)")
    discount = serializers.CharField(required=False, allow_null=True,
                                     help_text="Yenillik (50%, 30%, 20%)")


class SpecialtyInfoSerializer(serializers.Serializer):
    """Hünär jikme-jigi."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)


class FacultyInfoSerializer(serializers.Serializer):
    """Fakultet jikme-jigi."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)


class UniversityInfoSerializer(serializers.Serializer):
    """Universitet jikme-jigi."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    city = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    exam_info = serializers.CharField(required=False, allow_null=True)
    about = serializers.CharField(required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)


class MyUniversitySerializer(serializers.Serializer):
    """/my-university/ response-y."""
    user = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    specialty = SpecialtyInfoSerializer()
    faculty = FacultyInfoSerializer()
    university = UniversityInfoSerializer()
    region = RegionSerializer(required=False, allow_null=True)


class MessageSerializer(serializers.Serializer):
    """Diňe message gaýtarýan response-lar üçin."""
    message = serializers.CharField()


class SubscriptionResponseSerializer(serializers.ModelSerializer):
    """Abuna + discount görkezýän response."""
    discount_percent = serializers.IntegerField(read_only=True, help_text="Yenillik (%)")

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'is_active', 'started_at',
                  'expires_at', 'discount_percent']


# Detail view'ler üçin (goşmaça içki listeler bilen)

class RegionAdmissionSerializer(serializers.ModelSerializer):
    """Etrap boýunça hünär giriş maglumatlary (read-only, detallarda)."""
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = SpecialtyRegionAdmission
        fields = ['id', 'region', 'region_name', 'admission_capacity',
                  'applications_count', 'exam_start_at']


class UniversityDetailSerializer(serializers.ModelSerializer):
    faculties = FacultySerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    exam_info = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    about = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = University
        fields = ['id', 'name', 'city', 'description', 'exam_info', 'about', 'image', 'faculties']


class FacultyDetailSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)
    specialties = SpecialtySerializer(many=True, read_only=True)

    class Meta:
        model = Faculty
        fields = ['id', 'university', 'university_name', 'name',
                  'description', 'specialties']


class ExamDetailSerializer(serializers.ModelSerializer):
    specialty_name = serializers.CharField(source='specialty.name', read_only=True)
    faculty_name = serializers.CharField(
        source='specialty.faculty.name', read_only=True)
    university_name = serializers.CharField(
        source='specialty.faculty.university.name', read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = EntranceExam
        fields = ['id', 'specialty', 'specialty_name', 'faculty_name',
                  'university_name', 'title', 'description', 'subjects']


class SpecialtyDetailSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    university_name = serializers.CharField(
        source='faculty.university.name', read_only=True)
    exams = ExamDetailSerializer(many=True, read_only=True)
    region_admissions = RegionAdmissionSerializer(many=True, read_only=True)
    required_documents = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    application_deadline = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Specialty
        fields = ['id', 'faculty', 'faculty_name', 'university_name',
                  'name', 'description', 'required_documents',
                  'application_deadline', 'exams', 'region_admissions']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user_region = None
        if request and request.user.is_authenticated:
            user_region = getattr(request.user, 'region', None)
        if user_region:
            admissions = instance.region_admissions.filter(region=user_region).order_by('region')
            data['region_admissions'] = RegionAdmissionSerializer(admissions, many=True).data
        return data
