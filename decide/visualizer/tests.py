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
from base.tests import BaseTestCase

from voting.models import Voting, Question
from .views import build_census_map, build_vote_map


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
        q = Question(desc="test question")
        q.save()
        for i in range(3):
            opt = QuestionOption(
                question=q, option="option {}".format(i + 1), number=i + 2
            )
            opt.save()
        v = Voting(name="test voting")
        v.save()
        v.questions.set([q])

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username="testvoter{}".format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = "user{}".format(pk)
        user.set_password("qwerty")
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.questions.all()[0].options.all():
            clear[opt.number] = 0
            for _ in range(3):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    "voting": v.id,
                    "voter": voter.voter_id,
                    "vote": {"a": a, "b": b},
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post("store", json=data)
        return clear

    def test_not_open(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.save()

        response = self.client.get("/visualizer/" + str(v.id) + "/")

        self.assertIsNone(json.loads(response.context_data["voting"])["tally"])

    def test_visualizer_open_data(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        _ = self.store_votes(v)

        response = self.client.get("/visualizer/" + str(v.id) + "/")
        self.assertEqual(
            len(json.loads(response.context_data["census"])["voters"]), 100
        )
        self.assertIsNone(json.loads(response.context_data["voting"])["tally"])

    def test_visualizer_closed_data(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        _ = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        response = self.client.get("/visualizer/" + str(v.id) + "/")

        self.assertEqual(
            len(json.loads(response.context_data["census"])["voters"]), 100
        )
        #self.assertEqual(len(json.loads(response.context_data["voting"])["tally"]), 9)

class visualizerExportCensus(BaseTestCase):
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
        q = Question(desc="test question")
        q.save()
        for i in range(3):
            opt = QuestionOption(
                question=q, option="option {}".format(i + 1), number=i + 2
            )
            opt.save()
        v = Voting(name="test voting")
        v.save()
        v.questions.set([q])

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username="testvoter{}".format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = "user{}".format(pk)
        user.set_password("qwerty")
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.questions.all()[0].options.all():
            clear[opt.number] = 0
            for _ in range(3):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    "voting": v.id,
                    "voter": voter.voter_id,
                    "vote": {"a": a, "b": b},
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post("store", json=data)
        return clear

    
    
    def test_export_census_dict(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        _ = self.store_votes(v)
        r = mods.get("voting", params={"id": v.id})
        a = json.loads(json.dumps(r[0]))
        c = mods.get("census", params={"voting_id": v.id})
        i =0
        res = build_census_map(c.get("voters"))
        while i<len(res.get('Id')):
            self.assertEquals(User.objects.get(pk=int(res.get('Id')[i])).username, str(res.get('Name')[i]))
            i = i+1
        
        
    
    def test_export_votes_dict(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        _ = self.store_votes(v)

        r = mods.get("voting", params={"id": v.id})
        a = json.loads(json.dumps(r[0]))
        res =build_vote_map(a)
        i=0
        for option in res.get('question 1').get('option'):
            opt =a.get('questions')[0].get("options")[i].get('option')
            self.assertEquals(option, opt)
            i=i+1
            
    