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
        vid = self.kwargs.get('voting_id', 0)
        context = {}

        try:
            r = mods.get('voting', params={'id': vid})
            c = mods.get('census', params={'voting_id': vid})
            context = {'voting': r}
            context['voting'] = json.dumps(r[0])
            context['census'] = json.dumps(c)
        except Exception as e:
            print(f"Error: {e}")
            raise Http404("Voting not found")
        return render(request, self.template_name, context)
