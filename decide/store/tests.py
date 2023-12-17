import datetime
import random
import subprocess
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Vote
from base.tests import BaseTestCase
from census.models import Census
from voting.models import Question
from voting.models import Voting

from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path
from .consumers import VoteConsumer
from channels.layers import get_channel_layer
from django.conf import settings
from django.test import Client
import os
from django.db import transaction
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path
from .consumers import VoteConsumer
from channels.layers import get_channel_layer
from django.conf import settings
from django.test import Client
import os
from django.db import transaction

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.support.ui import Select

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.support.ui import Select


class StoreTextCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.question = Question(desc="qwerty")
        self.question.save()
        self.question2 = Question(desc="qwerty")
        self.question2.save()
        self.voting = Voting(
            pk=5001,
            name="voting example",
            start_date=timezone.now(),
        )
        self.voting.save()
        self.voting.questions.add(self.question)
        self.voting.questions.add(self.question2)

    def tearDown(self):
        super().tearDown()

    def gen_voting(self, pk, question_desc=None):
        voting = Voting(
            pk=pk,
            name="v1",
            start_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(days=1),
        )
        voting.save()

        if question_desc:
            question = Question(desc=question_desc)
            question.save()
            voting.questions.add(question)

        return voting

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = "user{}".format(pk)
        user.set_password("qwerty")
        user.save()
        return user

    def gen_votes(self):
        votings = [random.randint(1, 5000) for _ in range(10)]
        users = [random.randint(4, 5003) for _ in range(50)]
        for v in votings:
            a = random.randint(2, 500)
            b = random.randint(2, 500)
            self.gen_voting(v)
            random_user = random.choice(users)
            user = self.get_or_create_user(random_user)
            self.login(user=user.username)
            census = Census(voting_id=v, voter_id=random_user)
            census.save()
            data = {"voting": v, "voter": random_user, "vote": {"a": a, "b": b}}
            response = self.client.post("/store/", data, format="json")
            self.assertEqual(response.status_code, 200)

        self.logout()
        return votings, users

    def gen_vote_for_one_user(self):
        votings = [random.randint(1, 5000) for i in range(10)]
        u = 3
        a = random.randint(2, 500)
        b = random.randint(2, 500)
        random_voting = random.choice(votings)
        self.gen_voting(random_voting)
        user = self.get_or_create_user(u)
        self.login(user=user.username)
        census = Census(voting_id=random_voting, voter_id=u)
        census.save()
        data = {"voting": random_voting, "voter": u, "vote": {"a": a, "b": b}}
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.logout()
        return u

    def gen_many_votes_for_one_user(self):
        votings = [random.randint(1, 5000) for i in range(10)]
        users = [random.randint(4, 5003) for i in range(50)]
        random_user = random.choice(users)
        for v in votings:
            a = random.randint(2, 500)
            b = random.randint(2, 500)
            self.gen_voting(v)
            user = self.get_or_create_user(random_user)
            self.login(user=user.username)
            census = Census(voting_id=v, voter_id=random_user)
            census.save()
            data = {"voting": v, "voter": random_user, "vote": {"a": a, "b": b}}
            response = self.client.post("/store/", data, format="json")
            self.assertEqual(response.status_code, 400)

        self.logout()
        return random_user

    def test_gen_vote_invalid(self):
        data = {"voting": 1, "voter": 1, "vote": {"a": 1, "b": 1}}
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_store_vote(self):
        VOTING_PK = 345
        CTE_A = 96
        CTE_B = 184
        census = Census(voting_id=VOTING_PK, voter_id=1)
        census.save()
        self.gen_voting(VOTING_PK)
        votes = [{"vote": {"a": CTE_A, "b": CTE_B}}]
        data = {
            "voting": VOTING_PK,
            "voter": 1,
            "votes": votes,
            "voting_type": "classic",
        }

        user = self.get_or_create_user(1)
        self.login(user=user.username)
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, VOTING_PK)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().b, CTE_B)

    def test_voting_status(self):
        votes = [{"vote": {"a": 30, "b": 55}}]
        data = {"voting": 5001, "voter": 1, "votes": votes}
        census = Census(voting_id=5001, voter_id=1)
        census.save()

        self.voting.start_date = timezone.now() + datetime.timedelta(days=1)
        self.voting.save()
        user = self.get_or_create_user(1)
        self.login(user=user.username)
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 401)

        self.voting.start_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        self.voting.end_date = timezone.now() + datetime.timedelta(days=1)
        self.voting.save()
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 200)

        self.voting.end_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_store_vote_two_questions(self):
        VOTING_PK = 345
        CTE_A = 96
        CTE_B = 184
        census = Census(voting_id=VOTING_PK, voter_id=1)
        census.save()
        voting = self.gen_voting(VOTING_PK, question_desc="Question 1")
        question2 = Question(desc="Question 2")
        question2.save()
        voting.questions.add(question2)

        votes = [{"vote": {"a": CTE_A, "b": CTE_B}}]
        data = {
            "voting": VOTING_PK,
            "voter": 1,
            "votes": votes,
            "voting_type": "classic",
        }

        user = self.get_or_create_user(1)
        self.login(user=user.username)
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, VOTING_PK)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().b, CTE_B)

        self.assertEqual(voting.questions.count(), 2)
        self.assertEqual(voting.questions.first().desc, "Question 1")
        self.assertEqual(voting.questions.last().desc, "Question 2")

    def test_invalid_data(self):
        data = {"voting": 9999, "voter": 9999, "votes": [{"vote": {"a": 1, "b": 1}}]}
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_vote_outside_voting_period(self):
        voting = self.gen_voting(1)
        voting.start_date = timezone.now() + datetime.timedelta(days=1)
        voting.end_date = timezone.now() + datetime.timedelta(days=2)
        voting.save()
        data = {"voting": 1, "voter": 1, "votes": [{"vote": {"a": 1, "b": 1}}]}
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_vote_history_not_registered(self):
        response = self.client.get("/store/voteHistory/")
        self.assertEqual(response.status_code, 401)

    def test_vote_history_no_votes(self):
        self.login(user="admin")
        response = self.client.get("/store/voteHistory/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("votes", response.context)
        history = response.context["votes"]
        self.assertListEqual(list(history), [])

    def test_vote_history_one_vote(self):
        u = self.gen_vote_for_one_user()
        user = self.get_or_create_user(u)
        self.login(user=user.username)
        response = self.client.get("/store/voteHistory/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("votes", response.context)
        history = response.context["votes"]
        self.assertEqual(len(history), 0)

    def test_vote_history_many_votes(self):
        random_user = self.gen_many_votes_for_one_user()
        user = self.get_or_create_user(random_user)
        self.login(user=user.username)
        response = self.client.get("/store/voteHistory/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("votes", response.context)
        history = response.context["votes"]
        self.assertEqual(len(history), Vote.objects.filter(voter_id=user.id).count())
        for i, vote in enumerate(history):
            self.assertEqual(
                vote, Vote.objects.filter(voter_id=user.id).order_by("-voted")[i]
            )


class RealTimeDataTestCase(TestCase):
    def setUp(self):
        super().setUp()
        # Crea una pregunta y una votación
        question = Question.objects.create(desc="Test Question")
        self.voting = Voting.objects.create(name="Test Voting")
        self.voting.save()
        self.voting.questions.set([question])
        self.voting.save()

    def tearDown(self):
        super().tearDown()

    async def test_vote_consumer_connection(self):
        # Define la ruta del WebSocket para el consumidor de votos
        application = URLRouter(
            [
                re_path(r"ws/votes/$", VoteConsumer.as_asgi()),
            ]
        )

        # Crea un comunicador WebSocket para la ruta del consumidor de votos
        communicator = WebsocketCommunicator(application, "ws/votes/")

        # Intenta conectar al WebSocket
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Desconecta
        await communicator.disconnect()
        self.assertTrue(connected)

    async def test_vote_consumer_message_djangoChannels(self):
        application = URLRouter(
            [
                re_path(r"ws/votes/$", VoteConsumer.as_asgi()),
            ]
        )

        communicator = WebsocketCommunicator(application, "ws/votes/")

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "votes",
            {
                "type": "vote.added",
                "vote_id": self.voting.id,
            },
        )

        response = await communicator.receive_json_from()

        self.assertEqual(
            response,
            {
                "message": "Vote received",
                "vote_id": self.voting.id,
                "vote_count": 0,
                "vote_percentage": 0.0,
            },
        )

        await communicator.disconnect()

    async def test_vote_consumer_message_websocket(self):
        application = URLRouter(
            [
                re_path(r"ws/votes/$", VoteConsumer.as_asgi()),
            ]
        )

        communicator = WebsocketCommunicator(application, "ws/votes/")

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                "type": "vote.added",
                "vote_id": self.voting.id,
            },
        )

        response = await communicator.receive_json_from()

        self.assertEqual(response["message"], "Vote received")
        self.assertEqual(response["vote_id"], self.voting.id)

        await communicator.send_json_to(
            {
                "type": "voting.open",
                "voting_id": self.voting.id,
            },
        )

        response = await communicator.receive_json_from()

        self.assertEqual(response["message"], "Voting open")
        self.assertEqual(response["voting_id"], self.voting.id)

        await communicator.send_json_to(
            {
                "type": "voting.closed",
                "voting_id": self.voting.id,
            },
        )

        response = await communicator.receive_json_from()

        self.assertEqual(response["message"], "Voting closed")
        self.assertEqual(response["voting_id"], self.voting.id)

        await communicator.disconnect()


class BackupTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(settings.DATABASE_BACKUP_DIR):
            os.makedirs(settings.DATABASE_BACKUP_DIR)
        backup_savestate = "testsave.psql.bin"
        backup_files = list(os.listdir(settings.DATABASE_BACKUP_DIR))

        if backup_savestate in backup_files:
            os.remove(os.path.join(settings.DATABASE_BACKUP_DIR, backup_savestate))

        command = f"python manage.py dbbackup -o {backup_savestate}"
        subprocess.run(command, shell=True, check=True)
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        backup_savestate = "testsave.psql.bin"
        subprocess.run(
            ["python", "manage.py", "dbrestore", "--noinput", "-i", backup_savestate],
            check=True,
        )

        backup_files = list(os.listdir(settings.DATABASE_BACKUP_DIR))
        for file in backup_files:
            if "test" in file:
                os.remove(os.path.join(settings.DATABASE_BACKUP_DIR, file))

        return super().tearDownClass()

    def setUp(self):
        self.client = Client()
        super().setUp()

    def tearDown(self):
        super().tearDown()

    @transaction.atomic
    def test_backup_file_is_created(self):
        try:
            backup_files = list(os.listdir(settings.DATABASE_BACKUP_DIR))
            initial_backup_count = len(backup_files)
            self.client.get("/store/vote/create_backup/", format="json")
            new_backup_files = list(os.listdir(settings.DATABASE_BACKUP_DIR))
            updated_backup_count = len(new_backup_files)

            self.assertEqual(
                updated_backup_count,
                initial_backup_count + 1,
                "No new backup file created.",
            )

            # deletes the new created backup file
            for file in new_backup_files:
                if file not in backup_files:
                    os.remove(os.path.join(settings.DATABASE_BACKUP_DIR, file))
                    break
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    @transaction.atomic
    def test_backup_file_is_created_with_name(self):
        try:
            backup_name = "test"
            self.client.post(f"/store/vote/create_backup/{backup_name}/", format="json")
            self.assertTrue(
                os.path.exists(
                    os.path.join(
                        settings.DATABASE_BACKUP_DIR, f"{backup_name}.psql.bin"
                    )
                ),
                "Backup file to restore not found",
            )
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    @transaction.atomic
    def test_list_backup_page(self):
        url = reverse("store:vote_restore_backup_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list_backups.html")

    @transaction.atomic
    def test_backup_file_is_restored(self):
        try:
            backup_name = "test"
            self.client.get(f"/store/vote/create_backup/{backup_name}/", format="json")
            self.assertTrue(
                os.path.exists(
                    os.path.join(
                        settings.DATABASE_BACKUP_DIR, f"{backup_name}.psql.bin"
                    )
                ),
                "Backup file to restore not found",
            )

            restore_url = reverse("store:vote_restore_backup")
            response = self.client.post(
                restore_url, {"selected_backup": f"{backup_name}.psql.bin"}
            )
            self.assertEqual(response.status_code, 302)

        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    @transaction.atomic
    def test_backup_file_not_found_in_restore(self):
        inexistent_backup_name = "non_existing_backup"

        restore_url = reverse("store:vote_restore_backup")
        response = self.client.post(
            restore_url, {"selected_backup": f"{inexistent_backup_name}.psql.bin"}
        )
        self.assertEqual(response.status_code, 400)  # bad request

    @transaction.atomic
    def test_delete_backup(self):
        try:
            backup_name = "test"
            self.client.get(f"/store/vote/create_backup/{backup_name}/", format="json")
            self.assertTrue(
                os.path.exists(
                    os.path.join(
                        settings.DATABASE_BACKUP_DIR, f"{backup_name}.psql.bin"
                    )
                ),
                "Backup file to delete not found",
            )

            delete_url = reverse(
                "store:delete_backup",
                kwargs={"selected_backup": f"{backup_name}.psql.bin"},
            )
            response = self.client.post(
                delete_url, {"selected_backup": f"{backup_name}.psql.bin"}
            )

            self.assertEqual(response.status_code, 302)

            self.assertNotIn(
                f"{backup_name}.psql.bin", os.listdir(settings.DATABASE_BACKUP_DIR)
            )

        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    @transaction.atomic
    def test_backup_file_not_found_in_delete(self):
        inexistent_backup_name = "non_existing_backup"

        delete_url = reverse(
            "store:delete_backup",
            kwargs={"selected_backup": f"{inexistent_backup_name}.psql.bin"},
        )
        response = self.client.post(
            delete_url, {"selected_backup": f"{inexistent_backup_name}.psql.bin"}
        )
        self.assertEqual(response.status_code, 400)  # bad request


class DashboardTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        self.userlog = User.objects.create_superuser(
            "adminprueba", "admin@example.com", "1111"
        )
        self.user = User.objects.create_superuser("prueba", "p@example.com", "1111")
        question = Question.objects.create(desc="Test Question")
        self.voting = Voting.objects.create(name="Test Voting")
        self.voting.save()
        self.voting.questions.set([question])
        self.voting.save()
        self.census1 = Census(voting_id=self.voting.id, voter_id=self.user.id)
        self.census1.save()
        self.census2 = Census(voting_id=self.voting.id, voter_id=self.userlog.id)
        self.census2.save()

        self.driver = webdriver.Chrome()
        self.vars = {}

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def test_elementos_dashboard(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").send_keys("adminprueba")
        self.driver.find_element(By.ID, "id_password").send_keys("1111")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        # Hacer votacion activa
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        select_element = self.driver.find_element(By.NAME, "action")
        select = Select(select_element)
        select.select_by_value("start")
        self.driver.find_elements(By.CLASS_NAME, "action-select")[0].click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.LINK_TEXT, "Votes").click()

        # Hacer voto
        self.driver.find_element(By.LINK_TEXT, "Votes").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys(str(self.voting.id))
        self.driver.find_element(By.ID, "id_voter_id").click()
        self.driver.find_element(By.ID, "id_voter_id").send_keys(str(self.user.id))
        self.driver.find_element(By.ID, "id_a").click()
        self.driver.find_element(By.ID, "id_a").send_keys("1")
        self.driver.find_element(By.ID, "id_b").click()
        self.driver.find_element(By.ID, "id_b").send_keys("1")
        self.driver.find_element(By.NAME, "_save").click()

        # Nombre votacion
        nombre = self.driver.find_element(
            By.ID, "vote-name-" + str(self.voting.id)
        ).text
        self.assertEqual(nombre, "Name: " + self.voting.name)

        # Comprueba que se refleja en el dashboard correctamente
        fechaInicio = self.driver.find_element(
            By.ID, "start-date-" + str(self.voting.id)
        ).text
        self.assertTrue(fechaInicio != "Started: None")
        fechaFin = self.driver.find_element(
            By.ID, "end-date-" + str(self.voting.id)
        ).text
        self.assertEqual(fechaFin, "Finished: None")

        # Hacer votacion parada
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        select_element = self.driver.find_element(By.NAME, "action")
        select = Select(select_element)
        select.select_by_value("stop")
        self.driver.find_elements(By.CLASS_NAME, "action-select")[0].click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.LINK_TEXT, "Votes").click()

        # Comprueba que se cambian los datos
        fechaInicio = self.driver.find_element(
            By.ID, "start-date-" + str(self.voting.id)
        ).text
        self.assertTrue(fechaInicio != "Started: None")
        fechaFin = self.driver.find_element(
            By.ID, "end-date-" + str(self.voting.id)
        ).text
        self.assertTrue(fechaFin != "Finished: None")

    def test_funciones_dashboard(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").send_keys("adminprueba")
        self.driver.find_element(By.ID, "id_password").send_keys("1111")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        # Hacer votacion activa
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        select_element = self.driver.find_element(By.NAME, "action")
        select = Select(select_element)
        select.select_by_value("start")
        self.driver.find_elements(By.CLASS_NAME, "action-select")[0].click()
        self.driver.find_element(By.NAME, "index").click()

        # Hacer voto
        self.driver.find_element(By.LINK_TEXT, "Votes").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys(str(self.voting.id))
        self.driver.find_element(By.ID, "id_voter_id").click()
        self.driver.find_element(By.ID, "id_voter_id").send_keys(str(self.user.id))
        self.driver.find_element(By.ID, "id_a").click()
        self.driver.find_element(By.ID, "id_a").send_keys("1")
        self.driver.find_element(By.ID, "id_b").click()
        self.driver.find_element(By.ID, "id_b").send_keys("1")
        self.driver.find_element(By.NAME, "_save").click()

        # Comprueba que se refleja en el dashboard correctamente
        contador = self.driver.find_element(
            By.ID, "vote-count-" + str(self.voting.id)
        ).text
        self.assertEqual(contador, "Number of votes: 1")
        pctge = self.driver.find_element(
            By.ID, "vote-percentage-" + str(self.voting.id)
        ).text
        self.assertEqual(pctge, "Percentage: 50.00%")

        # Hacer otro
        self.driver.find_element(By.LINK_TEXT, "Votes").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_voting_id").send_keys(str(self.voting.id))
        self.driver.find_element(By.ID, "id_voter_id").click()
        self.driver.find_element(By.ID, "id_voter_id").send_keys(str(self.userlog.id))
        self.driver.find_element(By.ID, "id_a").click()
        self.driver.find_element(By.ID, "id_a").send_keys("1")
        self.driver.find_element(By.ID, "id_b").click()
        self.driver.find_element(By.ID, "id_b").send_keys("1")
        self.driver.find_element(By.NAME, "_save").click()

        # Comprueba que el dashboard se actualiza correctamente
        contador = self.driver.find_element(
            By.ID, "vote-count-" + str(self.voting.id)
        ).text
        self.assertEqual(contador, "Number of votes: 2")
        pctge = self.driver.find_element(
            By.ID, "vote-percentage-" + str(self.voting.id)
        ).text
        self.assertEqual(pctge, "Percentage: 100.00%")
