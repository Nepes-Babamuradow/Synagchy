from django.db import models

from app.infrastructure.database.models.subject import Subject


class School(models.Model):
    """Mekdep (school) modeli — bir mekdepde köp dersler bolup biler."""
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=512, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, related_name='schools', blank=True)

    def __str__(self):
        return self.name


class SchoolClass(models.Model):
    """
    Mekdepdäki klas (9-A, 10-B, 11-C).
    Bir mekdepde birnäçe klas bolup biler.
    Her klas üçin subjectler we PDF faýllary bar.
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name='Mekdep',
    )
    name = models.CharField(
        max_length=50,
        verbose_name="Klas ady",
        help_text="Mesele: 9-A, 10-B, 11-C",
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name='classes',
        blank=True,
        verbose_name="Dersler",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Klas"
        verbose_name_plural = "Klaslar"
        unique_together = ('school', 'name')
        ordering = ['school', 'name']

    @property
    def subjects_count(self):
        """Klasa bagly dersler sany."""
        return self.subjects.count()

    def __str__(self):
        return f"{self.school.name} - {self.name}"