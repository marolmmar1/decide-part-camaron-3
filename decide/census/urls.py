from django.urls import path
from . import views


urlpatterns = [
    path("", views.CensusCreate.as_view(), name="census_create"),
    path("<int:voting_id>/", views.CensusDetail.as_view(), name="census_detail"),
]
