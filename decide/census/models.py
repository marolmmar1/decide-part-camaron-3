from django.db import models
<<<<<<< HEAD
from base import mods

ROLES = [
    ('0','Only for Hierchical Votings. Select this if voting isn`t Hierchical'),
    ('1', 'Balanceado'),
    ('2', 'Colaborador'),
    ('3', 'Coordinador'),
    ('4', 'Presidente'),
]

=======
>>>>>>> central/integracion-votaciones


class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
<<<<<<< HEAD
    role = models.CharField(max_length=1, choices=ROLES, default='0',blank=True)
=======
>>>>>>> central/integracion-votaciones

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)
