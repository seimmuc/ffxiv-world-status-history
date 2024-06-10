import json
from pathlib import Path
from typing import Dict, List, Any, TypedDict, NamedTuple, Literal


MODEL_TYPE = Literal['ffxivws.Region', 'ffxivws.DataCenter', 'ffxivws.World']

MODNAME_REGION: MODEL_TYPE = 'ffxivws.Region'
MODNAME_DC: MODEL_TYPE = 'ffxivws.DataCenter'
MODNAME_WORLD: MODEL_TYPE = 'ffxivws.World'


class FixtureEntry(TypedDict):
    model: str
    pk: int
    fields: Dict[str, Any]


class Fixture(NamedTuple):
    data: List[FixtureEntry]
    regions: Dict[str, FixtureEntry]
    data_centers: Dict[str, FixtureEntry]
    worlds: Dict[str, FixtureEntry]

    def add(self, entry: FixtureEntry):
        if entry['model'] == MODNAME_REGION:
            d = self.regions
        elif entry['model'] == MODNAME_DC:
            d = self.data_centers
        elif entry['model'] == MODNAME_WORLD:
            d = self.worlds
        else:
            raise RuntimeError(f'Cannot load fixture: unknown model name "{entry["model"]}" found')
        name = entry['fields']['name']
        if name in d:
            raise RuntimeError(f'Cannot load fixture: duplicate entry name "{name}" for model "{entry["model"]}"')
        d[name] = entry
        self.data.append(entry)

    def max_id(self, model_type: MODEL_TYPE) -> int:
        max_id = 0
        for e in self.data:
            if e['model'] == model_type and e['pk'] > max_id:
                max_id = e['pk']
        return max_id


worlds_json_path = Path('worlds.json')
fixture_path = Path('../worlds.fixture.json')


def load_fixture(filepath: Path) -> Fixture:
    fix = Fixture(data=[], regions={}, data_centers={}, worlds={})
    try:
        with filepath.open(mode='rt', encoding='utf8') as f:
            fixture_data: List[FixtureEntry] = json.load(f)
    except FileNotFoundError:
        fixture_data = []
    for fix_entry in fixture_data:
        fix.add(fix_entry)
    return fix


if __name__ == '__main__':
    with worlds_json_path.open(mode='rt', encoding='utf8') as f:
        regions: Dict[str, Dict[str, int | Dict[str, List[str]]]] = json.load(f)

    fixture = load_fixture(fixture_path)
    max_id_rg = fixture.max_id(MODNAME_REGION)
    max_id_dc = fixture.max_id(MODNAME_DC)
    max_id_wr = fixture.max_id(MODNAME_WORLD)

    for region_name, region in regions.items():
        # Add region if it doesn't exist
        if region_name in fixture.regions:
            region_id = fixture.regions[region_name]['pk']
        else:
            region_id = max_id_rg = max_id_rg + 1
            fixture.add(entry={
                'model': MODNAME_REGION,
                'pk': region_id,
                'fields': {'name': region_name, 'data_region_id': region['data_region_id']}
            })

        for dc_name, world_list in region['data_centers'].items():
            # Add data center if it doesn't exist
            if dc_name in fixture.data_centers:
                dc_id = fixture.data_centers[dc_name]['pk']
            else:
                dc_id = max_id_dc = max_id_dc + 1
                fixture.add({
                    'model': MODNAME_DC,
                    'pk': dc_id,
                    'fields': {'region': region_id, 'name': dc_name}
                })

            for world_name in world_list:
                # Add world if it doesn't exist
                if world_name not in fixture.worlds:
                    w_id = max_id_wr = max_id_wr + 1
                    fixture.add({
                        'model': MODNAME_WORLD,
                        'pk': w_id,
                        'fields': {'data_center': dc_id, 'name': world_name}
                    })

    with fixture_path.open(mode='wt', encoding='utf8') as f:
        json.dump(fixture.data, f, ensure_ascii=False, indent=2)
