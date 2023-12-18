from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import django_filters.rest_framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
import os
from django.shortcuts import render
from django.conf import settings

import subprocess
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse


from .models import Vote
from .serializers import VoteSerializer
from base import mods
from base.perms import UserIsStaff
from rest_framework.permissions import IsAuthenticated

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class StoreView(generics.ListAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ("voting_id", "voter_id")

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
        vid = request.data.get("voting")
        voting = mods.get("voting", params={"id": vid})

        vid = request.data.get("voting")

        voting = mods.get("voting", params={"id": vid})
        if not voting or not isinstance(voting, list):
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        start_date = voting[0].get("start_date", None)
        # print ("Start date: "+  start_date)
        end_date = voting[0].get("end_date", None)
        # print ("End date: ", end_date)
        not_started = not start_date or timezone.now() < parse_datetime(start_date)
        # print (not_started)
        is_closed = end_date and parse_datetime(end_date) < timezone.now()
        if not_started or is_closed:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        uid = request.data.get("voter")
        votes = request.data.get("votes")  # Expect 'votes' to be an array

        if not vid or not uid or not votes:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        # validating voter
        if request.auth:
            token = request.auth.key
        else:
            token = "NO-AUTH-VOTE"
        voter = mods.post(
            "authentication", entry_point="/getuser/", json={"token": token}
        )
        voter_id = voter.get("id", None)
        if not voter_id or voter_id != uid:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        # the user is in the census
        perms = mods.get(
            "census/{}".format(vid), params={"voter_id": uid}, response=True
        )
        if perms.status_code == 401:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        for vote in votes:
            nested_vote = vote.get("vote")
            if nested_vote:
                a = nested_vote.get("a")
                b = nested_vote.get("b")
                v = Vote(voting_id=vid, voter_id=uid, a=a, b=b)
                v.save()

        defs = {"a": a, "b": b}
        if voting[0].get("voting_type", None) == "H":
            census = mods.get(
                "census/role/{}".format(vid), params={"voter_id": uid}, response=True
            )
            census_content = census.content.decode("utf-8")
            role = census_content.strip('"')
            numero = int(role)
            for i in range(1, numero):
                v, _ = Vote.objects.get_or_create(
                    voting_id=vid, voter_id=uid, value=i, defaults=defs
                )
                v.a = a
                v.b = b
                v.save()

        # Send a message through Django Channels
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "votes",
            {
                "type": "vote.added",
                "vote_id": vid,
            },
        )

        return Response({})


def create_backup(request, backup_name=None):
    try:
        if not os.path.exists(settings.DATABASE_BACKUP_DIR):
            os.makedirs(settings.DATABASE_BACKUP_DIR)
        if backup_name:
            backup_path = os.path.join(settings.DATABASE_BACKUP_DIR, backup_name)
            command = f"python manage.py dbbackup -O={backup_path}.psql.bin"
        else:
            command = "python manage.py dbbackup"

        subprocess.run(command, shell=True, check=True)
        messages.success(
            request,
            f'Backup "{backup_name}" created successfully.'
            if backup_name
            else "Backup created successfully.",
        )
    except Exception as e:
        messages.error(request, f"Error creating backup: {e}")

    return HttpResponseRedirect(reverse("admin:store_vote_changelist"))


def list_backups(request):
    backup_dir = settings.DATABASE_BACKUP_DIR
    backup_files = list(os.listdir(backup_dir))

    return render(request, "list_backups.html", {"backup_files": backup_files})


def restore_backup(request):
    if request.method == "POST":
        selected_backup = request.POST.get("selected_backup", "")
        try:
            backup_files = os.listdir(settings.DATABASE_BACKUP_DIR)
            if selected_backup in backup_files:
                subprocess.run(
                    [
                        "python",
                        "manage.py",
                        "dbrestore",
                        "--noinput",
                        "-i",
                        selected_backup,
                    ],
                    check=True,
                )
                messages.success(
                    request, f"Backup {selected_backup} restored successfully."
                )
            else:
                messages.error(
                    request, f"Error restoring backup: Backup file not found"
                )
                return HttpResponseBadRequest(
                    f"Error restoring backup: Backup file not found: {selected_backup}"
                )
        except Exception as e:
            messages.error(request, f"Error restoring backup: {e}")
            return HttpResponseBadRequest(f"Error restoring backup: {e}")

    return HttpResponseRedirect(reverse("admin:store_vote_changelist"))


def delete_backups(request):
    backup_files = list(os.listdir(settings.DATABASE_BACKUP_DIR))
    return render(request, "delete_backups.html", {"backups": backup_files})


def delete_selected_backup(request, selected_backup):
    if request.method == "POST":
        selected_backup = request.POST.get("selected_backup", None)
        if selected_backup:
            backup_path = os.path.join(settings.DATABASE_BACKUP_DIR, selected_backup)
            if (
                os.path.exists(backup_path)
                and backup_path.endswith(".psql.bin")
                and not ".." in backup_path
            ):
                os.remove(backup_path)
                messages.success(
                    request, f'Backup "{selected_backup}" deleted successfully.'
                )
            else:
                messages.error(request, "Error deleting backup: Backup file not found")
                return HttpResponseBadRequest(
                    f"Error deleting backup: Backup file not found: {selected_backup}"
                )
        else:
            messages.error(request, "No backup selected for deletion.")
        return HttpResponseRedirect(reverse("store:delete_backups"))
    else:
        return render(
            request, "confirm_delete.html", {"selected_backup": selected_backup}
        )


def delete_backups(request):
    backup_files = list(os.listdir(settings.DATABASE_BACKUP_DIR))
    return render(request, "delete_backups.html", {"backups": backup_files})


def delete_selected_backup(request, selected_backup):
    if request.method == "POST":
        selected_backup = request.POST.get("selected_backup", None)
        if selected_backup:
            backup_path = os.path.join(settings.DATABASE_BACKUP_DIR, selected_backup)
            if (
                os.path.exists(backup_path)
                and backup_path.endswith(".psql.bin")
                and not ".." in backup_path
            ):
                os.remove(backup_path)
                messages.success(
                    request, f'Backup "{selected_backup}" deleted successfully.'
                )
            else:
                messages.error(request, "Error deleting backup: Backup file not found")
                return HttpResponseBadRequest(
                    f"Error deleting backup: Backup file not found: {selected_backup}"
                )
        else:
            messages.error(request, "No backup selected for deletion.")
        return HttpResponseRedirect(reverse("store:delete_backups"))
    else:
        return render(
            request, "confirm_delete.html", {"selected_backup": selected_backup}
        )


class VoteHistoryView(generics.ListAPIView):
    serializer_class = VoteSerializer
    template_name = "voteHistory.html"

    def get(self, request):
        # Filtra los votos del usuario actual
        self.permission_classes = (IsAuthenticated,)
        self.check_permissions(request)
        user = self.request.user
        votes = Vote.objects.filter(voter_id=user.id).order_by("-voted")
        votesEmpty = len(votes) == 0
        return render(
            request, self.template_name, {"votes": votes, "votesEmpty": votesEmpty}
        )
