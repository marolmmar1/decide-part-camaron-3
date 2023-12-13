from django.db import models

ROLES = [
    ('0', 'Only for Hierchical Votings. Select this if voting isn`t Hierchical'),
    ('1', 'Balanceado'),
    ('2', 'Colaborador'),
    ('3', 'Coordinador'),
    ('4', 'Presidente'),
]


class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
    role = models.CharField(max_length=1, choices=ROLES, default='0')

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)
