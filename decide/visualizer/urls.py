from django.urls import path
from .views import (
    VisualizerView,
    download_votes_csv,
    export_votes_xls,
    download_census_csv,
    export_census_xls,
)


urlpatterns = [
    path("<int:voting_id>/", VisualizerView.as_view()),
    path("export-csv/<int:voting_id>/", download_votes_csv, name="export-csv"),
    path("export-xls/<int:voting_id>/", export_votes_xls, name="export-xls"),
    path(
        "export-census-csv/<int:voting_id>/",
        download_census_csv,
        name="export-census-csv",
    ),
    path(
        "export-census-xls/<int:voting_id>/",
        export_census_xls,
        name="export-census-xls",
    ),
]
