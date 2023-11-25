from django import forms
from .models import PostProcessing


class PostProcessingForm(forms.ModelForm):
    class Meta:
        model = PostProcessing
        fields = ['voting', 'question', 'type']
