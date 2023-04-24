from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('snaps/<int:snap_id>', views.snapshot_details, name='snapshot_details'),
    path('set_timezone', views.set_timezone, name='set_timezone'),
]
