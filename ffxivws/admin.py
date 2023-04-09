from django.contrib import admin

from ffxivws.models import Snapshot, DataCenter, World, Region, WorldState


admin.site.register(Snapshot)
admin.site.register(WorldState)
admin.site.register(Region)
admin.site.register(DataCenter)
admin.site.register(World)
