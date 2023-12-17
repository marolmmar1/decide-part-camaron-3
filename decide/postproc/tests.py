from django.utils import timezone
from rest_framework.test import APIClient
from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.exceptions import ValidationError
import time

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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

        for i in range(len(dhont)):
            for j in range(len(dhont[i]["dhont"])):
                self.assertEquals(
                    dhont[i]["dhont"][j],
                    expected[i]["dhont"][j],
                    "Métricas no coinciden",
                )

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
            {"droop": 1, "votes": 0, "number": 2, "option": "option 1"},
            {"droop": 1, "votes": 0, "number": 3, "option": "option 2"},
            {"droop": 1, "votes": 0, "number": 4, "option": "option 3"},
            {"droop": 1, "votes": 0, "number": 5, "option": "option 4"},
            {"droop": 1, "votes": 0, "number": 6, "option": "option 5"},
        ]

        self.assertEqual(droop, expected_result)

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


class TestSimulacionDroop(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.vars = {}
        self.driver = webdriver.Chrome(options=options)
        user_admin = User(username="adminB", is_staff=True, is_superuser=True)
        user_admin.set_password("qwertyA")
        user_admin.save()
        todos_los_permisos = Permission.objects.all()
        user_admin.user_permissions.add(*todos_los_permisos)
        user_admin.save()
        self.id = user_admin.id
        self.id_votacion = 1

        prueba_votacion = Voting.objects.last()
        if not prueba_votacion:
            prueba_votacion = 0
        else:
            prueba_votacion = prueba_votacion.id

        prueba_usuario = User.objects.last()
        if not prueba_usuario:
            prueba_usuario = 0
        else:
            prueba_usuario = prueba_usuario.id

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

    def test_01_simulaciondroop(self):
        self.driver.get(f"{self.live_server_url}/admin/")
        self.driver.set_window_size(1348, 696)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("adminB")
        self.driver.find_element(By.ID, "id_password").send_keys("qwertyA")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.CSS_SELECTOR, ".content").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting > th").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("droop")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys(
            "Testing con droop 3 opciones Si, No, Depende"
        )
        self.driver.find_element(By.ID, "id_voting_type").click()
        self.driver.find_element(By.ID, "id_questions").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.ID, "add_id_questions").click()
        self.vars["win8378"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win8378"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Funcionará?")
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-optionSiNo .vCheckboxLabel"
        ).click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option > .checkbox-row"
        ).click()
        self.driver.find_element(By.ID, "id_third_option").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_postproc_type").click()
        dropdown = self.driver.find_element(By.ID, "id_postproc_type")
        dropdown.find_element(By.XPATH, "//option[. = 'DROOP']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(3)"
        ).click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win6358"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win6358"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("perico")
        self.driver.find_element(By.ID, "id_url").send_keys(Keys.DOWN)
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.ID, "id_me").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_seats").click()
        self.driver.find_element(By.ID, "id_seats").send_keys("15")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/census/census/")
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys(self.id_votacion)
        self.driver.find_element(By.ID, "id_voter_id").send_keys(self.id)
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/voting/voting/")
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(3)").click()
        self.driver.find_element(By.NAME, "index").click()

        # Obtener el id de la votación justamente creada
        prueba_votacion = Voting.objects.last().id

        sleep(8)
        self.driver.get(f"{self.live_server_url}/booth/{prueba_votacion}")
        sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        sleep(3)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        sleep(3)
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("adminB")
        self.driver.find_element(By.ID, "password").send_keys("qwertyA")
        self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)
        sleep(3)
        self.driver.find_element(By.ID, "opt2_index0").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        sleep(2)
        alert_element = self.driver.find_element(By.CLASS_NAME, "alert-danger")
        div_contenido = alert_element.find_element(By.XPATH, ".//div").text
        self.assertEquals(
            div_contenido, "Error: Unauthorized", "Usuario no Autenticado"
        )

    def test_02_error(self):
        self.driver.get(f"{self.live_server_url}/admin/")
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
        dropdown.find_element(By.XPATH, "//option[. = 'DROOP']").click()
        sleep(2)
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(2)"
        ).click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-voting_type > div").click()
        self.driver.find_element(By.ID, "id_voting_type").click()
        dropdown = self.driver.find_element(By.ID, "id_voting_type")
        dropdown.find_element(By.XPATH, "//option[. = 'Multiple Choice']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_voting_type > option:nth-child(2)"
        ).click()
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
        self.driver.find_element(By.ID, "id_questions").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_questions > img").click()
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
        assert (
            "validationerror" in self.driver.page_source
            or "500" in self.driver.page_source
        )


class TestSimulacionDhont(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.vars = {}
        self.driver = webdriver.Chrome(options=options)
        user_admin = User(username="adminB", is_staff=True, is_superuser=True)
        user_admin.set_password("qwertyA")
        user_admin.save()
        todos_los_permisos = Permission.objects.all()
        user_admin.user_permissions.add(*todos_los_permisos)
        user_admin.save()
        self.id = user_admin.id
        self.id_votacion = 1

        prueba_votacion = Voting.objects.last()
        if not prueba_votacion:
            prueba_votacion = 0
        else:
            prueba_votacion = prueba_votacion.id

        prueba_usuario = User.objects.last()
        if not prueba_usuario:
            prueba_usuario = 0
        else:
            prueba_usuario = prueba_usuario.id

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

    def test_01_simulaciondhont(self):
        self.driver.get(f"{self.live_server_url}/admin/")
        self.driver.set_window_size(1348, 696)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("adminB")
        self.driver.find_element(By.ID, "id_password").send_keys("qwertyA")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.CSS_SELECTOR, ".content").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting > th").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Dhont")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys(
            "Testing con Dhont 3 opciones Si, No, Depende"
        )
        self.driver.find_element(By.ID, "id_voting_type").click()
        self.driver.find_element(By.ID, "id_questions").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.ID, "add_id_questions").click()
        self.vars["win8378"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win8378"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Funcionará?")
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-optionSiNo .vCheckboxLabel"
        ).click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option > .checkbox-row"
        ).click()
        self.driver.find_element(By.ID, "id_third_option").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_postproc_type").click()
        dropdown = self.driver.find_element(By.ID, "id_postproc_type")
        dropdown.find_element(By.XPATH, "//option[. = 'DHONDT']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(3)"
        ).click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win6358"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win6358"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("perico")
        self.driver.find_element(By.ID, "id_url").send_keys(Keys.DOWN)
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.ID, "id_me").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_seats").click()
        self.driver.find_element(By.ID, "id_seats").send_keys("15")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/census/census/")
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys(self.id_votacion)
        self.driver.find_element(By.ID, "id_voter_id").send_keys(self.id)
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/voting/voting/")
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(3)").click()
        self.driver.find_element(By.NAME, "index").click()

        # Obtener el id de la votación justamente creada
        prueba_votacion = Voting.objects.last().id

        sleep(8)
        self.driver.get(f"{self.live_server_url}/booth/{prueba_votacion}")
        sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        sleep(3)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        sleep(3)
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("adminB")
        self.driver.find_element(By.ID, "password").send_keys("qwertyA")
        self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)
        sleep(5)
        self.driver.find_element(By.ID, "opt2_index0").click()
        sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        sleep(2)
        alert_element = self.driver.find_element(By.CLASS_NAME, "alert-danger")
        div_contenido = alert_element.find_element(By.XPATH, ".//div").text
        self.assertEquals(
            div_contenido, "Error: Unauthorized", "Usuario no Autenticado"
        )

    def test_02_error(self):
        self.driver.get(f"{self.live_server_url}/admin/")
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
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(2)"
        ).click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-voting_type > div").click()
        self.driver.find_element(By.ID, "id_voting_type").click()
        dropdown = self.driver.find_element(By.ID, "id_voting_type")
        dropdown.find_element(By.XPATH, "//option[. = 'Multiple Choice']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_voting_type > option:nth-child(2)"
        ).click()
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
        self.driver.find_element(By.ID, "id_questions").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_questions > img").click()
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
        assert (
            "validationerror" in self.driver.page_source
            or "500" in self.driver.page_source
        )

    def test_03_grantpermisions(self):
        self.driver.get(f"{self.live_server_url}/admin/")
        self.driver.set_window_size(642, 696)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("adminB")
        self.driver.find_element(By.ID, "id_password").send_keys("qwertyA")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        sleep(5)
        self.driver.find_element(By.LINK_TEXT, "Users").click()
        self.driver.find_element(By.LINK_TEXT, "adminB").click()
        self.driver.find_element(By.NAME, "_save").click()
        sleep(10)
        assert "was changed" in self.driver.page_source

    def test_04_simulaciondhont_tally(self):
        self.driver.get(f"{self.live_server_url}/admin/")
        self.driver.set_window_size(1348, 696)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("adminB")
        self.driver.find_element(By.ID, "id_password").send_keys("qwertyA")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.CSS_SELECTOR, ".content").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting > th").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Dhont")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys(
            "Testing con Dhont 3 opciones Si, No, Depende"
        )
        self.driver.find_element(By.ID, "id_voting_type").click()
        self.driver.find_element(By.ID, "id_questions").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.ID, "add_id_questions").click()
        self.vars["win8378"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win8378"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Funcionará?")
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-optionSiNo .vCheckboxLabel"
        ).click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option > .checkbox-row"
        ).click()
        self.driver.find_element(By.ID, "id_third_option").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_postproc_type").click()
        dropdown = self.driver.find_element(By.ID, "id_postproc_type")
        dropdown.find_element(By.XPATH, "//option[. = 'DHONDT']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(3)"
        ).click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win6358"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win6358"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("perico")
        self.driver.find_element(By.ID, "id_url").send_keys(Keys.DOWN)
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.ID, "id_me").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_seats").click()
        self.driver.find_element(By.ID, "id_seats").send_keys("15")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/census/census/")
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys(self.id_votacion)
        self.driver.find_element(By.ID, "id_voter_id").send_keys(self.id)
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/voting/voting/")
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(3)").click()
        self.driver.find_element(By.NAME, "index").click()
        sleep(8)
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Stop']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(4)").click()
        self.driver.find_element(By.NAME, "index").click()
        sleep(5)
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Tally']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(5)").click()
        self.driver.find_element(By.NAME, "index").click()
        sleep(3)
        assert "500" in self.driver.page_source


class TestSimulacionSaintLague(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.vars = {}
        self.driver = webdriver.Chrome(options=options)
        user_admin = User(username="adminB", is_staff=True, is_superuser=True)
        user_admin.set_password("qwertyA")
        user_admin.save()
        todos_los_permisos = Permission.objects.all()
        user_admin.user_permissions.add(*todos_los_permisos)
        user_admin.save()
        self.id = user_admin.id
        self.id_votacion = 1

        prueba_votacion = Voting.objects.last()
        if not prueba_votacion:
            prueba_votacion = 0
        else:
            prueba_votacion = prueba_votacion.id

        prueba_usuario = User.objects.last()
        if not prueba_usuario:
            prueba_usuario = 0
        else:
            prueba_usuario = prueba_usuario.id

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

    def test_01_simulacion_saint_lague(self):
        self.driver.get(f"{self.live_server_url}/admin/")
        self.driver.set_window_size(1348, 696)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("adminB")
        self.driver.find_element(By.ID, "id_password").send_keys("qwertyA")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.CSS_SELECTOR, ".content").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting > th").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Saint")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys(
            "Testing con Saint Lague 3 opciones Si, No, Depende"
        )
        self.driver.find_element(By.ID, "id_voting_type").click()
        self.driver.find_element(By.ID, "id_questions").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.ID, "add_id_questions").click()
        self.vars["win8378"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win8378"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Funcionará?")
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-optionSiNo .vCheckboxLabel"
        ).click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option > .checkbox-row"
        ).click()
        self.driver.find_element(By.ID, "id_third_option").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_postproc_type").click()
        dropdown = self.driver.find_element(By.ID, "id_postproc_type")
        dropdown.find_element(By.XPATH, "//option[. = 'SAINT']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(4)"
        ).click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win6358"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win6358"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("perico")
        self.driver.find_element(By.ID, "id_url").send_keys(Keys.DOWN)
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.ID, "id_me").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_seats").click()
        self.driver.find_element(By.ID, "id_seats").send_keys("15")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/census/census/")
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys(self.id_votacion)
        self.driver.find_element(By.ID, "id_voter_id").send_keys(self.id)
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/voting/voting/")
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(3)").click()
        self.driver.find_element(By.NAME, "index").click()

        # Obtener el id de la votación justamente creada
        prueba_votacion = Voting.objects.last().id

        sleep(8)
        self.driver.get(f"{self.live_server_url}/booth/{prueba_votacion}")
        sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        sleep(3)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        sleep(3)
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("adminB")
        self.driver.find_element(By.ID, "password").send_keys("qwertyA")
        self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)
        sleep(3)
        self.driver.find_element(By.ID, "opt2_index0").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        sleep(2)
        alert_element = self.driver.find_element(By.CLASS_NAME, "alert-danger")
        div_contenido = alert_element.find_element(By.XPATH, ".//div").text
        self.assertEquals(
            div_contenido, "Error: Unauthorized", "Usuario no Autenticado"
        )

    def test_02_validation_error(self):
        self.driver.get(f"{self.live_server_url}/admin/")
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
        dropdown.find_element(By.XPATH, "//option[. = 'SAINT']").click()
        sleep(2)
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(2)"
        ).click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-voting_type > div").click()
        self.driver.find_element(By.ID, "id_voting_type").click()
        dropdown = self.driver.find_element(By.ID, "id_voting_type")
        dropdown.find_element(By.XPATH, "//option[. = 'Multiple Choice']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_voting_type > option:nth-child(2)"
        ).click()
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
        self.driver.find_element(By.ID, "id_questions").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_questions > img").click()
        self.vars["win6844"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win6844"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("a")
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
        assert (
            "validationerror" in self.driver.page_source
            or "500" in self.driver.page_source
        )

    def test_03_permissions_saint_lague(self):
        self.driver.get(f"{self.live_server_url}/admin/")
        self.driver.set_window_size(642, 696)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("adminB")
        self.driver.find_element(By.ID, "id_password").send_keys("qwertyA")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        sleep(5)
        self.driver.find_element(By.LINK_TEXT, "Users").click()
        self.driver.find_element(By.LINK_TEXT, "adminB").click()
        self.driver.find_element(By.NAME, "_save").click()
        sleep(10)
        assert "was changed" in self.driver.page_source

    def test_04_simulacion_votacion_saint_lague(self):
        self.driver.get(f"{self.live_server_url}/admin/")
        self.driver.set_window_size(1348, 696)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("adminB")
        self.driver.find_element(By.ID, "id_password").send_keys("qwertyA")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.CSS_SELECTOR, ".content").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting > th").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Saint Lague")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys(
            "Testing con Saint Lague 3 opciones Si, No, Depende"
        )
        self.driver.find_element(By.ID, "id_voting_type").click()
        self.driver.find_element(By.ID, "id_questions").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.ID, "add_id_questions").click()
        self.vars["win8378"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win8378"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Funcionará?")
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-optionSiNo .vCheckboxLabel"
        ).click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option > .checkbox-row"
        ).click()
        self.driver.find_element(By.ID, "id_third_option").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_postproc_type").click()
        dropdown = self.driver.find_element(By.ID, "id_postproc_type")
        dropdown.find_element(By.XPATH, "//option[. = 'SAINT']").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#id_postproc_type > option:nth-child(4)"
        ).click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win6358"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win6358"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("perico")
        self.driver.find_element(By.ID, "id_url").send_keys(Keys.DOWN)
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.ID, "id_me").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_seats").click()
        self.driver.find_element(By.ID, "id_seats").send_keys("15")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/census/census/")
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys(self.id_votacion)
        self.driver.find_element(By.ID, "id_voter_id").send_keys(self.id)
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f"{self.live_server_url}/admin/voting/voting/")
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(3)").click()
        self.driver.find_element(By.NAME, "index").click()
        sleep(8)
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Stop']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(4)").click()
        self.driver.find_element(By.NAME, "index").click()
        sleep(5)
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Tally']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(5)").click()
        self.driver.find_element(By.NAME, "index").click()
        sleep(3)
        assert "500" in self.driver.page_source
