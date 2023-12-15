import datetime
import random
import subprocess
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Vote
from .serializers import VoteSerializer
from base.tests import BaseTestCase
from census.models import Census
from voting.models import Question
from voting.models import Voting

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
from rest_framework.authtoken.models import Token


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

    def gen_votes(self):
        votings = [self.gen_voting(pk=random.randint(1, 5000)) for _ in range(5)]
        users = [self.get_or_create_user(pk=random.randint(3, 5002)) for _ in range(50)]

        for voting in votings:
            random_user = random.choice(users)
            votes = []
            census = Census(voting_id=voting.id, voter_id=random_user.id)
            census.save()
            a = random.randint(2, 500)
            b = random.randint(2, 500)
            votes.append({"vote": {"a": a, "b": b}})

            data = {"voting": voting.id, "voter": random_user.id, "votes": votes}

            self.login(user=random_user.username)
            response = self.client.post("/store/", data, format="json")

            self.assertEqual(response.status_code, 200)
            self.logout()

        return votings, users

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = "user{}".format(pk)
        user.set_password("qwerty")
        user.save()
        return user

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

    def test_vote(self):
        self.gen_votes()
        response = self.client.get("/store/", format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.get("/store/", format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get("/store/", format="json")
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.count())
        self.assertEqual(votes[0], VoteSerializer(Vote.objects.all().first()).data)

    def test_filter(self):
        votings, voters = self.gen_votes()
        v = votings[0].id

        response = self.client.get("/store/?voting_id={}".format(v), format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.get("/store/?voting_id={}".format(v), format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get("/store/?voting_id={}".format(v), format="json")
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.filter(voting_id=v).count())

        v = voters[0].id
        response = self.client.get("/store/?voter_id={}".format(v), format="json")

        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.filter(voter_id=v).count())

    def test_hasvote(self):
        self.gen_votes()
        vo = Vote.objects.first()
        v = vo.voting_id
        u = vo.voter_id

        response = self.client.get(
            "/store/?voting_id={}&voter_id={}".format(v, u), format="json"
        )
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.get(
            "/store/?voting_id={}&voter_id={}".format(v, u), format="json"
        )
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get(
            "/store/?voting_id={}&voter_id={}".format(v, u), format="json"
        )
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0]["voting_id"], v)
        self.assertEqual(votes[0]["voter_id"], u)

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
class DjangoChannelsTest(TestCase):
    def setUp(self):
        super().setUp()
        # Crea una pregunta y una votación
        question = Question.objects.create(desc="Test Question")
        self.voting = Voting.objects.create(name="Test Voting", question=question)
        self.voting.save()

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
    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = "user{}".format(pk)
        user.set_password("qwerty")
        user.save()
        return user

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

class DjangoChannelsTest(TestCase):

    def setUp(self):
        super().setUp()
        # Crea una pregunta y una votación
        question = Question.objects.create(desc='Test Question')
        self.voting = Voting.objects.create(name='Test Voting', question=question)
        self.voting.save()
        census = Census.objects.create(voting_id=self.voting.id, voter_id=user.id)

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
    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user
    
    async def test_vote_consumer_connection(self):
        # Define la ruta del WebSocket para el consumidor de votos
        application = URLRouter([
            re_path(r'ws/votes/$', VoteConsumer.as_asgi()),
        ])

        # Crea un comunicador WebSocket para la ruta del consumidor de votos
        communicator = WebsocketCommunicator(application, 'ws/votes/')

        # Intenta conectar al WebSocket
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Desconecta
        await communicator.disconnect()

    async def test_vote_consumer_message(self):

        # Define la ruta del WebSocket para el consumidor de votos
        application = URLRouter([
            re_path(r'ws/votes/$', VoteConsumer.as_asgi()),
        ])

        # Crea un comunicador WebSocket para la ruta del consumidor de votos
        communicator = WebsocketCommunicator(application, 'ws/votes/')

        # Conecta al WebSocket
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Manda mensaje por Django Channels
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            'votes', 
            {
                'type': 'vote.added',
                'vote_id': self.voting.id,
            }
        )

        # Recibe el mensaje del WebSocket
        response = await communicator.receive_json_from()
        
        # Verifica que el mensaje sea correcto
        self.assertEqual(response, {
            'message': 'Vote received',
            'vote_id': self.voting.id,
            'vote_count': 0,
            'vote_percentage': 0.0,
        })

        # Desconecta
        await communicator.disconnect()
        
