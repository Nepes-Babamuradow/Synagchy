from django.db import models


class University(models.Model):
    """
    Uniwersitet. Her uniwersitetiň giriş synaglary bolup biler.
    """
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    exam_info = models.TextField(
        blank=True,
        default='',
        verbose_name='Synaglar hakda maglumat',
       )
    about = models.TextField(
        blank=True,
        default='',
        verbose_name='Universitet barada umumy maglumat',
    )
    image = models.ImageField(upload_to='universities/images/', null=True, blank=True)

    class Meta:
            ordering = ['id']
    
    def __str__(self):
        return self.name

