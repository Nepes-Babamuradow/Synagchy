from django.db import models

from app.infrastructure.database.models.university import University


class Faculty(models.Model):
    """
    Uniwersitetiň fakulteti.
    Mysal: TDU - Fizika fakulteti
    """
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='faculties'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.university.name} - {self.name}"
