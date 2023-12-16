from django.test import TestCase
from base.tests import BaseTestCase
from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from django.conf import settings
from census.models import Census
from django.contrib.auth.models import User
from base import mods
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APIClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


# Create your tests here.

class BoothTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
    def tearDown(self):
        super().tearDown()
    def testBoothNotFound(self):
        
        # Se va a probar con el numero 10000 pues en las condiciones actuales en las que nos encontramos no parece posible que se generen 10000 votaciones diferentes
        response = self.client.get('/booth/10000/')
        self.assertEqual(response.status_code, 404)
    
    def testBoothRedirection(self):
        
        # Se va a probar con el numero 10000 pues en las condiciones actuales en las que nos encontramos no parece posible que se genren 10000 votaciones diferentes
        response = self.client.get('/booth/10000')
        self.assertEqual(response.status_code, 301)

class BoothTestCaseSelenium(StaticLiveServerTestCase):
   
    def setUp(self):
        self.client = APIClient()
        self.base = BaseTestCase()  
        self.base.setUp()
        self.vars={}
        
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        #Create questions
        q = Question(desc='test question')
        q.save()
        
        for i in range(5):
            opt = QuestionOption(question=q, number=i, option='option {}'.format(i+1))
            opt.save()
        #Create voting and add the questions to it
        v = Voting(name='test voting', question=q)
        v.save()
        au = Auth(name='test auth', url=self.live_server_url, me=True)
        au.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'url':self.live_server_url, 'name': 'me'})
        a.save()
        v.auths.add(au)

        #Create user
        u = User(username='voter1')
        u.set_password('decidepass123')
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
        self.driver.get(self.live_server_url+'/admin/voting/voting/')
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
        
        navbar_toggler = self.driver.find_element(By.CLASS_NAME, 'navbar-toggler')
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
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "Error: Bad Request")

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()