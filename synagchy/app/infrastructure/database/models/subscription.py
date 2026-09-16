from django.db import models

from app.infrastructure.database.models.user import User


class SubscriptionPlanPrice(models.Model):
    """Abuna bahalary. Admin panelden düzeditmek üçin."""
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='premium',
        unique=True,
        help_text='Abuna görnüşi',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Abuna bahasy (TMT)',
    )
    is_active = models.BooleanField(default=True, help_text='Bu baha işjeň bolsunmy?')
    description = models.TextField(blank=True, default='', help_text='Abuna barada goşmaça maglumat')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_plan_display()} - {self.price} TMT"


class Subscription(models.Model):
    """
    Abuna. Ulanyjy abuna satyn alyp, yenillikler gazanýar.
    """
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"
