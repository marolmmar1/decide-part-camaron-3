from django.test import TestCase
from base.tests import BaseTestCase
from selenium import webdriver
from voting.models import Voting, Question, QuestionOption
from django.conf import settings
from mixnet.models import Auth
from django.utils import timezone
from census.models import Census
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains





# Create your tests here.

class BoothTestCase(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
        
    def tearDown(self):
        self.driver.quit()
        
    def testBoothNotFound(self):
    
        response = self.client.get('/booth/10000/')
        self.assertEqual(response.status_code, 404)
    
    def testBoothRedirection(self):
        
        response = self.client.get('/booth/10000')
        self.assertEqual(response.status_code, 301)

    def wait_for_window(self, timeout = 2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()
    
    def create_voting(self):
        q1 = Question(desc='test question 1')
        q1.save()
        for i in range(5):
            opt = QuestionOption(question=q1, option='option {}'.format(i+1), number=i+2)
            opt.save()

        # Create the second question
        q2 = Question(desc='test question 2')
        q2.save()
        for i in range(3):
            opt = QuestionOption(question=q2, option='option {}'.format(i+1), number=i+1)
            opt.save()
            print(opt)
        v = Voting(name='test voting')
        v.save()
        v.questions.set([q1, q2])
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        print(v.auths.all().first().url)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def test_testselenium(self):
        self.driver.get("http://localhost:8000/admin/")
        self.driver.set_window_size(910, 880)
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("admin")
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
        self.driver.switch_to.window(self.vars["win402"])
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
        self.driver.find_element(By.CSS_SELECTOR, ".field-auths .related-widget-wrapper").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
        self.vars["win451"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win451"])
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("test auth")
        self.driver.find_element(By.ID, "id_url").click()
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000/")
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
        self.driver.find_element(By.ID, "id_voter_id").click()
        self.driver.find_element(By.ID, "id_voter_id").send_keys("1")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get("http://localhost:8000/booth/1")
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        self.vars["win5024"] = self.wait_for_window(2000)
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("admin")
        self.driver.find_element(By.ID, "password").send_keys("admin")
        self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)
        self.vars["win5024"] = self.wait_for_window(2000)
        self.driver.find_element(By.ID, "opt1_index0").click()
        self.driver.find_element(By.ID, "opt3_index1").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

    

    

    

