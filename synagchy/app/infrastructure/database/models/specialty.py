from django.db import models

from app.infrastructure.database.models.faculty import Faculty


class Specialty(models.Model):
    """
    Fakultetiň hünäri.
    Mysal: Fizika fakulteti - Radiofizika we Elektronika hünäri
    """
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='specialties'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    required_documents = models.TextField(
        blank=True,
        default='',
        verbose_name='Gerekli resminamalar',
    )
    application_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Resminama tabşyrygynyň gutarýan wagty',
    )

    def __str__(self):
        return self.name


class SpecialtyRegionAdmission(models.Model):
    """
    Hünäriň etrap boýunça giriş maglumatlary.
    Her bir hünär + etrap goşundynda öz kabul sany, tapşyryk sany we synag wagty bolýar.
    """
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.CASCADE,
        related_name='region_admissions'
    )
    region = models.ForeignKey(
        'app.Region',
        on_delete=models.CASCADE,
        related_name='specialty_admissions'
    )
    admission_capacity = models.IntegerField(
        default=0,
        verbose_name='Kabul edilmeli talyp sany',
    )
    applications_count = models.IntegerField(
        default=0,
        verbose_name='Tabşyrylanlaryň sany',
    )
    exam_start_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Synagyň başlaýan wagty',
    )

    class Meta:
        unique_together = ('specialty', 'region')
        ordering = ['specialty', 'region']

    def __str__(self):
        return f"{self.specialty.name} - {self.region.name}"
