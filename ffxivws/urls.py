from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('snaps/<int:snap_id>', views.snapshot_details, name='snapshot_details'),
    path('snaps/latest', views.snapshot_latest_redirect, name='snapshot_latest'),
    path('world/<str:world_name>', views.world_history, name='world_history'),
    path('set_timezone', views.set_timezone, name='set_timezone'),
    path('settings', views.set_setting, name='settings'),
]
