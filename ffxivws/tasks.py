from .models import Snapshot
from .status_page_parser import run_snapshot

from celery import shared_task


@shared_task(name='count_snaps')
def count_snapshots():
    # debug task that accesses database and returns data
    return Snapshot.objects.count()


@shared_task(name='capture_full_snapshot')
def capture_full_snapshot():
    run_snapshot(manual=False)
