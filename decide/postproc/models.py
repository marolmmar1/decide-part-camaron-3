from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.

class PostProcessing(models.Model):
    class Type(models.TextChoices):
        DEFAULT = "DEF", _("DEFAULT")
        BORDA = "BOR", _("BORDA")
        DHONDT = "DHO", _("DHONDT")
        PARITY = "PAR", _("PARITY")
    voting_id = models.PositiveIntegerField()
    question_id = models.PositiveIntegerField()
    type = models.CharField(max_length=3, choices=Type.choices, default=Type.DEFAULT)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    results = models.JSONField(blank=True, null=True)
    class Meta:
        unique_together = (('voting_id', 'question_id', 'type'),)

    def __str__(self):
        return f"{self.type} - v{self.voting_id} - q{self.question_id} - \n \t results: {self.results}"