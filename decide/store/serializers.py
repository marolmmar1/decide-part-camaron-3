from rest_framework import serializers

from .models import Vote


<<<<<<< HEAD
class VoteSerializer(serializers.HyperlinkedModelSerializer):
    a = serializers.IntegerField()
    b = serializers.IntegerField()

    class Meta:
        model = Vote
        fields = ('voting_id', 'voter_id','a', 'b')
=======
class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('id', 'voter_id', 'voting_id', 'a', 'b', 'voted')
>>>>>>> central/integracion-votaciones
