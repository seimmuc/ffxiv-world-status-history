import json
from pathlib import Path
from typing import Dict, List


if __name__ == '__main__':
    with Path('worlds.json').open(mode='rt', encoding='utf8') as f:
        regions: Dict[str, Dict[str, int | List[str]]] = json.load(f)
    result = []
    dc_id = 0
    w_id = 0
    for region_id, (region_name, region) in enumerate(regions.items(), start=1):
        # Add region
        result.append({
            'model': 'ffxivws.Region',
            'pk': region_id,
            'fields': {'name': region_name, 'data_region_id': region['data_region_id']}
        })

        for dc_name, world_list in region['data_centers'].items():
            # Add data center
            dc_id += 1
            result.append({
                'model': 'ffxivws.DataCenter',
                'pk': dc_id,
                'fields': {'region': region_id, 'name': dc_name}
            })

            for world_name in world_list:
                # Add world
                w_id += 1
                result.append({
                    'model': 'ffxivws.World',
                    'pk': w_id,
                    'fields': {'data_center': dc_id, 'name': world_name}
                })

    with Path('../worlds.fixture.json').open(mode='wt', encoding='utf8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
