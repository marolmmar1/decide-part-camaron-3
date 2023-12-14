from django.db import models

from voting.models import Voting, Question
from django.utils.translation import gettext_lazy as _
import copy
import math
from django.utils import timezone


class PostProcessing(models.Model):
    class Type(models.TextChoices):
        NONE = "NON", _("NONE")
        # BORDA = "BOR", _("BORDA")
        DHONDT = "DHO", _("DHONDT")
        SAINT = "PAR", _("SAINT")
        DROOP = "DRO", _("DROOP")

    voting = models.ForeignKey(Voting, null=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=Type.choices, default=Type.NONE)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    results = models.JSONField(blank=True, null=True)

    class Meta:
        unique_together = (("voting_id", "question_id", "type"),)

    def __str__(self):
        return f"{self.type} - v{self.voting_id} - q{self.question_id} - \n \t results: {self.results}"

    def dhondt(self, opts, total_seats):
        for option in opts:
            votes = option["votes"]
            dhont_values = []
            for seat in range(1, total_seats + 1):
                dhont = round(votes / seat, 4)
                dhont_values.append({"seat": seat, "percentaje": dhont})
            option["dhont"] = dhont_values
        self.results = opts
        self.save()

    def saint(self, opts, total_seats):
        opts_aux = copy.deepcopy(opts)

        for option in opts:
            option["saintLague"] = 0

        for i in range(1, total_seats + 1):
            quotients = {
                option["option"]: option["votes"] / (2 * i - 1) for option in opts_aux
            }
            best_option = max(quotients, key=quotients.get)
            for option in opts_aux:
                if option["option"] == best_option:
                    option["votes"] /= 2 * i + 1
                    break
            for option in opts:
                if option["option"] == best_option:
                    option["saintLague"] += 1
                    break
        self.results = opts
        self.save()

    def borda(self, opts):
        n = len(opts)
        for option in opts:
            votes = option["votes"]
            borda = 0
            for i in range(n):
                borda += (n - i) * votes
            option["borda"] = borda
        self.results = opts
        self.save()

    def droop(self, opts, total_seats):
        n = total_seats
        m = sum([option["votes"] for option in opts])
        q = 1 + (m / (n + 1))
        droop = {}
        seats_oc = 0
        for option in opts:
            droop_option = {}
            ei = math.floor(option["votes"] / q)
            seats_oc += ei
            ri = option["votes"] - q * ei
            droop_option["ei"] = ei
            droop_option["ri"] = ri
            droop[option["option"]] = droop_option
            option["droop"] = ei
        residual = n - seats_oc
        best_ri = sorted(droop.items(), key=lambda x: x[1]["ri"], reverse=True)[
            :residual
        ]
        best_options = [option[0] for option in best_ri]
        for option in opts:
            if option["option"] in best_options:
                option["droop"] += 1
        if self != None:
            self.results = opts
            self.save()
        return opts

    def do(self, opts, total_seats):
        self.start_date = timezone.now()
        if self.type == self.Type.DHONDT:
            self.dhondt(opts, total_seats)
        elif self.type == self.Type.SAINT:
            self.saint(opts, total_seats)
        elif self.type == self.Type.DROOP:
            self.droop(opts, total_seats)
        else:
            self.results = None
        self.end_date = timezone.now()
        self.save()
