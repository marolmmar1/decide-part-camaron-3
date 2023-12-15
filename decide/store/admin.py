from django.contrib import admin
from django.db.models import Count
from .models import Vote
from census.models import Census   
from voting.models import Voting   
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class VoteAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id', 'voted')
    search_fields = ('voting_id', 'voter_id')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        votes = Vote.objects.values('voting_id').annotate(total_votes=Count('voting_id'))
        for vote in votes:
            census = Census.objects.filter(voting_id=vote['voting_id']).values('voter_id').distinct().count()
            vote['percentage'] = (vote['total_votes'] / census) * 100 if census else 0
            vote['start_date'] = Voting.objects.filter(id=vote['voting_id']).values('start_date').first()['start_date']
            vote['end_date'] = Voting.objects.filter(id=vote['voting_id']).values('end_date').first()['end_date']
            vote['name'] = Voting.objects.filter(id=vote['voting_id']).values('name').first()['name']
        extra_context['votes'] = votes
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
         
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'votes', 
            {
                'type': 'vote.added',
                'vote_id': obj.voting_id,
            }
        )


admin.site.register(Vote, VoteAdmin)
