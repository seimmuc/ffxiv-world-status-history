from pathlib import Path
from typing import Dict, TypeVar, Iterator, Tuple

import requests
from bs4 import BeautifulSoup, Tag
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from ffxivws.models import WorldState, World, Snapshot


class FwsHTMLParseError(RuntimeError):
    pass


@transaction.atomic
def run_snapshot(text=None, manual=False):
    if text is None:
        text = fetch_data()

    wqs: QuerySet[World] = World.objects.all()
    worlds: Dict[str, World] = {w.name.lower(): w for w in wqs}
    s: Snapshot = Snapshot.objects.create(
            type=Snapshot.Type.MANUAL if manual else Snapshot.Type.TIMED,
            timestamp=timezone.now(),
            result='Pending',
            logfile=False
    )

    log = ''
    ws_count = 0
    fail_count = 0
    for world_tag, dc_name in iter_worlds(text):
        try:
            w_state = parse_world_state(w_tag=world_tag, snapshot=s, worlds=worlds)
            w_state.save()
            ws_count += 1
        except (FwsHTMLParseError, KeyError) as e:
            log += f'encountered {type(e).__name__} while getting world state:\n=====\n{world_tag.prettify()}=====\n\n'
            fail_count += 1

    if fail_count:
        log += f'\nfailed to save {fail_count} world states, ({ws_count} succeeded)\n'
        s.result = 'Error'
        s.logfile = True
        with Path(s.get_logfile_name()).open('wt', encoding='utf8') as f:
            f.write(log)
    else:
        s.result = 'Success'
    s.save()


def fetch_data() -> str:
    response = requests.get('https://na.finalfantasyxiv.com/lodestone/worldstatus/')
    response.raise_for_status()
    return response.text


def iter_worlds(page_html: str) -> Iterator[Tuple[Tag, str]]:
    soup = BeautifulSoup(page_html, features='html.parser')
    tab_tags = soup.select('body > div.ldst__bg > div.ldst__contents.clearfix > .js--tab-content')
    if len(tab_tags) != 4:
        raise FwsHTMLParseError(f'{len(tab_tags)} region tab tags found, expected 4')
    dc_tags = soup.select('body > div.ldst__bg > div.ldst__contents.clearfix > div.js--tab-content > '
                          'ul.world-dcgroup > li.world-dcgroup__item')
    for dc_tag in dc_tags:
        dc_name = dc_tag.select_one('h2.world-dcgroup__header').text
        world_tags = dc_tag.select('ul > li.item-list > div.world-list__item')
        for world_tag in world_tags:
            yield world_tag, dc_name


status_classes = {
    'world-ic__1': WorldState.Status.ONLINE,
    'world-ic__2': WorldState.Status.MAINTENANCE_PARTIAL,
    'world-ic__3': WorldState.Status.MAINTENANCE_FULL
}
char_create_classes = {
    'world-ic__available': WorldState.CharCreation.ALLOWED,
    'world-ic__unavailable': WorldState.CharCreation.PROHIBITED
}

T = TypeVar('T')


def find_class_in_tag(tag: Tag, classes: Dict[str, T]) -> T:
    for cl in tag['class']:
        if cl in classes:
            return classes[cl]
    return None


def parse_world_status(status_tag: Tag) -> WorldState.Status:
    status = find_class_in_tag(status_tag, status_classes)
    if status is None:
        raise FwsHTMLParseError(f'Unknown world status: tag="{status_tag}"')
    return status


def parse_classification(class_tag: Tag) -> WorldState.Classification:
    c_text = class_tag.text.upper()
    if c_text not in WorldState.Classification.names:
        raise FwsHTMLParseError(f'Unknown world classification: tag={c_text}')
    return WorldState.Classification[c_text]


def parse_char_creation(cc_tag: Tag) -> WorldState.CharCreation:
    cc = find_class_in_tag(cc_tag, char_create_classes)
    if cc is None:
        raise FwsHTMLParseError(f'Unknown character creation state: tag="{cc_tag}"')
    return cc


def parse_world_state(w_tag: Tag, snapshot: Snapshot, worlds: Dict[str, World]) -> WorldState:
    name = w_tag.select_one('div.world-list__world_name > p').text
    w = worlds[name.lower()]
    ws = WorldState(
            snapshot=snapshot,
            world=w,
            status=parse_world_status(status_tag=w_tag.select_one('div.world-list__status_icon > i')),
            classification=parse_classification(w_tag.select_one('div.world-list__world_category > p')),
            char_creation=parse_char_creation(w_tag.select_one('div.world-list__create_character > i'))
    )
    return ws
