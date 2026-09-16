from django.contrib.auth.models import AbstractUser
from django.db import models
from app.infrastructure.database.models.specialty import Specialty
from app.infrastructure.database.models.region import Region


class User(AbstractUser):
    """
    Ulanyjy (talyp). Django-nyň AbstractUser-inden miras alýar,
    şonuň üçin login, parol, email ýaly esasy meýdanlar bar.
    """
    first_name = models.CharField(max_length=150, blank=True, verbose_name="At")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Familiýa")
    phone = models.CharField(max_length=30, blank=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Etrap',
    )
    rating = models.IntegerField(default=0)
    subscription_rank = models.IntegerField(default=0)  # 1,2,3 -> yenillik

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
