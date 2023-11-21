from django.utils import timezone
from django.utils.dateparse import parse_datetime
import django_filters.rest_framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics

<<<<<<< HEAD
=======
import subprocess
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

>>>>>>> central/integracion-votaciones
from .models import Vote
from .serializers import VoteSerializer
from base import mods
from base.perms import UserIsStaff
<<<<<<< HEAD
=======
from rest_framework.permissions import IsAuthenticated
>>>>>>> central/integracion-votaciones


class StoreView(generics.ListAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('voting_id', 'voter_id')

    def get(self, request):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        return super().get(request)

    def post(self, request):
        """
         * voting: id
         * voter: id
         * vote: { "a": int, "b": int }
        """

        vid = request.data.get('voting')
        voting = mods.get('voting', params={'id': vid})
        if not voting or not isinstance(voting, list):
            # print("por aqui 35")
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        start_date = voting[0].get('start_date', None)
        # print ("Start date: "+  start_date)
        end_date = voting[0].get('end_date', None)
<<<<<<< HEAD
        #print ("End date: ", end_date)
        not_started = not start_date or timezone.now() < parse_datetime(start_date)
        #print (not_started)
        is_closed = end_date and parse_datetime(end_date) < timezone.now()
        if not_started or is_closed:
            #print("por aqui 42")
=======
        # print ("End date: ", end_date)
        not_started = not start_date or timezone.now() < parse_datetime(start_date)
        # print (not_started)
        is_closed = end_date and parse_datetime(end_date) < timezone.now()
        if not_started or is_closed:
            # print("por aqui 42")
>>>>>>> central/integracion-votaciones
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        uid = request.data.get('voter')
        vote = request.data.get('vote')

        if not vid or not uid or not vote:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        # validating voter
        if request.auth:
            token = request.auth.key
        else:
            token = "NO-AUTH-VOTE"
<<<<<<< HEAD
        voter = mods.post('authentication', entry_point='/getuser/', json={'token': token})
=======
        voter = mods.post('authentication',
                          entry_point='/getuser/', json={'token': token})
>>>>>>> central/integracion-votaciones
        voter_id = voter.get('id', None)
        if not voter_id or voter_id != uid:
            # print("por aqui 59")
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        # the user is in the census
<<<<<<< HEAD
        perms = mods.get('census/{}'.format(vid), params={'voter_id': uid}, response=True)
=======
        perms = mods.get('census/{}'.format(vid),
                         params={'voter_id': uid}, response=True)
>>>>>>> central/integracion-votaciones
        if perms.status_code == 401:
            # print("por aqui 65")
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        a = vote.get("a")
        b = vote.get("b")

<<<<<<< HEAD
        defs = { "a": a, "b": b }
=======
        defs = {"a": a, "b": b}
>>>>>>> central/integracion-votaciones
        v, _ = Vote.objects.get_or_create(voting_id=vid, voter_id=uid,
                                          defaults=defs)
        v.a = a
        v.b = b

<<<<<<< HEAD
        
        v.save()


        
        
        if voting[0].get('voting_type', None) == 'H':
            census = mods.get('census/role/{}'.format(vid), params={'voter_id': uid}, response=True)
            census_content = census.content.decode('utf-8')
            role = census_content.strip('"')
            numero = int(role)
            for i in range(1, numero):
                v, _ = Vote.objects.get_or_create(voting_id=vid, voter_id=uid, value=i,
                                                defaults=defs)
                v.a = a
                v.b = b
                v.save()

        return  Response({})
=======
        v.save()

        return Response({})


def create_backup(request):
    try:
        subprocess.run('python manage.py dbbackup', shell=True, check=True)
        messages.success(request, 'Backup created successfully.')
    except Exception as e:
        messages.error(request, f'Error creating backup: {e}')

    return HttpResponseRedirect(reverse('admin:store_vote_changelist'))


def restore_backup(request):
    try:
        subprocess.run('python manage.py dbrestore --noinput',
                       shell=True, check=True)
        messages.success(request, 'Backup restored successfully.')
    except Exception as e:
        messages.error(request, f'Error restoring backup: {e}')

    return HttpResponseRedirect(reverse('admin:store_vote_changelist'))


class VoteHistoryView(generics.ListAPIView):
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra los votos del usuario actual
        user = self.request.user
        return Vote.objects.filter(voter_id=user.id).order_by('-voted')
>>>>>>> central/integracion-votaciones
