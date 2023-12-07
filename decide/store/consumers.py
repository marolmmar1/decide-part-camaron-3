from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Count
import json
from voting.models import Voting
from census.models import Census
from store.models import Vote

class VoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        vote_id = text_data_json['vote_id']
        print(vote_id)

        # Busca la votación en la base de datos
        voting = Voting.objects.get(id=vote_id)

        # Cuenta los votos para esta votación
        vote_count = Vote.objects.filter(voting_id=vote_id).count()

        # Cuenta el número total de votantes elegibles
        total_voters = Census.objects.filter(voting_id=vote_id).count()

        # Calcula el porcentaje de votos
        vote_percentage = (vote_count / total_voters) * 100 if total_voters else 0

        await self.send(text_data=json.dumps({
            'message': 'Vote received',
            'vote_id': vote_id,  # Envía el ID de la votación al cliente
            'vote_count': vote_count,  # Envía el recuento de votos al cliente
            'vote_percentage': vote_percentage,  # Envía el porcentaje de votos al cliente
        }))