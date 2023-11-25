import json
from django.views.generic import View
from django.conf import settings
from django.shortcuts import render
from django.http import Http404
from voting.models import Voting

from base import mods


class VisualizerView(View):
    template_name = 'visualizer/visualizer.html'

    def get(self, request, *args, **kwargs):
        voting_id = self.kwargs.get('voting_id', 0)

        try:
            voting_data = Voting.objects.get(id=voting_id)
            print(voting_data)
            context = {'voting': voting_data}
        except Exception as e:
            print(f"Error: {e}")
            raise Http404("Voting not found")

        return render(request, self.template_name, context)
