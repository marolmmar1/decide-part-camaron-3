from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


from base import mods
from base.models import Auth, Key


class Question(models.Model):
    desc = models.TextField()
    optionSiNo = models.BooleanField(default=False, help_text="Marca esta casilla solo si el tipo de votación es 'Single Choice'. No podrás añadir más opciones si esta casilla está marcada.")

    def __str__(self):
        return self.desc    
    

    def clean(self):
        if self.optionSiNo and self.pk is not None:  # Si la instancia ya existe y la opción es Sí/No
            for voting in self.voting.all():
                if voting.voting_type != 'S':
                    raise ValidationError('La opción Sí/No solo puede usarse con el tipo de votación Single Choice')
        super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guarda la instancia en la base de datos
        if self.optionSiNo:
            if self.options.count() > 2:
                raise ValidationError('No puedes tener más de dos opciones si la opción Sí/No está marcada')





@receiver(post_save, sender=Question)
def post_SiNo_Option(sender, instance, **kwargs):
    if instance.optionSiNo:
        options = instance.options.all()
        if options.count() == 0:
            op1 = QuestionOption(question=instance, number=1, option="Sí")
            op1.save()
            op2 = QuestionOption(question=instance, number=2, option="No")
            op2.save()

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)
    
    def clean(self):
        if self.question.optionSiNo and self.question.options.all().count() != 2:
            raise ValidationError('Las Preguntas Sí/No no deben tener opciones extras. Borre todas las opciones añadidas para poder crear la pregunta')


VOTING_TYPES = [
    ('S', 'Single Choice'),
    ('M', 'Multiple Choice'),
    ('H', 'Hierarchy'),
    ('Q', 'Many Questions'),
]
class Voting(models.Model):
    voting_type = models.CharField(max_length=1, choices=VOTING_TYPES)
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)

    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE)


    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        votes_format = []
        vote_list = []
        for vote in votes:
            for info in vote:
                if info == 'a':
                    votes_format.append(vote[info])
                if info == 'b':
                    votes_format.append(vote[info])
            vote_list.append(votes_format)
            votes_format = []
        return vote_list

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()

    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()

        opts = []
        for opt in options:
            if isinstance(tally, list):
                votes = tally.count(opt.number)
            else:
                votes = 0
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'votes': votes
            })

        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name
