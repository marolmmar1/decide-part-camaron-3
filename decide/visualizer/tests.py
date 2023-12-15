from base.tests import BaseTestCase
import itertools
import json
from base import mods
from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from census.models import Census
from mixnet.mixcrypt import MixCrypt, ElGamal

# Create your tests here.

class visualizerTest(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(3):
            opt = QuestionOption(question=q, option='option {}'.format(i+1), number=i+2)
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
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
            for _ in range(3):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])


    def test_visualizer_render(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        _ = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        response = self.client.get('/visualizer/' + str(v.id) + "/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visualizer/visualizer.html')

        self.assertIn('voting', response.context)
        self.assertIn('census', response.context)

    def test_not_open(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.save()

        response = self.client.get('/visualizer/' + str(v.id) + "/")

        self.assertIsNone(json.loads(response.context_data['voting'])['tally'])

    def test_visualizer_open_data(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        _ = self.store_votes(v)

        response = self.client.get('/visualizer/' + str(v.id) + "/")
        self.assertEqual(len(json.loads(response.context_data['census'])['voters']),100)
        self.assertIsNone(json.loads(response.context_data['voting'])['tally'])


    def test_visualizer_closed_data(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        _ = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        response = self.client.get('/visualizer/' + str(v.id) + "/")

        self.assertEqual(len(json.loads(response.context_data['census'])['voters']),100)
        self.assertEqual(len(json.loads(response.context_data['voting'])['tally']),9)

