from rest_framework import serializers

from .models import Question, QuestionOption, Voting
from base.serializers import KeySerializer, AuthSerializer


class QuestionOptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('number', 'option')


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    options = QuestionOptionSerializer(many=True)
    class Meta:
        model = Question
        fields = ('desc', 'options')


class VotingSerializer(serializers.HyperlinkedModelSerializer):
    question = QuestionSerializer(many=False)
    pub_key = KeySerializer()
    auths = AuthSerializer(many=True)

    class Meta:
        model = Voting
<<<<<<< HEAD
        fields = ('id', 'name', 'desc', 'voting_type', 'question', 'start_date',
=======
        fields = ('id', 'name', 'desc', 'question', 'start_date',
>>>>>>> central/integracion-votaciones
                  'end_date', 'pub_key', 'auths', 'tally', 'postproc')


class SimpleVotingSerializer(serializers.HyperlinkedModelSerializer):
    question = QuestionSerializer(many=False)

    class Meta:
        model = Voting
<<<<<<< HEAD
        fields = ('name', 'desc', 'voting_type', 'question', 'start_date', 'end_date')
=======
        fields = ('name', 'desc', 'question', 'start_date', 'end_date')
>>>>>>> central/integracion-votaciones
