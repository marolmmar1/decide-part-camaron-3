import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time
import json
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
from datetime import datetime
from django.core.exceptions import ValidationError

class TestSelenium(StaticLiveServerTestCase):
  def setUp(self):
    self.driver = webdriver.Chrome()
    self.vars = {}
    options = webdriver.ChromeOptions()
    options.headless = True
    self.driver = webdriver.Chrome(options=options)

  def tearDown(self):
    self.driver.quit()
  
  def wait_for_window(self, timeout = 2):
    time.sleep(round(timeout / 1000))
    wh_now = self.driver.window_handles
    wh_then = self.vars["window_handles"]
    if len(wh_now) > len(wh_then):
      return set(wh_now).difference(set(wh_then)).pop()
  
  def test_selenium(self):
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
    self.driver.find_element(By.ID, "id_desc").send_keys("¿Ganará el Atletico de Madrid la Champions?")
    self.driver.find_element(By.CSS_SELECTOR, ".field-optionSiNo .vCheckboxLabel").click()
    self.driver.find_element(By.CSS_SELECTOR, ".field-third_option .vCheckboxLabel").click()
    self.driver.find_element(By.NAME, "_save").click()
    self.driver.switch_to.window(self.vars["root"])
    self.vars["window_handles"] = self.driver.window_handles
    self.driver.find_element(By.CSS_SELECTOR, "#add_id_auths > img").click()
    self.vars["win5929"] = self.wait_for_window(2000)
    if self.vars["win5929"] in self.driver.window_handles:
        self.driver.switch_to.window(self.vars["win5929"])
    else:
        print("La ventana no existe o ya ha sido cerrada.")
    element = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.ID, "id_url"))
    )
    element.click()
    self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
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
    self.driver.find_element(By.LINK_TEXT, "¿Ganará el Atletico de Madrid la Champions?").click()
    elementSi = self.driver.find_element(By.ID, "id_options-0-option")
    self.assertTrue(elementSi.text == "Sí")
    elementNo = self.driver.find_element(By.ID, "id_options-1-option")
    self.assertTrue(elementNo.text == "No")
    elementDepende = self.driver.find_element(By.ID, "id_options-2-option")
    self.assertTrue(elementDepende.text == "Depende")
    self.driver.find_element(By.NAME, "_save").click()


class TestSelenium1(StaticLiveServerTestCase):
  def setUp(self):
    self.driver = webdriver.Chrome()
    self.vars = {}
    options = webdriver.ChromeOptions()
    options.headless = True
    self.driver = webdriver.Chrome(options=options)
  
  def tearDown(self):
    self.driver.quit()
  
  def wait_for_window(self, timeout = 2):
    time.sleep(round(timeout / 1000))
    wh_now = self.driver.window_handles
    wh_then = self.vars["window_handles"]
    if len(wh_now) > len(wh_then):
      return set(wh_now).difference(set(wh_then)).pop()
  
  def test_selenium1(self):
    self.driver.get("http://127.0.0.1:8000/admin/login/?next=/admin/")
    self.driver.set_window_size(1050, 691)
    self.driver.find_element(By.ID, "id_username").click()
    self.driver.find_element(By.ID, "id_username").send_keys("admin")
    self.driver.find_element(By.ID, "id_username").click()
    self.driver.find_element(By.ID, "id_username").click()
    element = self.driver.find_element(By.ID, "id_username")
    actions = ActionChains(self.driver)
    actions.double_click(element).perform()
    self.driver.find_element(By.ID, "id_password").click()
    self.driver.find_element(By.ID, "id_password").send_keys("admin")
    self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
    self.driver.find_element(By.LINK_TEXT, "Votings").click()
    self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
    self.driver.find_element(By.ID, "id_name").click()
    self.driver.find_element(By.ID, "id_name").send_keys("Votacion Atleti")
    self.driver.find_element(By.ID, "id_desc").click()
    self.vars["window_handles"] = self.driver.window_handles
    self.driver.find_element(By.CSS_SELECTOR, "#add_id_question > img").click()
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
    self.driver.find_element(By.CSS_SELECTOR, ".field-third_option .vCheckboxLabel").click()
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
    self.driver.find_element(By.ID, "id_options-0-option").send_keys("Si ganara algo")
    self.driver.find_element(By.ID, "id_options-1-number").click()
    self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
    self.driver.find_element(By.ID, "id_options-1-option").click()
    self.driver.find_element(By.ID, "id_options-1-option").send_keys("Ganara una liga")
    self.driver.find_element(By.NAME, "_save").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) > .field-__str__ > a").click()
    self.driver.find_element(By.NAME, "_save").click()
    self.driver.find_element(By.LINK_TEXT, "¿Ganará algo?").click()
    elementSi = self.driver.find_element(By.ID, "id_options-0-option")
    self.assertTrue(elementSi.text == "Depende")
    elementNo = self.driver.find_element(By.ID, "id_options-1-option")
    self.assertTrue(elementNo.text == "Si ganara algo")
    elementDepende = self.driver.find_element(By.ID, "id_options-2-option")
    self.assertTrue(elementDepende.text == "Ganara una liga")
    self.driver.find_element(By.NAME, "_save").click()

 
class TestSelenium2(StaticLiveServerTestCase):
  def setUp(self):
    self.driver = webdriver.Chrome()
    self.vars = {}
    options = webdriver.ChromeOptions()
    options.headless = True
    self.driver = webdriver.Chrome(options=options)
  
  def tearDown(self):
    self.driver.quit()
  
  def wait_for_window(self, timeout = 2):
    time.sleep(round(timeout / 1000))
    wh_now = self.driver.window_handles
    wh_then = self.vars["window_handles"]
    if len(wh_now) > len(wh_then):
      return set(wh_now).difference(set(wh_then)).pop()
  
  def test_selenium2(self):
    self.driver.get("http://127.0.0.1:8000/admin/login/?next=/admin/")
    self.driver.set_window_size(1050, 691)
    self.driver.find_element(By.ID, "id_username").click()
    self.driver.find_element(By.ID, "id_username").send_keys("admin")
    self.driver.find_element(By.ID, "id_password").click()
    self.driver.find_element(By.ID, "id_password").send_keys("admin")
    self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
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
    self.driver.find_element(By.CSS_SELECTOR, "#add_id_question > img").click()
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
    self.driver.find_element(By.ID, "id_options-0-option").send_keys("Si, se irá el cholo")
    self.driver.find_element(By.ID, "id_options-1-number").click()
    self.driver.find_element(By.ID, "id_options-1-number").send_keys("3")
    self.driver.find_element(By.ID, "id_options-1-option").click()
    self.driver.find_element(By.ID, "id_options-1-option").send_keys("No, se quedará el cholo")
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
    element = WebDriverWait(self.driver, 5).until(
        EC.presence_of_element_located((By.ID, "id_url"))
    )
    self.driver.find_element(By.ID, "id_url").click()
    self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
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
    self.driver.find_element(By.CSS_SELECTOR, ".field-third_option .vCheckboxLabel").click()
    self.driver.find_element(By.NAME, "_save").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) > .field-__str__ > a").click()
    elementSegunda = self.driver.find_element(By.ID, "id_options-0-option")
    self.assertTrue(elementSegunda.text == "Si, se irá el cholo")
    elementTercera = self.driver.find_element(By.ID, "id_options-1-option")
    self.assertTrue(elementTercera.text == "No, se quedará el cholo")
    elementDepende = self.driver.find_element(By.ID, "id_options-2-option")
    self.assertTrue(elementDepende.text == "Depende")
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
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1), number=i+2)
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def test_to_string(self):
        v = self.create_voting()
        self.assertEquals(str(v),"test voting")
        self.assertEquals(str(v.question),"test question")
        self.assertEquals(str(v.question.options.all()[0]),"option 1 (2)")

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'voting_type': 'S',
            'name': 'Example',
            'desc': 'Description example',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')

    def test_update_voting_405(self):
        v = self.create_voting()
        data = {}
        self.login()
        response = self.client.post('/voting/{}/'.format(v.pk), data, format= 'json')
        self.assertEquals(response.status_code, 405)

class VotingModelTestCase(BaseTestCase):
    def setUp(self):
        q = Question(desc='Descripcion')
        q.save()
        
        opt1 = QuestionOption(question=q, option='opcion 1')
        opt1.save()
        opt1 = QuestionOption(question=q, option='opcion 2')
        opt1.save()

        self.v = Voting(name='Votacion', question=q)
        self.v.save()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v = None

    def testExist(self):
        v=Voting.objects.get(name='Votacion')
        self.assertEquals(v.question.options.all()[0].option, "opcion 1")

class LogInSuccessTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
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
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/")
        
class LogInErrorTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
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
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/p').text == 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')

    def passwordWrongLogIn(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("wrongPassword")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/p').text == 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')

class QuestionsTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
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
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/voting/question/add/")
        
        self.cleaner.find_element(By.ID, "id_desc").click()
        self.cleaner.find_element(By.ID, "id_desc").send_keys('Test')
        self.cleaner.find_element(By.ID, "id_options-0-number").click()
        self.cleaner.find_element(By.ID, "id_options-0-number").send_keys('1')
        self.cleaner.find_element(By.ID, "id_options-0-option").click()
        self.cleaner.find_element(By.ID, "id_options-0-option").send_keys('test1')
        self.cleaner.find_element(By.ID, "id_options-1-number").click()
        self.cleaner.find_element(By.ID, "id_options-1-number").send_keys('2')
        self.cleaner.find_element(By.ID, "id_options-1-option").click()
        self.cleaner.find_element(By.ID, "id_options-1-option").send_keys('test2')
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/voting/question/")

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/voting/question/add/")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/voting/question/add/")

class VotingModelTestCaseOptionSiNo(BaseTestCase):
    def setUp(self):
        q = Question(desc='Test question', optionSiNo=True)
        q.save()

        self.v = Voting(name='Votacion', question=q)
        self.v.save()

        super().setUp()
    def tearDown(self):
        super().tearDown()
        self.v = None

    def testExist(self):
        v = Voting.objects.get(name='Votacion')
        self.assertTrue(v.question.options.count() == 2)
        self.assertEquals(v.question.options.all()[0].option, "Sí")
        self.assertEquals(v.question.options.all()[1].option, "No")
    
    def test_cannot_add_more_options(self):
        with self.assertRaises(ValidationError):
            new_option = QuestionOption(question=self.v.question, number=3, option="Maybe")
            new_option.save()
    def test_cannot_delete_predefined_options(self):
        initial_option_count = self.v.question.options.count()

        yes_option = self.v.question.options.get(option="Sí")
        with self.assertRaises(ValidationError):
            yes_option.delete()

        final_option_count = self.v.question.options.count()
        self.assertEqual(initial_option_count, final_option_count)

    def test_cannot_edit_predefined_options(self):
        yes_option = self.v.question.options.get(option="Sí")
        with self.assertRaises(ValidationError):
            yes_option.option = "Maybe"
            yes_option.save()

    def test_can_change_options_to_depends(self):
        self.v.question.optionSiNo = False
        self.v.question.third_option = True
        self.v.question.save()

        options = self.v.question.options.values_list('option', flat=True)
        self.assertIn("Depende", options)

    def test_cannot_add_more_than_three_options(self):
        self.v.question.third_option = True
        self.v.question.save()

        with self.assertRaises(ValidationError):
            new_option = QuestionOption(question=self.v.question, number=4, option="Maybe")
            new_option.save()

    def test_can_add_third_option(self):
        self.v.question.third_option = True
        self.v.question.save()

        new_option = QuestionOption(question=self.v.question, number=3, option="Depende")
        new_option.save()

        options = self.v.question.options.values_list('option', flat=True)
        self.assertIn("Depende", options)

class VotingModelTestCaseThirdOption(TestCase):
    def setUp(self):
        self.v = Voting(name='Test Voting')
        self.q = Question(desc='Test question')
        self.q.save()
        self.v.question_id = self.q.id
        self.v.save()
        self.opt1 = QuestionOption(question=self.q, number=1, option='Yes')
        self.opt1.save()
        self.opt2 = QuestionOption(question=self.q, number=2, option='No')
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
