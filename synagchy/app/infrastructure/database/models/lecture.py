from django.db import models

from app.infrastructure.database.models.subject import Subject
from app.infrastructure.database.models.school import School, SchoolClass
from ckeditor.fields import RichTextField


class LectureTopic(models.Model):
    """
    Leksiýanyň içindäki tema. Mysal: Fizika dersinde "Nyutonyň kanunlary".
    Her leksiýanyň içinde birnäçe tema bolýar.
    """
    lecture = models.ForeignKey(
        'Lecture',
        on_delete=models.CASCADE,
        related_name='topics'
    )
    title = models.CharField(max_length=255)
    description = RichTextField(verbose_name="tema_description")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.lecture.title} - {self.title}"


class Lecture(models.Model):
    """
    Leksiýa contenti. Köp formatda bolup bilýär:
    tekst, formula, surat (image), saz (audio), wideo we PDF.
    """
    CONTENT_CHOICES = [
        ('text', 'Tekst'),
        ('formula', 'Formula'),
        ('image', 'Surat'),
        ('audio', 'Saz'),
        ('video', 'Wideo'),
        ('pdf', 'PDF'),
    ]
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='lectures'
    )
    title = models.CharField(max_length=255)
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_CHOICES,
        default='text'
    )

    # Tekst / formula
    content_text = models.CharField(max_length=255,null=True,blank=True)

    # Surat / PDF
    image = models.ImageField(upload_to='lectures/images/', null=True, blank=True)
    pdf_file = models.FileField(upload_to='lectures/pdf/', null=True, blank=True)

    # Saz / wideo
    audio = models.FileField(upload_to='lectures/audio/', null=True, blank=True)
    video = models.FileField(upload_to='lectures/video/', null=True, blank=True)

    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    @property
    def topics_count(self):
        return self.topics.count()            

    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"


class LectureG(models.Model):
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='lecturesG'
    )
    title = models.CharField(max_length=255)
    

    # Tekst / formula
    
    image = models.ImageField(upload_to='lectures/images/', null=True, blank=True)
    pdf_file = models.FileField(upload_to='lectures/pdf/', null=True, blank=True)

    # Saz / wideo
    audio = models.FileField(upload_to='lectures/audio/', null=True, blank=True)
    video = models.FileField(upload_to='lectures/video/', null=True, blank=True)

    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']


    def __str__(self):
        return f"{self.title})"


class SchoolSubjectPDF(models.Model):
    """
    Mekdep we ders bagly leksiýa PDF faýllary.
    Bir mekdepde bir ders üçin leksiýa PDF faýly admin panelden goşulýar.
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='lecture_pdfs',
        verbose_name='Mekdep',
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lecture_pdfs',
        verbose_name='Klas',
        help_text="Bu faýl kamyň klasyna bagly (ýoksa mekdepýň umumy faýly)",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='lecture_pdfs',
        verbose_name='Ders',
    )
    lecture_pdf = models.FileField(
        upload_to='school_subject_lectures/pdf/',
        null=True,
        blank=True,
        verbose_name="Leksiýa PDF",
        help_text="Mekdep we ders boýunça leksiýa PDF faýly",
    )
    questions_pdf = models.FileField(
        upload_to='school_subject_lectures/questions/',
        null=True,
        blank=True,
        verbose_name="Soraglar PDF",
        help_text="Mekdep we ders boýunça soraglar PDF faýly",
    )
    answers_pdf = models.FileField(
        upload_to='school_subject_lectures/answers/',
        null=True,
        blank=True,
        verbose_name="Jogaplar PDF",
        help_text="Mekdep we ders boýunça jogaplar PDF faýly",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mekdep-Ders PDF"
        verbose_name_plural = "Mekdep-Ders PDF faýllary"
        unique_together = ('school', 'school_class', 'subject')
        ordering = ['school', 'school_class', 'subject']

    def __str__(self):
        cls_str = f" - {self.school_class.name}" if self.school_class else ""
        return f"{self.school.name}{cls_str} - {self.subject.name}"
