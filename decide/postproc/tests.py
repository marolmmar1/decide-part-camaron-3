from django.utils import timezone
from rest_framework.test import APIClient
from base.tests import BaseTestCase
from django.core.exceptions import ValidationError

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
            for i in range(5):
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

    def test_correct_postproc(self):
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

        dhont = postproc.results

        expected = [{'dhont': [{'seat': 1, 'percentaje': 5.0}, {'seat': 2, 'percentaje': 2.5}, {'seat': 3, 'percentaje': 1.6667}, {'seat': 4, 'percentaje': 1.25}, {'seat': 5, 'percentaje': 1.0}, {'seat': 6, 'percentaje': 0.8333}, {'seat': 7, 'percentaje': 0.7143}, {'seat': 8, 'percentaje': 0.625}, {'seat': 9, 'percentaje': 0.5556}, {'seat': 10, 'percentaje': 0.5}]}, {'dhont': [{'seat': 1, 'percentaje': 5.0}, {'seat': 2, 'percentaje': 2.5}, {'seat': 3, 'percentaje': 1.6667}, {'seat': 4, 'percentaje': 1.25}, {'seat': 5, 'percentaje': 1.0}, {'seat': 6, 'percentaje': 0.8333}, {'seat': 7, 'percentaje': 0.7143}, {'seat': 8, 'percentaje': 0.625}, {'seat': 9, 'percentaje': 0.5556}, {'seat': 10, 'percentaje': 0.5}]}, {'dhont': [{'seat': 1, 'percentaje': 5.0}, {'seat': 2, 'percentaje': 2.5}, {'seat': 3, 'percentaje': 1.6667}, {'seat': 4, 'percentaje': 1.25}, {'seat': 5, 'percentaje': 1.0}, {
            'seat': 6, 'percentaje': 0.8333}, {'seat': 7, 'percentaje': 0.7143}, {'seat': 8, 'percentaje': 0.625}, {'seat': 9, 'percentaje': 0.5556}, {'seat': 10, 'percentaje': 0.5}]}, {'dhont': [{'seat': 1, 'percentaje': 5.0}, {'seat': 2, 'percentaje': 2.5}, {'seat': 3, 'percentaje': 1.6667}, {'seat': 4, 'percentaje': 1.25}, {'seat': 5, 'percentaje': 1.0}, {'seat': 6, 'percentaje': 0.8333}, {'seat': 7, 'percentaje': 0.7143}, {'seat': 8, 'percentaje': 0.625}, {'seat': 9, 'percentaje': 0.5556}, {'seat': 10, 'percentaje': 0.5}]}, {'dhont': [{'seat': 1, 'percentaje': 5.0}, {'seat': 2, 'percentaje': 2.5}, {'seat': 3, 'percentaje': 1.6667}, {'seat': 4, 'percentaje': 1.25}, {'seat': 5, 'percentaje': 1.0}, {'seat': 6, 'percentaje': 0.8333}, {'seat': 7, 'percentaje': 0.7143}, {'seat': 8, 'percentaje': 0.625}, {'seat': 9, 'percentaje': 0.5556}, {'seat': 10, 'percentaje': 0.5}]}]

        for i in range(len(dhont)):
            for j in range(len(dhont[i]['dhont'])):
                self.assertEquals(
                    dhont[i]['dhont'][j], expected[i]['dhont'][j], 'Métricas no coinciden')

    def test_invalid_config_voting(self):
        try:
            self.create_voting('DHO', 'M')
        except ValidationError as e:
            self.assertEqual(
                e.message, 'Las técnicas de postprocesado no se pueden aplicar a votaciones no Simples')
        else:
            self.fail(
                "Se esperaba una excepción ValidationError, pero no se lanzó")
