from base.tests import BaseTestCase
import json
from base import mods
from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from census.models import Census
from mixnet.mixcrypt import MixCrypt, ElGamal
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from base.tests import BaseTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

from voting.models import Voting, Question
from .views import (
    build_census_map,
    build_vote_map,
    process_dho_voting_data,
    process_post_voting_data,
)
from rest_framework.test import APIClient


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

        self.store_votes(v)

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

        self.store_votes(v)

        self.login()  # set token

        v.tally_votes(self.token)

        response = self.client.get("/visualizer/" + str(v.id) + "/")

        self.assertEqual(
            len(json.loads(response.context_data["census"])["voters"]), 100
        )


class VisualizerSeleniumTesting(StaticLiveServerTestCase):
    def setUp(self):
        # Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True

        # Configuración de opciones
        option_list = [
            "--headless",
            "--disable-gpu",
            "--window-size=1920,1200",
            "--ignore-certificate-errors",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]

        for option in option_list:
            options.add_argument(option)

        # Asignar opciones al controlador
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

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
                self.base.login(user=user.username)
                voter = voters.pop()
                mods.post("store", json=data)
        return clear

    def test_not_open_data(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.save()

        self.driver.get(f'{self.live_server_url+"/visualizer/"+str(v.id)}')
        header = self.driver.find_element(By.CSS_SELECTOR, "h2")
        self.assertTrue(header.text == "Votación no comenzada")

    def test_open_data(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.driver.get(f'{self.live_server_url+"/visualizer/"+str(v.id)}')
        header = self.driver.find_element(By.CSS_SELECTOR, "h2")
        self.assertTrue(header.text == "Votación en curso")

    def test_closed_data(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.end_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.base.login()  # set token

        v.tally_votes(self.base.token)

        self.driver.get(f'{self.live_server_url+"/visualizer/"+str(v.id)}')
        header = self.driver.find_element(By.CSS_SELECTOR, "h2")
        self.assertTrue(header.text == "Estadísticas de la votación:")


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
        json.loads(json.dumps(r[0]))
        c = mods.get("census", params={"voting_id": v.id})
        i = 0
        res = build_census_map(c.get("voters"))
        while i < len(res.get("Id")):
            self.assertEquals(
                User.objects.get(pk=int(res.get("Id")[i])).username,
                str(res.get("Name")[i]),
            )
            i = i + 1

    def test_export_votes_dict(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        _ = self.store_votes(v)

        r = mods.get("voting", params={"id": v.id})
        a = json.loads(json.dumps(r[0]))
        res = build_vote_map(a)
        i = 0
        for option in res.get("question 1").get("option"):
            opt = a.get("questions")[0].get("options")[i].get("option")
            self.assertEquals(option, opt)
            i = i + 1


class exportPosprocDhont(BaseTestCase):
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
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(
                question=q, option="option {}".format(i + 1), number=i + 2
            )
            opt.save()
        v = Voting(name="test voting", postproc_type=postproc, voting_type=type)
        v.save()
        v.questions.set([q])
        v.save()

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
        for question in v.questions.all():
            for opt in question.options.all():
                clear[opt.number] = 0
                for _ in range(5):
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

    def test_correct_postproc1(self):
        v = self.create_voting("DHO", "S")

        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        expected = [
            {
                "dhont": [
                    {"seat": 1, "percentaje": 0.0},
                    {"seat": 2, "percentaje": 0.0},
                    {"seat": 3, "percentaje": 0.0},
                    {"seat": 4, "percentaje": 0.0},
                    {"seat": 5, "percentaje": 0.0},
                    {"seat": 6, "percentaje": 0.0},
                    {"seat": 7, "percentaje": 0.0},
                    {"seat": 8, "percentaje": 0.0},
                    {"seat": 9, "percentaje": 0.0},
                    {"seat": 10, "percentaje": 0.0},
                ],
                "votes": 0,
                "number": 2,
                "option": "option 1",
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 0.0},
                    {"seat": 2, "percentaje": 0.0},
                    {"seat": 3, "percentaje": 0.0},
                    {"seat": 4, "percentaje": 0.0},
                    {"seat": 5, "percentaje": 0.0},
                    {"seat": 6, "percentaje": 0.0},
                    {"seat": 7, "percentaje": 0.0},
                    {"seat": 8, "percentaje": 0.0},
                    {"seat": 9, "percentaje": 0.0},
                    {"seat": 10, "percentaje": 0.0},
                ],
                "votes": 0,
                "number": 3,
                "option": "option 2",
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 0.0},
                    {"seat": 2, "percentaje": 0.0},
                    {"seat": 3, "percentaje": 0.0},
                    {"seat": 4, "percentaje": 0.0},
                    {"seat": 5, "percentaje": 0.0},
                    {"seat": 6, "percentaje": 0.0},
                    {"seat": 7, "percentaje": 0.0},
                    {"seat": 8, "percentaje": 0.0},
                    {"seat": 9, "percentaje": 0.0},
                    {"seat": 10, "percentaje": 0.0},
                ],
                "votes": 0,
                "number": 4,
                "option": "option 3",
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 0.0},
                    {"seat": 2, "percentaje": 0.0},
                    {"seat": 3, "percentaje": 0.0},
                    {"seat": 4, "percentaje": 0.0},
                    {"seat": 5, "percentaje": 0.0},
                    {"seat": 6, "percentaje": 0.0},
                    {"seat": 7, "percentaje": 0.0},
                    {"seat": 8, "percentaje": 0.0},
                    {"seat": 9, "percentaje": 0.0},
                    {"seat": 10, "percentaje": 0.0},
                ],
                "votes": 0,
                "number": 5,
                "option": "option 4",
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 0.0},
                    {"seat": 2, "percentaje": 0.0},
                    {"seat": 3, "percentaje": 0.0},
                    {"seat": 4, "percentaje": 0.0},
                    {"seat": 5, "percentaje": 0.0},
                    {"seat": 6, "percentaje": 0.0},
                    {"seat": 7, "percentaje": 0.0},
                    {"seat": 8, "percentaje": 0.0},
                    {"seat": 9, "percentaje": 0.0},
                    {"seat": 10, "percentaje": 0.0},
                ],
                "votes": 0,
                "number": 6,
                "option": "option 5",
            },
        ]

        r = 0
        a = 0
        r = mods.get("voting", params={"id": v.id})
        a = json.loads(json.dumps(r[0]))
        res = process_dho_voting_data(a)

        i = 0
        while i < 5:
            compare = res.get("question 1")
            j = 0
            for seat in expected[i].get("dhont"):
                key = "seat " + str(j + 1)
                self.assertEquals(seat.get("percentaje"), compare.get(key)[i])
                j = j + 1
            i = i + 1


class exportPosprocPAR(BaseTestCase):
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
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(
                question=q, option="option {}".format(i + 1), number=i + 2
            )
            opt.save()
        v = Voting(name="test voting", postproc_type=postproc, voting_type=type)
        v.save()
        v.questions.set([q])
        v.save()

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
        for question in v.questions.all():
            for opt in question.options.all():
                clear[opt.number] = 0
                for _ in range(5):
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

    def test_correct_postproc1(self):
        v = self.create_voting("PAR", "S")

        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        r = 0
        a = 0
        r = mods.get("voting", params={"id": v.id})
        a = json.loads(json.dumps(r[0]))
        res = process_post_voting_data(a, "saintLague")
        i = 1
        j = 0
        for question in a.get("questions"):
            for option in question.get("options"):
                x = int(a.get("postproc").get("results")[j].get("saintLague"))
                y = int(res.get("question 1").get("saintLague")[j])
                self.assertEquals(x, y)
                j = j + 1
            i = i + 1


class exportPosprocDro(BaseTestCase):
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
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(
                question=q, option="option {}".format(i + 1), number=i + 2
            )
            opt.save()
        v = Voting(name="test voting", postproc_type=postproc, voting_type=type)
        v.save()
        v.questions.set([q])
        v.save()

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
        for question in v.questions.all():
            for opt in question.options.all():
                clear[opt.number] = 0
                for _ in range(5):
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

    def test_correct_postproc1(self):
        v = self.create_voting("DRO", "S")

        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        r = 0
        a = 0
        r = mods.get("voting", params={"id": v.id})
        a = json.loads(json.dumps(r[0]))
        res = process_post_voting_data(a, "droop")
        i = 1
        j = 0
        for question in a.get("questions"):
            for option in question.get("options"):
                x = int(a.get("postproc").get("results")[j].get("droop"))
                y = int(res.get("question 1").get("droop")[j])
                self.assertEquals(x, y)
                j = j + 1
            i = i + 1
