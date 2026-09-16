from django.db import models
from ckeditor.fields import RichTextField

from app.infrastructure.database.models.exam import EntranceExam


class Subject(models.Model):
    """
    Synaga degişli ders. Bir ders birnäçe synaga / hünäre degişli bolup bilýär.
    """
    name = models.CharField(max_length=255)
    max_score = models.IntegerField(default=100)
    image = models.ImageField(upload_to='subjects/images/', null=True, blank=True)
    exam_pdf = models.FileField(upload_to='subjects/exams/', null=True, blank=True)
    questions_pdf = models.FileField(
        upload_to='subjects/questions/',
        null=True,
        blank=True,
        verbose_name="Soraglar PDF",
        help_text="Soraglaryň PDF faýly (klasa we ders boýunça)"
    )
    answers_pdf = models.FileField(
        upload_to='subjects/answers/',
        null=True,
        blank=True,
        verbose_name="Jogaplar PDF",
        help_text="Dogry jogaplaryň PDF faýly (klasa we ders boýunça)"
    )
    exams = models.ManyToManyField(
        EntranceExam,
        related_name='subjects',
        blank=True,
        help_text='Bu dersiň degişli bolan synaglar',
    )

    class Meta:
            ordering = ['id']
    
    def __str__(self):
        return self.name
