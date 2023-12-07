from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

<<<<<<< HEAD
from base.perms import UserIsStaff, IsReadOnly
# from rest_framework.permissions import OR
=======
from base.perms import UserIsStaff
>>>>>>> central/integracion-votaciones
from .models import Census


class CensusCreate(generics.ListCreateAPIView):
<<<<<<< HEAD
    permission_classes = [IsReadOnly|UserIsStaff]
=======
    permission_classes = (UserIsStaff,)
>>>>>>> central/integracion-votaciones

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        role = request.data.get('role','0')
        try:
            for voter in voters:
                if not (isinstance(role, str)) or (len(role) != 1):
                    return Response('Invalid role value.', status=ST_400)
                census = Census(voting_id=voting_id, voter_id=voter, role=role)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
<<<<<<< HEAD

=======
>>>>>>> central/integracion-votaciones
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')
<<<<<<< HEAD
    
class CensusRole(generics.RetrieveAPIView):
    
    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            census = Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response(census.role)
=======
>>>>>>> central/integracion-votaciones
