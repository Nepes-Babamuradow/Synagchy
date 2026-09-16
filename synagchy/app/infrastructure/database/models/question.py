from django.db import models
from ckeditor.fields import RichTextField
from django.utils.html import strip_tags
import re

from app.infrastructure.database.models.subject import Subject


class Question(models.Model):
    """
    Sorag. Her soragyň 4 warianty we dogry jogapy bar.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'ýönekeý'),
        ('medium', 'Orta'),
        ('hard', 'Kyn'),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Sorag sanawy (order)",
        help_text="Soragyň dersdäki taribi (1, 2, 3...)."
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Soragyň ady",
        blank=True,
        null=True,
        help_text="Soragyň kysa ady (mesele: Nyutonyň 1-nji kanuny). Awomatik tapylýar."
    )
    text = RichTextField(verbose_name="Sorag")

    # Kimyawy formula (mesele H2SO4, HCl, NaOH, C6H12O6)
    formula = models.CharField(
        max_length=50,
        verbose_name="Kimyawy formula",
        blank=True,
        null=True,
        help_text="Soragda kimyawy formula bar (mesele H2SO4). Awomatik tapylýar."
    )

    # Jogaplary hem RichTextField edýäris:
    option_a = RichTextField(verbose_name="A varianty")
    option_b = RichTextField(verbose_name="B varianty")
    option_c = RichTextField(verbose_name="C varianty")
    option_d = RichTextField(verbose_name="D varianty")
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        verbose_name="Dogry jogap"
    )
    difficulty_level = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        verbose_name="Kynlyk derejesi",
    )

    class Meta:
        ordering = ['subject', 'order', 'id']

    def _extract_title(self, text):
        """Text-den soragyň kysa ady tapyp gaýtar."""
        if not text:
            return None
        plain = strip_tags(text)
        sentences = plain.split('.')
        if sentences:
            title = sentences[0].strip()
            if len(title) > 60:
                title = title[:60] + '...'
            return title
        return plain[:60]

    def _extract_formula(self, text):
        """Text-den kimyawy formula tapyp gaýtar."""
        if not text:
            return None
        plain = strip_tags(text)
        pattern = r'\b(?:[A-Z][a-z]?\d*){2,}\b'
        matches = re.findall(pattern, plain)
        return matches[0] if matches else None

    def save(self, *args, **kwargs):
        # Auto-assign order if not set
        if not self.order and self.order != 0:
            last = Question.objects.filter(subject=self.subject).order_by('-order').first()
            self.order = (last.order + 1) if last else 1
        # Auto-extract title from text if title field is empty
        if not self.title and self.text:
            self.title = self._extract_title(self.text)
        # Auto-extract formula from text if formula field is empty
        if not self.formula and self.text:
            extracted = self._extract_formula(self.text)
            if extracted:
                self.formula = extracted
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text[:50]
