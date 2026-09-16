from django.db import models

from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.exam import EntranceExam
from app.infrastructure.database.models.subject import Subject


class ExamResult(models.Model):
    """
    Sorag çözüş netijesi. Ulanyjy synag çözende şu ýerde saklanýar.
    Ders birnäçe synaga degişli bolsa, synagsyz hem netije saklanýar.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='results'
    )
    exam = models.ForeignKey(
        EntranceExam,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='results'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results',
    )
    score = models.IntegerField(default=0, verbose_name="Ball (%)")
    correct_count = models.IntegerField(default=0, verbose_name="Dogry jogap sany")
    incorrect_count = models.IntegerField(default=0, verbose_name="Ýalňyş jogap sany")
    total_count = models.IntegerField(default=0, verbose_name="Jemi sorag sany")
    duration_seconds = models.IntegerField(default=0, verbose_name="Testiň dowamlylygy (sekunt)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        exam_title = self.exam.title if self.exam else 'umumy'
        subject_name = self.subject.name if self.subject else ''
        if subject_name:
            return f"{self.user.username} - {subject_name} - {self.score}"
        return f"{self.user.username} - {exam_title} - {self.score}"
