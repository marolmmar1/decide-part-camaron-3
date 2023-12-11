import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from base import mods
from voting.models import QuestionOption, Voting


# TODO: check permissions and census
class BoothView(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            voting = Voting.objects.filter(id=vid).get()
            context['voting_obj'] = voting
            order_options = [i + 1 for i in range(QuestionOption.objects.filter(question=voting.question).count())]
            r[0]['order_options'] = order_options
            
            context['voting'] = json.dumps(r[0])

        except Exception as e:
            print(e)
            raise Http404

        context['KEYBITS'] = settings.KEYBITS

        return context
