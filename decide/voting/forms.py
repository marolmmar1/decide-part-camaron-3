from voting.models import Question
from django.forms import ModelForm
from voting.models import Voting
from voting.models import QuestionOption
from base.models import Auth

class QuestionForm(ModelForm):
    class Meta: 
        model= Question
        fields = ['desc']

class QuestionYNForm(ModelForm):
    class Meta: 
        model= Question
        fields = ['desc', 'optionSiNo','third_option']
