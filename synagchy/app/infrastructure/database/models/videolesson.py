from django.db import models


class VideoLesson(models.Model):
    """Wideo sapak (video lesson) modeli."""
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=2048)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
