from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from voting.models import Voting, Question

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class AdminTestCase(StaticLiveServerTestCase):
    def setUp(self):
        # Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()

        # Opciones de Chrome
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

    def test_simpleCorrectLogin(self):
        # Abre la ruta del navegador
        self.driver.get(f"{self.live_server_url}/admin/")
        # Busca los elementos y “escribe”
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty", Keys.ENTER)

        # Verifica que nos hemos logado porque aparece la barra de herramientas superior
        self.assertTrue(len(self.driver.find_elements(By.ID, "user-tools")) == 1)

    def test_simpleWrongLogin(self):
        self.driver.get(f"{self.live_server_url}/admin/")
        self.driver.find_element(By.ID, "id_username").send_keys("WRONG")
        self.driver.find_element(By.ID, "id_password").send_keys("WRONG")
        self.driver.find_element(By.ID, "login-form").submit()

        # Si no, aparece este error
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "errornote")) == 1)
        time.sleep(5)


class VisualizerTestCase(StaticLiveServerTestCase):
    def setUp(self):
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

    def test_simpleVisualizer(self):
        q = Question(desc="test question")
        q.save()
        v = Voting(name="test voting")
        v.save()
        v.questions.add(q)
        v.save()
        self.driver.get(f"{self.live_server_url}/visualizer/{v.pk}/")
        vState = self.driver.find_element(By.TAG_NAME, "h2").text
        self.assertTrue(vState, "Votación no comenzada")
