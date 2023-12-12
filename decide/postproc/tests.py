from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from base.tests import BaseTestCase
import itertools
import random
import json
from django.core.serializers import serialize
from django.db.models import JSONField

from base import mods
from django.contrib.auth.models import User
from voting.models import Question, QuestionOption, Voting
from .models import PostProcessing
from census.models import Census
from mixnet.mixcrypt import ElGamal, MixCrypt
from mixnet.models import Auth
from django.conf import settings


class PostProcTestCase(BaseTestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        super().setUp()

    def tearDown(self):
        self.client = None
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self, postproc, type):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(
                question=q, option='option {}'.format(i+1), number=i+2)
            opt.save()
        v = Voting(name='test voting', question=q,
                   postproc_type=postproc, voting_type=type)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={
                                          'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': {'a': a, 'b': b},
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting('DHO', 'S')
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        postproc = PostProcessing.objects.get(voting=v)
        postproc.do(v.postproc, v.seats)
        print(postproc.results)

        correct_result = {'dhont': [{'seat': 1, 'percentaje': 1.0}, {'seat': 2, 'percentaje': 0.5}, {'seat': 3, 'percentaje': 0.3333}, {'seat': 4, 'percentaje': 0.25}, {'seat': 5, 'percentaje': 0.2}, {'seat': 6, 'percentaje': 0.1667}, {'seat': 7, 'percentaje': 0.1429}, {'seat': 8, 'percentaje': 0.125}, {'seat': 9, 'percentaje': 0.1111}, {'seat': 10, 'percentaje': 0.1}]}, {'option': 'option 2', 'number': 3, 'votes': 3, 'dhont': [{'seat': 1, 'percentaje': 3.0}, {'seat': 2, 'percentaje': 1.5}, {'seat': 3, 'percentaje': 1.0}, {'seat': 4, 'percentaje': 0.75}, {'seat': 5, 'percentaje': 0.6}, {'seat': 6, 'percentaje': 0.5}, {'seat': 7, 'percentaje': 0.4286}, {'seat': 8, 'percentaje': 0.375}, {'seat': 9, 'percentaje': 0.3333}, {'seat': 10, 'percentaje': 0.3}]}, {'option': 'option 3', 'number': 4, 'votes': 2, 'dhont': [{'seat': 1, 'percentaje': 2.0}, {'seat': 2, 'percentaje': 1.0}, {'seat': 3, 'percentaje': 0.6667}, {'seat': 4, 'percentaje': 0.5}, {'seat': 5, 'percentaje': 0.4}, {
            'seat': 6, 'percentaje': 0.3333}, {'seat': 7, 'percentaje': 0.2857}, {'seat': 8, 'percentaje': 0.25}, {'seat': 9, 'percentaje': 0.2222}, {'seat': 10, 'percentaje': 0.2}]}, {'option': 'option 4', 'number': 5, 'votes': 4, 'dhont': [{'seat': 1, 'percentaje': 4.0}, {'seat': 2, 'percentaje': 2.0}, {'seat': 3, 'percentaje': 1.3333}, {'seat': 4, 'percentaje': 1.0}, {'seat': 5, 'percentaje': 0.8}, {'seat': 6, 'percentaje': 0.6667}, {'seat': 7, 'percentaje': 0.5714}, {'seat': 8, 'percentaje': 0.5}, {'seat': 9, 'percentaje': 0.4444}, {'seat': 10, 'percentaje': 0.4}]}, {'option': 'option 5', 'number': 6, 'votes': 1, 'dhont': [{'seat': 1, 'percentaje': 1.0}, {'seat': 2, 'percentaje': 0.5}, {'seat': 3, 'percentaje': 0.3333}, {'seat': 4, 'percentaje': 0.25}, {'seat': 5, 'percentaje': 0.2}, {'seat': 6, 'percentaje': 0.1667}, {'seat': 7, 'percentaje': 0.1429}, {'seat': 8, 'percentaje': 0.125}, {'seat': 9, 'percentaje': 0.1111}, {'seat': 10, 'percentaje': 0.1}]}

        serialized_mi_dhont = serialize('json', [compare_value[0]['dhont']], cls=DjangoJSONEncoder)
        serialized_otro_dhont = serialize('json', [correct_result['dhont']], cls=DjangoJSONEncoder)

        # Verifica la igualdad usando assertJSONEqual
        self.assertJSONEqual(serialized_mi_dhont, serialized_otro_dhont)


