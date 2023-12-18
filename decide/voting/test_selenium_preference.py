from base.tests import BaseTestCase
from voting.models import Voting
from django.contrib.auth.models import User
from base import mods
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APIClient
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


class VotingPreferenceTestCaseSelenium(StaticLiveServerTestCase):
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

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()


class VotingPreferenceTestCaseSeleniumSuccess(StaticLiveServerTestCase):
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

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()


class VotingPreferenceTestCaseSeleniumFail(StaticLiveServerTestCase):
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

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    def test_boothVoting(self):
        user = User.objects.get(username="admin1")

        self.driver.get(f'{self.live_server_url+"/admin/login/?next=/admin/"}')
        self.driver.find_element(By.ID, "id_username").send_keys("admin1")
        self.driver.find_element(By.ID, "id_password").send_keys("admin1")
        self.driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()

        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        dropdown = self.driver.find_element(By.ID, "id_voting_type")
        dropdown.find_element(By.XPATH, "//option[. = 'Multiple Choice']").click()
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
        self.driver.find_element(By.ID, "id_name").send_keys("Votacion 1")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Esto es una votacion")
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_questions > img").click()
        self.vars["win9215"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win9215"])
        self.driver.find_element(By.ID, "id_desc").send_keys("Esto es una pregunta")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("Opcion 1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("Opcion 2")
        self.driver.find_element(By.ID, "id_options-2-number").click()
        self.driver.find_element(By.ID, "id_options-2-number").send_keys("3")
        self.driver.find_element(By.ID, "id_options-2-option").click()
        self.driver.find_element(By.ID, "id_options-2-option").send_keys(" Opcion 3")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()

        self.vars["win1617"] = self.wait_for_window(5000)
        self.driver.switch_to.window(self.vars["win1617"])

        self.driver.find_element(By.ID, "id_name").send_keys(self.live_server_url + "/")
        self.driver.find_element(By.ID, "id_url").send_keys(self.live_server_url + "/")

        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.NAME, "_save").click()
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
        self.driver.find_element(By.CSS_SELECTOR, ".model-census .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys("1")
        self.driver.find_element(By.ID, "id_voter_id").send_keys(user.pk)
        self.driver.find_element(By.NAME, "_save").click()

        voting = Voting.objects.get(name="Votacion 1")
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
        self.driver.find_element(By.ID, "username").send_keys("admin1")
        self.driver.find_element(By.ID, "password").send_keys("admin1")
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        time.sleep(3)

        self.driver.find_element(By.ID, "option-1").send_keys("1")
        self.driver.find_element(By.ID, "option-2").send_keys("1")
        self.driver.find_element(By.ID, "option-3").send_keys("1")

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        time.sleep(5)
        self.assertTrue(
            self.driver.find_element(
                By.XPATH, "//div[contains(text(), 'Order of options not valid')]"
            )
            != None
        )

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
