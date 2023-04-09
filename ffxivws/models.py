from django.db import models
from django.utils.translation import gettext_lazy as _


class Snapshot(models.Model):
    class Type(models.TextChoices):
        TIMED = 'T'
        MANUAL = 'M'
        OTHER = 'O'

    type = models.CharField(max_length=1, choices=Type.choices)
    timestamp = models.DateTimeField('state capture time')
    result = models.CharField(verbose_name='fetch result', max_length=10)
    logfile = models.BooleanField(verbose_name='has error log')

    def get_logfile_name(self) -> str | None:
        return f'{self.timestamp:%Y%m%d_%H%M%S}_{self.pk}.log' if self.logfile else None

    def __str__(self):
        return f'{str(self.timestamp)}({self.pk})'


class Region(models.Model):
    name = models.CharField(max_length=40, unique=True)
    data_region_id = models.SmallIntegerField()

    def __str__(self):
        return self.name


class DataCenter(models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=20, db_index=True, unique=True)

    def __str__(self):
        return self.name


class World(models.Model):
    data_center = models.ForeignKey(DataCenter, on_delete=models.PROTECT)
    name = models.CharField(max_length=20, db_index=True, unique=True)

    def __str__(self):
        return self.name


class WorldState(models.Model):
    class Status(models.TextChoices):
        ONLINE = 'ONL', _('Online')
        MAINTENANCE_PARTIAL = 'MTP', _('Partial Maintenance')
        MAINTENANCE_FULL = 'MTF', _('Maintenance')

    class Classification(models.TextChoices):
        STANDARD = 'ST', _('Standard')
        NEW = 'NW', _('New')
        PREFERRED = 'PF', _('Preferred')
        CONGESTED = 'CG', _('Congested')

    class CharCreation(models.IntegerChoices):
        ALLOWED = 1, _('Character creation available')
        PROHIBITED = 0, _('Character creation unavailable')

    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE)
    world = models.ForeignKey(World, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=3, choices=Status.choices)
    classification = models.CharField(max_length=2, choices=Classification.choices)
    char_creation = models.SmallIntegerField(choices=CharCreation.choices)

    def __str__(self):
        return f'{str(self.snapshot.timestamp)}-{self.world.name}'
