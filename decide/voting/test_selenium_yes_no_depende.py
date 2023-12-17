from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APIClient

from selenium import webdriver
from selenium.webdriver.common.by import By

import time
from selenium.webdriver.common.action_chains import ActionChains

from base import mods
from base.tests import BaseTestCase


class TestSelenium(StaticLiveServerTestCase):
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


class TestSelenium1(StaticLiveServerTestCase):
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

    def test_selenium1(self):
        user = User.objects.get(username="admin1")
        self.driver.get(f'{self.live_server_url+"/admin/login/?next=/admin/"}')
        self.driver.find_element(By.ID, "id_username").send_keys("admin1")
        self.driver.find_element(By.ID, "id_password").send_keys("admin1")
        self.driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Votacion Atleti")
        self.driver.find_element(By.ID, "id_desc").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_questions > img").click()
        self.vars["win7257"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win7257"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("¿Ganará algo?")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win2483"] = self.wait_for_window(2000)
        if self.vars["win2483"] in self.driver.window_handles:
            self.driver.switch_to.window(self.vars["win2483"])
        else:
            print("La ventana no existe o ya ha sido cerrada.")
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("url")
        self.driver.find_element(By.ID, "id_url").click()
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.ID, "content").click()
        self.driver.find_element(By.LINK_TEXT, "¿Ganará algo?").click()
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option .vCheckboxLabel"
        ).click()
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        element = self.driver.find_element(By.ID, "id_options-0-option")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_options-0-option")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_options-0-option")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys(
            "Si ganara algo"
        )
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys(
            "Ganara una liga"
        )
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "tr:nth-child(1) > .field-__str__ > a"
        ).click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "¿Ganará algo?").click()
        elementSi = self.driver.find_element(By.ID, "id_options-0-option")
        self.assertTrue(elementSi.text == "Depende")
        elementNo = self.driver.find_element(By.ID, "id_options-1-option")
        self.assertTrue(elementNo.text == "Si ganara algo")
        elementDepende = self.driver.find_element(By.ID, "id_options-2-option")
        self.assertTrue(elementDepende.text == "Ganara una liga")
        self.driver.find_element(By.NAME, "_save").click()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()


class TestSelenium2(StaticLiveServerTestCase):
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

    def test_selenium2(self):
        user = User.objects.get(username="admin1")
        self.driver.get(f'{self.live_server_url+"/admin/login/?next=/admin/"}')
        self.driver.find_element(By.ID, "id_username").send_keys("admin1")
        self.driver.find_element(By.ID, "id_password").send_keys("admin1")
        self.driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
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
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_questions > img").click()
        self.vars["win8675"] = self.wait_for_window(2000)
        self.vars["root"] = self.driver.current_window_handle
        self.driver.switch_to.window(self.vars["win8675"])
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("¿Cambiará de entrenador?")
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("0")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        element = self.driver.find_element(By.ID, "id_options-0-number")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_options-0-number")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_options-0-number")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys(
            "Si, se irá el cholo"
        )
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("3")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys(
            "No, se quedará el cholo"
        )
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win942"] = self.wait_for_window(2000)
        if self.vars["win942"] in self.driver.window_handles:
            self.driver.switch_to.window(self.vars["win942"])
        else:
            print("La ventana no existe o ya ha sido cerrada.")
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("url")
        self.driver.find_element(By.ID, "id_url").click()
        self.driver.find_element(By.ID, "id_url").send_keys(self.live_server_url + "/")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.switch_to.window(self.vars["root"])
        self.driver.find_element(By.NAME, "_save").click()
        element = self.driver.find_element(By.ID, "nav-sidebar")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "nav-sidebar")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "nav-sidebar")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "¿Cambiará de entrenador?").click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".field-third_option .vCheckboxLabel"
        ).click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "tr:nth-child(1) > .field-__str__ > a"
        ).click()
        elementSegunda = self.driver.find_element(By.ID, "id_options-0-option")
        self.assertTrue(elementSegunda.text == "Si, se irá el cholo")
        elementTercera = self.driver.find_element(By.ID, "id_options-1-option")
        self.assertTrue(elementTercera.text == "No, se quedará el cholo")
        elementDepende = self.driver.find_element(By.ID, "id_options-2-option")
        self.assertTrue(elementDepende.text == "Depende")
        self.driver.find_element(By.NAME, "_save").click()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
