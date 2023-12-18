import json

from random import choice

from locust import (
    HttpUser,
    SequentialTaskSet,
    TaskSet,
    task,
    between,
    events
)
import websocket
import time


HOST = "http://localhost:8000"
VOTING = 1


class DefVisualizer(TaskSet):

    @task
    def index(self):
        self.client.get("/visualizer/{0}/".format(VOTING))


class DefVoters(SequentialTaskSet):

    def on_start(self):
        with open('voters.json') as f:
            self.voters = json.loads(f.read())
        self.voter = choice(list(self.voters.items()))

    @task
    def login(self):
        username, pwd = self.voter
        self.token = self.client.post("/authentication/login/", {
            "username": username,
            "password": pwd,
        }).json()

    @task
    def getuser(self):
        self.usr= self.client.post("/authentication/getuser/", self.token).json()
        print( str(self.user))

    @task
    def voting(self):
        headers = {
            'Authorization': 'Token ' + self.token.get('token'),
            'content-type': 'application/json'
        }
        self.client.post("/store/", json.dumps({
            "token": self.token.get('token'),
            "vote": {
                "a": "12",
                "b": "64"
            },
            "voter": self.usr.get('id'),
            "voting": VOTING
        }), headers=headers)


    def on_quit(self):
        self.voter = None

class Visualizer(HttpUser):
    host = HOST
    tasks = [DefVisualizer]
    wait_time = between(3,5)


class Voters(HttpUser):
    host = HOST
    tasks = [DefVoters]
    wait_time= between(3,5)


# Para probarlo tener abierto tambien decide desplegado en el puerto 8000
class WebSocketUser(HttpUser):
    """
    Para probarlo tener abierto tambien decide desplegado en el puerto 8000
    """
    host = "ws://localhost:8000/ws/votes/"
    wait_time = between(5, 15)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = None
    
    def on_start(self):
        try:
            self.ws = websocket.create_connection(f"{self.host}")
        except Exception as e:
            print(f"Failed to connect: {e}")
    
    def on_stop(self):
        if self.ws is not None:
            self.ws.close()

    
    @task
    def send_message(self):
        if self.ws is not None:
            message = json.dumps({"type": "vote.added", "vote_id": 1})
            
            start_time = time.time()
            self.ws.send(message)
            response = self.ws.recv()
            end_time = time.time()
            
            response_time = int((end_time - start_time) * 1000)  # response time in milliseconds
            events.request.fire(request_type="WebSocket", name="vote.added", response_time=response_time, response_length=len(response))