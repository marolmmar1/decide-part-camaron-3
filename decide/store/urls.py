from django.urls import path, include
from . import views

<<<<<<< HEAD

urlpatterns = [
    path('', views.StoreView.as_view(), name='store'),
=======
app_name='store'

urlpatterns = [
    path('', views.StoreView.as_view(), name='store'),
    path('vote/create_backup/', views.create_backup, name='vote_create_backup'),
    path('vote/restore_backup/', views.restore_backup, name='vote_restore_backup'),
>>>>>>> central/integracion-votaciones
]
