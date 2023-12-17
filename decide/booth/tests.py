from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APIClient
from base import mods
import time
from voting.models import Voting, Question, QuestionOption, Auth
from base.tests import BaseTestCase
from selenium import webdriver
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from base.tests import BaseTestCase
from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from django.conf import settings
from census.models import Census
import time

import time


class BoothTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.client = APIClient()
        self.base = BaseTestCase()
        self.base.setUp()
        self.vars = {}
        mods.mock_query(self.client)

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        u = User(username="admin1")
        u.set_password("admin1")
        u.is_staff = True
        u.is_superuser = True
        u.save()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def testBoothNotFound(self):
        response = self.client.get("/booth/10000/")
        self.assertEqual(response.status_code, 404)

    def testBoothRedirection(self):
        response = self.client.get("/booth/10000")
        self.assertEqual(response.status_code, 301)

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

        ### SELENIUM TESTS

    def test_selenium_vote_multiple_questions_not_started(self):
        self.driver.get(f'{self.live_server_url+"/admin/login/?next=/admin/"}')
        self.driver.set_window_size(910, 880)
        self.driver.find_element(By.ID, "id_username").send_keys("admin1")
        self.driver.find_element(By.ID, "id_password").send_keys("admin1")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("test voting")
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_questions > img").click()
        self.vars["win5024"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win5024"])
        self.driver.find_element(By.ID, "id_desc").send_keys("test question 1")
        self.driver.find_element(By.ID, "id_optionSiNo").click()
        self.driver.find_element(By.NAME, "_save").click()

        self.driver.switch_to.window(self.vars["root"])
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_questions > img").click()
        self.vars["win402"] = self.wait_for_window(2000)
        if self.vars["win402"] in self.driver.window_handles:
            self.driver.switch_to.window(self.vars["win402"])
        else:
            print("La ventana no existe o ya ha sido cerrada.")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("test question 2")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-2-number").click()
        self.driver.find_element(By.ID, "id_options-2-number").send_keys("3")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("A")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("B")
        self.driver.find_element(By.ID, "id_options-2-option").click()
        self.driver.find_element(By.ID, "id_options-2-option").send_keys("C")
        element = self.driver.find_element(By.NAME, "_save")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "_save")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "_save")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-auths .related-widget-wrapper"
        ).click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win451"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win451"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("test auth")
        self.driver.find_element(By.ID, "id_url").click()
        self.driver.find_element(By.ID, "id_url").send_keys(self.live_server_url + "/")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-census .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys("1")
        self.driver.find_element(By.ID, "id_voter_id").click()
        self.driver.find_element(By.ID, "id_voter_id").send_keys("1")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(self.live_server_url + "/booth/1")
        self.assertTrue(self.live_server_url + "/booth/1/" == self.driver.current_url)
        self.assertTrue(
            self.driver.find_element(By.CSS_SELECTOR, "h1").text == "Not Found"
        )


class BoothTestCaseSelenium(StaticLiveServerTestCase):
    def setUp(self):
        self.client = APIClient()
        self.base = BaseTestCase()
        self.base.setUp()
        self.vars = {}

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        # Create questions
        q = Question(desc="test question")
        q.save()

        for i in range(5):
            opt = QuestionOption(question=q, number=i, option="option {}".format(i + 1))
            opt.save()
        # Create voting and add the questions to it
        v = Voting(name="test voting")
        v.save()
        v.questions.add(q)
        au = Auth(name="test auth", url=self.live_server_url, me=True)
        au.save()
        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL,
            defaults={"me": True, "url": self.live_server_url, "name": "me"},
        )
        a.save()
        v.auths.add(au)

        # Create user
        u = User(username="voter1")
        u.set_password("decidepass123")
        u.is_staff = True
        u.is_superuser = True
        u.save()

    def test_booth_login_fail(self):
        voting = Voting.objects.get(name="test voting")
        user = User.objects.get(username="voter1")

        census = Census(voting_id=voting.pk, voter_id=user.pk)
        census.save()

        self.driver.get(f'{self.live_server_url+"/admin/login/?next=/admin/"}')
        self.driver.find_element(By.ID, "id_username").send_keys("voter1")
        self.driver.find_element(By.ID, "id_password").send_keys("decidepass123")
        self.driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()
        self.driver.get(self.live_server_url + "/admin/voting/voting/")
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "index").click()

        self.driver.get(f'{self.live_server_url+"/booth/"+voting.id.__str__()}')
        element = self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary")

        navbar_toggler = self.driver.find_element(By.CLASS_NAME, "navbar-toggler")
        navbar_toggler.click()
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()

        element = self.driver.find_element(By.CSS_SELECTOR, "body")
        actions = ActionChains(self.driver)

        time.sleep(1)
        self.driver.find_element(By.ID, "username").click()
        time.sleep(1)
        self.driver.find_element(By.ID, "username").send_keys("voter1")
        self.driver.find_element(By.ID, "password").send_keys("decidepass1234")
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        time.sleep(5)
        self.assertTrue(
            self.driver.find_element(By.CSS_SELECTOR, ".alert").text
            == "Error: Bad Request"
        )

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
