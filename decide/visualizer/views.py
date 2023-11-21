import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from base import mods


class VisualizerView(TemplateView):
    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
<<<<<<< HEAD
            c = mods.get('census', params={'voting_id': vid})
            context['voting'] = json.dumps(r[0])
            context['census'] = json.dumps(c)
=======
            context['voting'] = json.dumps(r[0])
>>>>>>> central/integracion-votaciones
        except:
            raise Http404

        return context
