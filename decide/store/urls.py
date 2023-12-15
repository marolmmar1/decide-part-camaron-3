from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.StoreView.as_view(), name='store'),
    path('vote/create_backup/', views.create_backup, name='vote_create_backup'),
    path('vote/create_backup/<str:backup_name>/', views.create_backup, name='vote_create_backup_with_name'),
    path('vote/restore_backup/', views.restore_backup, name='vote_restore_backup'),
    path('vote/list_backup/', views.list_backups, name='vote_restore_backup_list'),
    path('vote/delete_backups/', views.delete_backups, name='delete_backups'),
    path('vote/delete_backup/<str:selected_backup>/', views.delete_selected_backup, name='delete_backup')
]
