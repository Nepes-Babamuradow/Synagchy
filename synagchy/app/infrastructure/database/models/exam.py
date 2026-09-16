from django.db import models
from django.core.exceptions import ValidationError

from app.infrastructure.database.models.specialty import Specialty

MAX_EXAMS_PER_SPECIALTY = 5


class EntranceExam(models.Model):
    """
    Hünäriň giriş synagy.
    Mysal: Radiofizika hünäri - Fizika, Matematika, Tarih synaglary
    """
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='lectures/pdf/', null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.pk is None and self.specialty_id:
            count = EntranceExam.objects.filter(
                specialty_id=self.specialty_id).count()
            if count >= MAX_EXAMS_PER_SPECIALTY:
                raise ValidationError(
                    f"Bu hünärde iň köp {MAX_EXAMS_PER_SPECIALTY} sany synag bolup biler.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class timeExam(models.Model):
    """
    Synagyň resminama we girizilen senesi.
    """
    exam = models.ForeignKey(
        EntranceExam,
        on_delete=models.CASCADE,
        related_name='time_exams'
    )
    time_doc = models.DateTimeField(verbose_name="Resminamanyň senesi")
    time_entry = models.DateTimeField(verbose_name="Girizilen senesi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam.title} - {self.time_doc}"
