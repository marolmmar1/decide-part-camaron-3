from django.urls import path, include
from . import views

app_name='store'

urlpatterns = [
    path('', views.StoreView.as_view(), name='store'),
    path('vote/create_backup/', views.create_backup, name='vote_create_backup'),
]
