import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

import time
from selenium.webdriver.common.action_chains import ActionChains

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
from django.core.exceptions import ValidationError


class TestTestselenium1:
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    def test_testselenium1(self):
        self.driver.get("http://127.0.0.1:8000/admin/login/?next=/admin/")
        self.driver.set_window_size(1311, 606)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("admin")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        dropdown = self.driver.find_element(By.ID, "id_voting_type")
        dropdown.find_element(By.XPATH, "//option[. = 'Single Choice']").click()
        element = self.driver.find_element(By.ID, "id_voting_type")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_voting_type")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_voting_type")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-name > div").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Champions")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Ganar la champions")
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_question > img").click()
        self.vars["win504"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win504"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys(
            "¿Ganará el Atletico de Madrid la Champions?"
        )
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-optionSiNo .vCheckboxLabel"
        ).click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option .vCheckboxLabel"
        ).click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win5929"] = self.wait_for_window(2000)
        if self.vars["win5929"] in self.driver.window_handles:
            self.driver.switch_to.window(self.vars["win5929"])
        else:
            print("La ventana no existe o ya ha sido cerrada.")
        self.driver.switch_to.window(self.vars["win5929"])
        self.driver.find_element(By.ID, "id_url").click()
        self.driver.find_element(By.ID, "id_url").send_keys("http://127.0.0.1:8000")
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").click()
        element = self.driver.find_element(By.ID, "id_name")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "id_name").send_keys("url")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(
            By.LINK_TEXT, "¿Ganará el Atletico de Madrid la Champions?"
        ).click()
        self.driver.find_element(By.NAME, "_save").click()


class TestTestselenium2:
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    def test_testselenium2(self):
        self.driver.get("http://127.0.0.1:8000/admin/login/?next=/admin/")
        self.driver.set_window_size(1050, 708)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.CSS_SELECTOR, ".login").click()
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("admin")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        dropdown = self.driver.find_element(By.ID, "id_voting_type")
        dropdown.find_element(By.XPATH, "//option[. = 'Single Choice']").click()
        element = self.driver.find_element(By.ID, "id_voting_type")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_voting_type")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_voting_type")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Votacion Atleti")
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_question > img").click()
        self.vars["win6767"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win6767"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").click()
        element = self.driver.find_element(By.ID, "id_desc")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "id_desc").send_keys(
            "¿Ganará algo el Atleti este año?"
        )
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Votacion Atleti")
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win2405"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win2405"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("url")
        self.driver.find_element(By.ID, "id_url").click()
        self.driver.find_element(By.ID, "id_url").click()
        element = self.driver.find_element(By.ID, "id_url")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "id_url").send_keys("http://127.0.0.1:8000")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(
            By.LINK_TEXT, "¿Ganará algo el Atleti este año?"
        ).click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option .vCheckboxLabel"
        ).click()
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.CSS_SELECTOR, "#options-0 > .field-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys(
            "Ganará la Champions"
        )
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys(
            "No ganará nada"
        )
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys(
            "Ganará un título"
        )
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-__str__ > a").click()
        self.driver.find_element(By.NAME, "_save").click()


class VotingTestCase(BaseTestCase):
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
        for i in range(5):
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

    def test_to_string(self):
        # Crea un objeto votacion
        v = self.create_voting()
        # Verifica que el nombre de la votacion es test voting
        self.assertEquals(str(v), "test voting")
        # Verifica que la descripcion de la pregunta sea test question
        # self.assertEquals(str(v.questions.),"test question")
        # Verifica que la primera opcion es option1 (2)
        # self.assertEquals(str(v.question.options.all()[0]),"option 1 (2)")

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for question in v.questions.all():
            for opt in question.options.all():
                clear[opt.number] = 0
                for i in range(random.randint(0, 5)):
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

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)
        self.login()  # set token
        v.tally_votes(self.token)
        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_create_voting_from_api(self):
        data = {"name": "Example"}
        response = self.client.post("/voting/", data, format="json")
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user="noadmin")
        response = mods.post("voting", params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post("voting", params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            "voting_type": "S",
            "name": "Example",
            "desc": "Description example",
            "questions": ["I want a "],
            "seats": 8,
            "questions_opt": [["cat", "dog", "horse"]],
            "postproc_type": "DHONT",
        }

        response = self.client.post("/voting/", data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {"action": "start"}

        # response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        # self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user="noadmin")
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {"action": "bad"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ["stop", "tally"]:
            data = {"action": action}
            response = self.client.put(
                "/voting/{}/".format(voting.pk), data, format="json"
            )

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), "Voting is not started")

        data = {"action": "start"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Voting started")

        # STATUS VOTING: started
        data = {"action": "start"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already started")

        data = {"action": "tally"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting is not stopped")

        data = {"action": "stop"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Voting stopped")

        # STATUS VOTING: stopped
        data = {"action": "start"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already started")

        data = {"action": "stop"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already stopped")

        data = {"action": "tally"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Voting tallied")

        # STATUS VOTING: tallied
        data = {"action": "start"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already started")

        data = {"action": "stop"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already stopped")

        data = {"action": "tally"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already tallied")

    def test_update_voting_405(self):
        v = self.create_voting()
        data = {}  # El campo action es requerido en la request
        self.login()
        response = self.client.post("/voting/{}/".format(v.pk), data, format="json")
        self.assertEquals(response.status_code, 405)

    def test_create_voting_multiple_questions_from_api(self):
        # login with user admin
        self.login()
        data = {
            "voting_type": "S",
            "name": "Example",
            "desc": "Description example",
            "questions": ["I want a ", "I prefer a"],
            "questions_opt": [["cat", "dog", "horse"], ["red", "blue", "green"]],
            "seats": 10,
            "postproc_type": "DHONT",
        }

        response = self.client.post("/voting/", data, format="json")
        self.assertEqual(response.status_code, 201)


class VotingModelTestCase(BaseTestCase):
    def setUp(self):
        q = Question(desc="Descripcion")
        q.save()

        opt1 = QuestionOption(question=q, option="opcion 1")
        opt1.save()
        opt1 = QuestionOption(question=q, option="opcion 2")
        opt1.save()

        self.v = Voting(name="Votacion")

        self.v.save()
        self.v.questions.set([q])
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v = None

    def testExist(self):
        v = Voting.objects.get(name="Votacion")
        for question in v.questions.all():
            self.assertEquals(question.options.all()[0].option, "opcion 1")


class VotingTypeTestCase(BaseTestCase):
    def test_create_voting_with_invalid_voting_type(self):
        q = Question(desc="Descripcion")
        q.save()

        opt1 = QuestionOption(question=q, option="opcion type 1")
        opt1.save()
        opt2 = QuestionOption(question=q, option="opcion type 2")
        opt2.save()

        with self.assertRaises(ValidationError):
            self.v = Voting(name="Votacion_Type", voting_type="INVALID")
            self.v.full_clean()
            self.v.save()

        votings_with_invalid_type = Voting.objects.filter(name="Votacion_Type")
        self.assertEqual(votings_with_invalid_type.count(), 0)


class VotingHierarchyModelTestCase(BaseTestCase):
    def setUp(self):
        q = Question(desc="Descripcion")
        q.save()

        opt1 = QuestionOption(question=q, option="opcion hierarchy 1")
        opt1.save()
        opt1 = QuestionOption(question=q, option="opcion hierarchy 2")
        opt1.save()

        self.v = Voting(name="Votacion_Hierarchy", voting_type="H")

        self.v.save()
        self.v.questions.set([q])
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v = None

    def testExist(self):
        v = Voting.objects.get(name="Votacion_Hierarchy")
        for question in v.questions.all():
            self.assertEquals(question.options.all()[0].option, "opcion hierarchy 1")
            self.assertEquals(v.voting_type, "H")


class LogInSuccessTests(StaticLiveServerTestCase):
    def setUp(self):
        # Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def successLogIn(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")
        self.assertTrue(self.cleaner.current_url == self.live_server_url + "/admin/")


class LogInErrorTests(StaticLiveServerTestCase):
    def setUp(self):
        # Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def usernameWrongLogIn(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[2]/div/div[1]/p"
            ).text
            == "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
        )

    def passwordWrongLogIn(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("wrongPassword")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[2]/div/div[1]/p"
            ).text
            == "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
        )


class QuestionsTests(StaticLiveServerTestCase):
    def setUp(self):
        # Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def createQuestionSuccess(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/voting/question/add/")

        self.cleaner.find_element(By.ID, "id_desc").click()
        self.cleaner.find_element(By.ID, "id_desc").send_keys("Test")
        self.cleaner.find_element(By.ID, "id_options-0-number").click()
        self.cleaner.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.cleaner.find_element(By.ID, "id_options-0-option").click()
        self.cleaner.find_element(By.ID, "id_options-0-option").send_keys("test1")

        self.cleaner.find_element(By.ID, "id_options-1-number").click()
        self.cleaner.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.cleaner.find_element(By.ID, "id_options-1-option").click()
        self.cleaner.find_element(By.ID, "id_options-1-option").send_keys("test2")
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.current_url == self.live_server_url + "/admin/voting/question/"
        )

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/voting/question/add/")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[3]/div/div[1]/div/form/div/p"
            ).text
            == "Please correct the errors below."
        )
        self.assertTrue(
            self.cleaner.current_url
            == self.live_server_url + "/admin/voting/question/add/"
        )


class VotingModelTestCaseOptionSiNo(BaseTestCase):
    def setUp(self):
        q = Question(desc="Test question", optionSiNo=True)
        q.save()
        self.v = Voting(name="Votacion")

        self.v.save()
        self.v.questions.set([q])

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v = None

    def testExist(self):
        v = Voting.objects.get(name="Votacion")
        for question in v.questions.all():
            self.assertTrue(question.options.count() == 2)
            self.assertEquals(question.options.all()[0].option, "Sí")
            self.assertEquals(question.options.all()[1].option, "No")

    def test_cannot_add_more_options(self):
        with self.assertRaises(ValidationError):
            for question in self.v.questions.all():
                new_option = QuestionOption(question=question, number=3, option="Maybe")
                new_option.save()

    def test_cannot_delete_predefined_options(self):
        for question in self.v.questions.all():
            options = question.options.all()
            initial_option_count = options.count()
            # Intentar eliminar la opción "Sí"
            yes_option = options.get(option="Sí")
            with self.assertRaises(ValidationError):
                yes_option.delete()

            # Verificar que el número de opciones no ha cambiado
            final_option_count = options.count()
            self.assertEqual(initial_option_count, final_option_count)

    def test_cannot_edit_predefined_options(self):
        # Intentar editar la opción "Sí"
        for question in self.v.questions.all():
            options = question.options.all()
            yes_option = options.get(option="Sí")
            with self.assertRaises(ValidationError):
                yes_option.option = "Maybe"
                yes_option.save()

    def test_can_change_options_to_depends(self):
        # Cambiar la pregunta de "Sí/No" a "Depende"
        for question in self.v.questions.all():
            question.optionSiNo = False
            question.third_option = True
            question.save()

            # Verificar que las opciones se han actualizado correctamente
            options = question.options.values_list("option", flat=True)
            self.assertIn("Depende", options)

    def test_cannot_add_more_than_three_options(self):
        for question in self.v.questions.all():
            question.third_option = True
            question.save()

            with self.assertRaises(ValidationError):
                new_option = QuestionOption(question=question, number=4, option="Maybe")
                new_option.save()

    def test_can_add_third_option(self):
        # Establecer third_option en True
        for question in self.v.questions.all():
            question.third_option = True
            question.save()
            # Añadir una tercera opción
            new_option = QuestionOption(question=question, number=3, option="Depende")
            new_option.save()

            # Verificar que la tercera opción se ha añadido correctamente
            options = question.options.values_list("option", flat=True)
            self.assertIn("Depende", options)


class VotingModelTestCaseThirdOption(TestCase):
    def setUp(self):
        self.v = Voting(name="Test Voting")
        self.q = Question(desc="Test question")
        self.q.save()
        self.v.question_id = self.q.id
        self.v.save()
        self.opt1 = QuestionOption(question=self.q, number=1, option="Yes")
        self.opt1.save()
        self.opt2 = QuestionOption(question=self.q, number=2, option="No")
        self.opt2.save()

    def test_can_change_third_option_to_false(self):
        self.q.third_option = True
        self.q.save()


        new_option = QuestionOption(question=self.q, number=3, option="Depende")
        new_option.save()
        self.q.third_option = False
        new_option.delete()
        self.q.save()
        self.assertFalse(self.q.third_option)

    def test_can_set_third_option_true_if_more_than_two_options_defined(self):
        new_option = QuestionOption(question=self.q, number=3, option="Depende")
        new_option.save()

        self.q.third_option = True
        self.q.save()
        self.assertTrue(self.q.third_option)

    def test_can_toggle_third_option(self):
        self.q.third_option = True
        self.q.save()

        new_option = QuestionOption(question=self.q, number=3, option="Depende")
        new_option.save()

        self.q.third_option = False
        new_option.delete()
        self.q.save()

        self.q.third_option = True
        self.q.save()
        self.assertTrue(self.q.third_option)

class VotingModelTestCasePreference(BaseTestCase):
    def setUp(self):        
        q = Question(desc='Test question')
        q.save()

        opt1 = QuestionOption(question=q, option='opcion preference 1', number=1)
        opt1.save()
        opt2 = QuestionOption(question=q, option='opcion preference 2', number=2)
        opt2.save()
        opt3 = QuestionOption(question=q, option='opcion preference 3', number=3)
        opt3.save()

        self.v = Voting(name='Votacion', question=q, voting_type='M')
        self.v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        self.v.auths.add(a)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v = None

    def testExist(self):
        v = Voting.objects.get(name='Votacion')
        self.assertTrue(v.question.options.count() == 3)
        self.assertEquals(v.question.options.all()[0].option, "opcion preference 1")
        self.assertEquals(v.question.options.all()[1].option, "opcion preference 2")
        self.assertEquals(v.question.options.all()[2].option, "opcion preference 3")
    
    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)
    
    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = []
        for _ in range(5):
            bag = list(range(1, len(v.question.options.all())+1))
            l = []
            n=len(v.question.options.all())-1
            for e in v.question.options.all():
                l.append(bag.pop(random.randint(0, n)))
                n-=1

            res = int(str(l).replace('[', '').replace(']', '').replace(',', '1010101').replace(' ', ''))
            a, b = self.encrypt_msg(res, v)
            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'vote': { 'a': a, 'b': b },
            }
            clear.append(l)
            user = self.get_or_create_user(voter.voter_id)
            self.login(user=user.username)
            voter = voters.pop()
            mods.post('store', json=data)
        return clear

    def testVoting(self):
        self.create_voters(self.v)

        self.v.create_pubkey()
        self.v.start_date = timezone.now()
        self.v.save()

        clear = self.store_votes(self.v)

        self.login()  # set token
        self.v.tally_votes(self.token)

        tally = self.v.tally

        for e in range(len(clear)):
            self.assertTrue(tally[e] in clear)

        for q in self.v.postproc:
            self.assertEqual(q["votes"], sum(e[q["number"]-1] for e in tally)/len(self.v.question.options.all()))

class VotingModelTestCasePreferenceInvalid(BaseTestCase):
    def setUp(self):        
        q = Question(desc='Test question')
        q.save()

        opt1 = QuestionOption(question=q, option='opcion preference 1', number=1)
        opt1.save()
        opt2 = QuestionOption(question=q, option='opcion preference 2', number=2)
        opt2.save()
        opt3 = QuestionOption(question=q, option='opcion preference 3', number=3)
        opt3.save()

        self.v = Voting(name='Votacion', question=q, voting_type='M')
        self.v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        self.v.auths.add(a)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v = None

    def testExist(self):
        v = Voting.objects.get(name='Votacion')
        self.assertTrue(v.question.options.count() == 3)
        self.assertEquals(v.question.options.all()[0].option, "opcion preference 1")
        self.assertEquals(v.question.options.all()[1].option, "opcion preference 2")
        self.assertEquals(v.question.options.all()[2].option, "opcion preference 3")
    
    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)
    
    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = []
        for _ in range(5):
            bag = [1 for _ in v.question.options.all()]
            l = []
            n=len(v.question.options.all())-1
            for e in v.question.options.all():
                l.append(bag.pop(random.randint(0, n)))
                n-=1

            res = int(str(l).replace('[', '').replace(']', '').replace(',', '1010101').replace(' ', ''))
            a, b = self.encrypt_msg(res, v)
            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'vote': { 'a': a, 'b': b },
            }
            clear.append(l)
            user = self.get_or_create_user(voter.voter_id)
            self.login(user=user.username)
            voter = voters.pop()
            mods.post('store', json=data)
        return clear

    def testVoting(self):
        self.create_voters(self.v)

        self.v.create_pubkey()
        self.v.start_date = timezone.now()
        self.v.save()

        clear = self.store_votes(self.v)

        self.login()  # set token

        self.assertRaises(Exception, self.v.tally_votes, token=self.token)
