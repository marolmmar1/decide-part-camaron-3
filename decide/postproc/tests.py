from django.utils import timezone
from rest_framework.test import APIClient
from base.tests import BaseTestCase
import itertools
import random
import json
from django.core.serializers import serialize
from django.db.models import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.exceptions import ValidationError
import pytest
import time
import json

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from base import mods
from django.contrib.auth.models import User, Permission
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
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(
                question=q, option="option {}".format(i + 1), number=i + 2
            )
            opt.save()
        v = Voting(
            name="test voting", question=q, postproc_type=postproc, voting_type=type
        )
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
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(5):
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

    def test_correct_postproc(self):
        v = self.create_voting("DHO", "S")

        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        postproc = PostProcessing.objects.get(voting=v)

        dhont = postproc.results

        expected = [
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
        ]

        for i in range(len(dhont)):
            for j in range(len(dhont[i]["dhont"])):
                self.assertEquals(
                    dhont[i]["dhont"][j],
                    expected[i]["dhont"][j],
                    "Métricas no coinciden",
                )

    def test_invalid_config_voting(self):
        try:
            self.create_voting("DHO", "M")
        except ValidationError as e:
            self.assertEqual(
                e.message,
                "Las técnicas de postprocesado no se pueden aplicar a votaciones no Simples",
            )
        else:
            self.fail("Se esperaba una excepción ValidationError, pero no se lanzó")


    def test_droop_wikipedia_example(self):
        # validating the functionality of the function using the wikipedia example
        test = [
            {"option": "Partido A", "number": 1, "votes": 391000},
            {"option": "Partido B", "number": 2, "votes": 311000},
            {"option": "Partido C", "number": 3, "votes": 184000},
            {"option": "Partido D", "number": 4, "votes": 73000},
            {"option": "Partido E", "number": 5, "votes": 27000},
            {"option": "Partido F", "number": 6, "votes": 12000},
            {"option": "Partido G", "number": 7, "votes": 2000},
        ]
        expected_result = [
            {"option": "Partido A", "number": 1, "votes": 391000, "droop": 8},
            {"option": "Partido B", "number": 2, "votes": 311000, "droop": 7},
            {"option": "Partido C", "number": 3, "votes": 184000, "droop": 4},
            {"option": "Partido D", "number": 4, "votes": 73000, "droop": 2},
            {"option": "Partido E", "number": 5, "votes": 27000, "droop": 0},
            {"option": "Partido F", "number": 6, "votes": 12000, "droop": 0},
            {"option": "Partido G", "number": 7, "votes": 2000, "droop": 0},
        ]
        seats = 21
        droop = PostProcessing.droop(None, opts=test, total_seats=seats)
        self.assertEquals(droop, expected_result)

    def test_correct_droop_postproc(self):
        v = self.create_voting("DRO", "S")
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.login()
        v.tally_votes(self.token)
        postproc = PostProcessing.objects.get(voting=v)

        droop = postproc.results

        expected_result = [
            {"option": "option 1", "number": 2, "votes": 5, "droop": 2},
            {"option": "option 2", "number": 3, "votes": 5, "droop": 2},
            {"option": "option 3", "number": 4, "votes": 5, "droop": 2},
            {"option": "option 4", "number": 5, "votes": 5, "droop": 2},
            {"option": "option 5", "number": 6, "votes": 5, "droop": 2},
        ]

        self.assertEqual(droop, expected_result)

    def test_invalid_droop_postproc(self):
        invalid_voting_types = ["M", "H", "Q"]
        for voting_type in invalid_voting_types:
            try:
                self.create_voting("DRO", voting_type)
            except ValidationError as e:
                self.assertEqual(
                    e.message,
                    "Las técnicas de postprocesado no se pueden aplicar a votaciones no Simples",
                )
            else:
                self.fail("Se esperaba una excepción ValidationError, pero no se lanzó")


class PostProcTestsSaintLague(BaseTestCase):
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
        v = Voting(
            name="test voting", question=q, postproc_type=postproc, voting_type=type
        )
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
        for opt in v.question.options.all():
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

    def test_saint_function(self):
        opts = [
            {"option": "A", "votes": 100},
            {"option": "B", "votes": 80},
        ]
        total_seats = 5

        instance = PostProcessing()
        instance.saint(opts, total_seats)

        self.assertEqual(len(opts), len(instance.results))

        total_seats_assigned = sum(option["saintLague"] for option in instance.results)
        self.assertEqual(total_seats, total_seats_assigned)

        for option in instance.results:
            expected_seats = round(
                (option["votes"] / sum(o["votes"] for o in opts)) * total_seats
            )
            self.assertEqual(option["saintLague"], expected_seats)

    def test_correct_postproc_saint_lague(self):
        v = self.create_voting("PAR", "S")
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.login()
        v.tally_votes(self.token)

        postproc = PostProcessing.objects.get(voting=v)

        saint_lague = postproc.results
        results_expected = [
            {"option": "option 1", "number": 2, "votes": 5, "saintLague": 2},
            {"option": "option 2", "number": 3, "votes": 5, "saintLague": 2},
            {"option": "option 3", "number": 4, "votes": 5, "saintLague": 2},
            {"option": "option 4", "number": 5, "votes": 5, "saintLague": 2},
            {"option": "option 5", "number": 6, "votes": 5, "saintLague": 2},
        ]

        self.assertEqual(saint_lague, results_expected)

    def test_invalid_config_voting(self):
        try:
            self.create_voting("PAR", "M")
        except ValidationError as e:
            self.assertEqual(
                e.message,
                "Las técnicas de postprocesado no se pueden aplicar a votaciones no Simples",
            )
        else:
            self.fail(
                "Se esperaba una excepción ValidationError, pero no se lanzó")

class TestSimulaciondhontFallido(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = False
        self.vars = {}
        self.driver = webdriver.Chrome(options=options)
        user_admin = User(username='adminB', is_staff=True, is_superuser=True)
        user_admin.set_password('qwertyA')
        user_admin.save()
        todos_los_permisos = Permission.objects.all()
        user_admin.user_permissions.add(*todos_los_permisos)
        user_admin.save()
        self.id = 5
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    def test_simulaciondhont(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.set_window_size(1348, 696)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("adminB")
        self.driver.find_element(By.ID, "id_password").send_keys("qwertyA")
        self.driver.find_element(
            By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.CSS_SELECTOR, ".content").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting > th").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Dhont")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys(
            "Testing con Dhont 3 opciones Si, No, Depende")
        self.driver.find_element(By.ID, "id_voting_type").click()
        self.driver.find_element(By.ID, "id_question").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.ID, "add_id_question").click()
        self.vars["win8378"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win8378"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Funcionará?")
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-optionSiNo .vCheckboxLabel").click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option > .checkbox-row").click()
        self.driver.find_element(By.ID, "id_third_option").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_postproc_type").click()
        dropdown = self.driver.find_element(By.ID, "id_postproc_type")
        dropdown.find_element(By.XPATH, "//option[. = 'DHONDT']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(3)").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(
            By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win6358"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win6358"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("perico")
        self.driver.find_element(By.ID, "id_url").send_keys(Keys.DOWN)
        self.driver.find_element(By.ID, "id_url").send_keys(
            "http://localhost:8000")
        self.driver.find_element(By.ID, "id_me").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_seats").click()
        self.driver.find_element(By.ID, "id_seats").send_keys("15")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f'{self.live_server_url}/admin/census/census/')
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys("1")
        self.driver.find_element(By.ID, "id_voter_id").send_keys(self.id)
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f'{self.live_server_url}/admin/voting/voting/')
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "option:nth-child(3)").click()
        self.driver.find_element(By.NAME, "index").click()
        sleep(8)
        self.driver.get(f'{self.live_server_url}/booth/4')
        sleep(5)
        self.driver.find_element(
            By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        sleep(3)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        sleep(3)
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("adminB")
        self.driver.find_element(By.ID, "password").send_keys("qwertyA")
        self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)
        sleep(3)
        self.driver.find_element(By.ID, "q1").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        sleep(2)
        alert_element = self.driver.find_element(By.CLASS_NAME, "alert-danger")
        div_contenido = alert_element.find_element(By.XPATH, ".//div").text
        self.assertEquals(div_contenido, "Error: Unauthorized",
                          "Usuario no Autenticado")

    def test_testerror(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.set_window_size(1348, 696)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("adminB")
        self.driver.find_element(By.ID, "id_password").send_keys("qwertyA")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("error")
        self.driver.find_element(By.ID, "id_desc").send_keys("combinacion invalida")
        self.driver.find_element(By.ID, "id_postproc_type").click()
        dropdown = self.driver.find_element(By.ID, "id_postproc_type")
        dropdown.find_element(By.XPATH, "//option[. = 'DHONDT']").click()
        sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-voting_type > div").click()
        self.driver.find_element(By.ID, "id_voting_type").click()
        dropdown = self.driver.find_element(By.ID, "id_voting_type")
        dropdown.find_element(By.XPATH, "//option[. = 'Multiple Choice']").click()
        self.driver.find_element(By.CSS_SELECTOR, "#id_voting_type > option:nth-child(2)").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win9368"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win9368"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("garrafon")
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.ID, "id_me").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_question").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_question > img").click()
        self.vars["win6844"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win6844"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("perico")
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("a")
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("b")
        self.driver.find_element(By.ID, "id_options-2-number").send_keys("3")
        self.driver.find_element(By.ID, "id_options-2-option").send_keys("c")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.NAME, "_save").click()
        
        sleep(3)
        assert "validationerror" in self.driver.page_source or "500" in self.driver.page_source
