import zoneinfo
from itertools import chain
from typing import Callable, TypeVar

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_safe, require_POST

from ffxivws.models import Snapshot, WorldState, DataCenter, Region


def index(request: HttpRequest):
    return render(request=request, template_name='ffxivws/index.html.jinja', context={})


regions_abr_map = {
    'na': 'North America',
    'eu': 'Europe',
    'oc': 'Oceania',
    'jp': 'Japan'
}
TIMEZONES = zoneinfo.available_timezones()
TIMEZONES.remove('localtime')


@require_safe
def snapshot_details(request: HttpRequest, snap_id: int):
    # noinspection PyUnresolvedReferences
    s = Snapshot.objects.get(id=snap_id)

    regions: dict[str, dict[str, list[WorldState]]] = dict()    # {} breaks PyCharm's type detection for some reason
    for ws in s.worldstate_set.all():   # type: WorldState
        dc: DataCenter = ws.world.data_center
        region: Region = dc.region
        _get_or_add(
                d=_get_or_add(d=regions, key=region.name, default_factory=dict),
                key=dc.name,
                default_factory=list
        ).append(ws)

    reg_params = request.GET.getlist('regions', ('all',))
    reg_list = [r.lower() for r in chain.from_iterable(p.split(',') for p in reg_params)]
    if 'all' in reg_list:
        r_active = list(regions_abr_map.values())
    else:
        r_active = [regions_abr_map[r] for r in reg_list if r in regions_abr_map]

    context = {'snapshot': s, 'regions': regions, 'regions_active': r_active}
    return render(request=request, template_name='ffxivws/snapshot.html.jinja', using='jinja', context=context)


@require_POST
def set_timezone(request: HttpRequest):
    tz = request.POST.get('timezone', default='UTC')
    if tz in TIMEZONES:
        request.session['timezone'] = tz
    redirect_to = request.POST.get('redirect_to', default='/')
    return HttpResponseRedirect(redirect_to=redirect_to, status=303)


K = TypeVar('K')
V = TypeVar('V')


def _get_or_add(d: dict[K, V], key: K, default_factory: Callable[[], V]) -> V:
    if key in d:
        return d[key]
    v = default_factory()
    d[key] = v
    return v
