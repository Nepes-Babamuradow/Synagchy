from django.db import models

from app.infrastructure.database.models.user import User


class Payment(models.Model):
    """
    Bank tölegi. Ulanyjy premium abuna satyn alanda töleg edýär.
    Top 3 (1,2,3-nji orunda) ulanyjylar yenillik alýarlar.
    """
    STATUS_CHOICES = [
        ('pending', 'Başlangyç'),
        ('paid', 'Töleg edildi'),
        ('failed', 'Başartsyz'),
        ('refunded', 'Yzyna gaýtaryldy'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    plan = models.CharField(
        max_length=20, default='premium',
        help_text='Abuna görnüşi: premium / vip'
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Asyl baha (yenillik öňündäki)'
    )
    discount_percent = models.IntegerField(default=0)
    final_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Yenillik bilen hasaplanan soňky baha'
    )
    bank_ref = models.CharField(
        max_length=255, blank=True,
        help_text='Bank API-syndan gelen töleg referansy'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.final_amount} TMT ({self.status})"
