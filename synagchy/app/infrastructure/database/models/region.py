from django.db import models


class Region(models.Model):
    """
    Etrap (region). Ulanyjy we hünäriň giriş maglumatlary regiona göre bolýar.
    Mysal: Aşgabat, Mary, Lebap, Daşoguz, Türkmenabat we ş.m.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
