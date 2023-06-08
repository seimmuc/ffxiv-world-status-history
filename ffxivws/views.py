import json
import zoneinfo
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from itertools import chain
from typing import TypeVar, NamedTuple, List, Iterator, Any

from django.db.models import QuerySet, Choices
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_safe, require_POST

from ffxivws.models import Snapshot, WorldState, DataCenter, Region, World
from ffxivws.utils import get_or_add_to_dict


# Constants
regions_abr_map = {
    'na': 'North America',
    'eu': 'Europe',
    'oc': 'Oceania',
    'jp': 'Japan'
}
TIMEZONES = zoneinfo.available_timezones()
TIMEZONES.remove('localtime')
TIMEZONES_LIST = sorted(TIMEZONES)
# Move UTC to the front of the list
TIMEZONES_LIST.remove('UTC')
TIMEZONES_LIST.insert(0, 'UTC')
STATUS_ENUM: dict[str, WorldState.Status] = {e.value: e for e in WorldState.Status}
STATUS_ORD: dict[WorldState.Status, int] = {e: i for i, e in enumerate(WorldState.Status)}
CLASSIFICATIONS_ENUM: dict[str, WorldState.Classification] = {e.value: e for e in WorldState.Classification}
CLASSIFICATIONS_ORD: dict[WorldState.Classification, int] = {e: i for i, e in enumerate(WorldState.Classification)}
CHAR_CREATION_ENUM: dict[str, WorldState.CharCreation] = {e.value: e for e in WorldState.CharCreation}
CHAR_CREATION_ORD: dict[WorldState.CharCreation, int] = {e: i for i, e in enumerate(WorldState.CharCreation)}
DAYS_OPTIONS = [('Week', 7), ('2 Weeks', 14), ('Month', 30), ('90 Days', 90)]


# Utility classes and functions
@dataclass(frozen=True)
class NavbarItem:
    display_text: str

    @classmethod
    def from_dict(cls, source: dict[str, Any]) -> 'NavbarItem':
        t = source['type']
        if t == 'separator':
            return NavbarSeparator('')
        elif t == 'text':
            return NavbarText(display_text=source['text'])
        elif t == 'menu':
            return NavbarMenu(display_text=source['text'],
                              children=list(cls.from_dict(cs) for cs in source['children']))
        elif t == 'button':
            return NavbarButton(display_text=source['text'], target_url=source['url'])
        else:
            raise RuntimeError('Invalid NavbarItem type')


@dataclass(frozen=True)
class NavbarSeparator(NavbarItem):
    type = 'separator'


@dataclass(frozen=True)
class NavbarText(NavbarItem):
    type = 'text'


@dataclass(frozen=True)
class NavbarMenu(NavbarItem):
    children: List[NavbarItem]
    type = 'menu'


@dataclass(frozen=True)
class NavbarButton(NavbarItem):
    target_url: str
    type = 'button'


def build_navbar() -> tuple[list[NavbarItem], dict[str, dict[str, list[str]]]]:
    wld_dict: dict[str, dict[str, list[str]]] = {}  # Dict[region_name, Dict[dc_name, List[world_name]]]
    for w in World.objects.all():   # type: World
        dc = w.data_center
        get_or_add_to_dict(
                d=get_or_add_to_dict(d=wld_dict, key=dc.region.name, default_factory=dict),
                key=dc.name,
                default_factory=list
        ).append(w.name)
    worlds_menu = []
    for i, (reg_name, dc) in enumerate(wld_dict.items()):
        if i > 0:
            worlds_menu.append(NavbarSeparator(''))
        worlds_menu.append(NavbarText(display_text=reg_name))
        for dc_name, world_list in dc.items():
            dc_children: list[NavbarItem] = []
            worlds_menu.append(NavbarMenu(display_text=dc_name, children=dc_children))
            for world_name in world_list:
                world_url = reverse_lazy('world_history', kwargs={'world_name': world_name})
                dc_children.append(NavbarButton(display_text=world_name, target_url=world_url))
    return [
        NavbarButton(display_text='Home', target_url=reverse_lazy('index')),
        NavbarMenu(display_text='Worlds', children=worlds_menu),
        NavbarMenu(display_text='Snapshots', children=[
            NavbarButton(display_text='Latest', target_url=reverse_lazy('snapshot_latest'))
        ])
    ], wld_dict


# Constants that require utility classes/functions
navbar, worlds = build_navbar()


def timezone_ctx() -> dict[str, Any]:
    return dict(timezones=TIMEZONES_LIST, current_tz=timezone.get_current_timezone())


def navbar_ctx(current_position: list[str] | None = None) -> dict[str, Any]:
    return {'navbar': navbar, 'navbar_pos': current_position}


def index(request: HttpRequest):
    return render(request=request, template_name='ffxivws/index.html.jinja', context={})


# noinspection PyUnusedLocal
def snapshot_latest_redirect(request: HttpRequest):
    try:
        snapshot = Snapshot.objects.latest('timestamp')
    except Snapshot.DoesNotExist:
        return HttpResponse(b'No snapshots found', status=404, content_type='text/plain')
    return redirect('snapshot_details', permanent=False, snap_id=snapshot.id)


@require_safe
def snapshot_details(request: HttpRequest, snap_id: int):
    try:
        # noinspection PyUnresolvedReferences
        s = Snapshot.objects.get(id=snap_id)
    except Snapshot.DoesNotExist:
        return HttpResponse(b'Snapshot not found', status=404, content_type='text/plain')

    regions: dict[str, dict[str, list[WorldState]]] = dict()    # {} breaks PyCharm's type detection for some reason
    for ws in s.worldstate_set.all():   # type: WorldState
        dc: DataCenter = ws.world.data_center
        region: Region = dc.region
        get_or_add_to_dict(
                d=get_or_add_to_dict(d=regions, key=region.name, default_factory=dict),
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
    context.update(timezone_ctx())
    context.update(navbar_ctx(current_position=['Snapshots']))
    return render(request=request, template_name='ffxivws/snapshot.html.jinja', using='jinja', context=context)


class WorldStateSummary(NamedTuple):
    status: List[WorldState.Status]
    classification: List[WorldState.Classification]
    # noinspection SpellCheckingInspection
    # because I don't want underscores in CSS and can't use dashes here
    charcreate: List[WorldState.CharCreation]
    snapshots: List[WorldState]

    @classmethod
    def from_world_state_list(cls, wsl: list[WorldState]) -> 'WorldStateSummary':
        st = cls._sorted_enum_list((ws.status for ws in wsl), STATUS_ENUM, STATUS_ORD)
        cl = cls._sorted_enum_list((ws.classification for ws in wsl), CLASSIFICATIONS_ENUM, CLASSIFICATIONS_ORD)
        cc = cls._sorted_enum_list((ws.char_creation for ws in wsl), CHAR_CREATION_ENUM, CHAR_CREATION_ORD)
        return cls(status=st, classification=cl, charcreate=cc, snapshots=wsl)

    T = TypeVar('T', bound=Choices)

    @staticmethod
    def _sorted_enum_list(it: Iterator[str], enum_dict: dict[str, T], enum_ord: dict[T, int]) -> list[T]:
        return sorted((enum_dict[s] for s in set(it)), key=lambda e: enum_ord[e])


@require_safe
def world_history(request: HttpRequest, world_name: str):
    if not world_name.isalpha():
        return HttpResponse(b'Invalid world name', status=400, content_type='text/plain')
    try:
        world = World.objects.get(name__iexact=world_name)
    except World.DoesNotExist:
        return HttpResponse(b'World not found', status=404, content_type='text/plain')
    try:
        history_length = max(min(int(request.GET.get('days', 7)), 180), 0)
    except ValueError:
        history_length = 7
    today = timezone.localdate()
    from_date = today - timedelta(days=history_length)
    from_time = datetime.combine(from_date, time(), tzinfo=timezone.get_current_timezone())
    states: QuerySet[WorldState] = WorldState.objects.filter(world=world, snapshot__timestamp__gte=from_time)
    by_day: dict[date, list[WorldState]] = {}
    for state in states:
        get_or_add_to_dict(d=by_day, key=timezone.localdate(state.snapshot.timestamp), default_factory=list).append(state)
    days: list[tuple[date, WorldStateSummary | None]] = []
    cd: date = today
    while cd >= from_date:
        days.append((cd, WorldStateSummary.from_world_state_list(by_day[cd]) if (cd in by_day) else None))
        cd -= timedelta(days=1)
    js_data = {ws.snapshot.id: dict(status=ws.get_status_display(), classification=ws.get_classification_display(),
                                    charcreate=ws.get_char_creation_display())
               for day, summary in days if summary is not None for ws in summary.snapshots}
    js_data = json.dumps(js_data, ensure_ascii=False)
    context = dict(days=days, world=world, from_date=from_date, today=today, days_opt=DAYS_OPTIONS, js_data=js_data)
    context.update(timezone_ctx())
    context.update(navbar_ctx(current_position=['Worlds', world.data_center.name, world.name]))
    return render(request=request, template_name='ffxivws/world.html.jinja', using='jinja', context=context)


@require_POST
def set_timezone(request: HttpRequest):
    tz = request.POST.get('timezone', default='UTC')
    if tz in TIMEZONES:
        request.session['timezone'] = tz
    redirect_to = request.POST.get('redirect_to', default='/')
    return HttpResponseRedirect(redirect_to=redirect_to, status=303)


