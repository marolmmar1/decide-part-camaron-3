from django import template

from voting.models import Voting

register = template.Library()


@register.filter(name="getVoting")
def getVoting(vid):
    return Voting.objects.get(id=vid)
