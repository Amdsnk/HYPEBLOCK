import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.artwork import ArtworkManager
from backend.server import _JsonDatabase, _validate_collection, app, build_prompt, generate_collection

ROOT = Path(__file__).resolve().parents[1]


def test_all_records_have_allowed_eye_traits_and_rich_prompts():
    items, _ = generate_collection()
    assert len(items) == 296
    assert sum(item['traits']['Gender'] == 'Male' for item in items) == 148
    assert sum(item['traits']['Gender'] == 'Female' for item in items) == 148
    for item in items:
        assert item['traits']['Eyes'] != 'Cyclops'
        assert 'Exactly TWO' in item['prompt']
        assert 'HYPEBLOCK' in item['prompt']
        assert 'CRITICAL SKIN RULE' in item['prompt']
        assert 'No wounds, scars' in item['prompt']
        assert 'rotting grey-green' not in item['prompt']
        if item['traits']['Gender'] == 'Male':
            assert 'compact broad cartoon gremlin head' in item['prompt']
            assert 'rugged masculine face' not in item['prompt']
        if item['traits']['Accessory'] in ('Chain', 'Diamond Chain', 'Iced Chain'):
            assert 'pendant' in item['prompt']
    bad = {**items[0], 'traits': {**items[0]['traits'], 'Eyes': 'Cyclops'}}
    with pytest.raises(RuntimeError):
        _validate_collection([bad])
    with pytest.raises(ValueError):
        build_prompt(bad['traits'])


def test_retired_art_is_not_served_even_from_persistent_override(tmp_path):
    art = tmp_path / 'generated'
    art.mkdir()
    raw = b'retired-art'
    (art / '1.png').write_bytes(raw)
    (tmp_path / 'art_direction.json').write_text(json.dumps({'version': 'two-eyes-brand-v1', 'blocked_artwork': [{'token_id': 1, 'sha256': hashlib.sha256(raw).hexdigest()}]}))
    db = _JsonDatabase(tmp_path / 'store.json')
    manager = ArtworkManager(db, tmp_path)
    assert manager.path(1) is None
    (art / '1.png').write_bytes(b'new-two-eye-art')
    assert manager.path(1) == art / '1.png'


def test_excluded_fallback_assets_return_404():
    with TestClient(app) as client:
        for name in ('green_cyclops_cigar.jpeg', 'purple_cyclops.jpeg', 'zombie_horns.jpeg', 'zombie_bomber.jpeg', 'zombie_laser_epic.jpeg', 'att_zombie_devil_epic.jpeg'):
            assert client.get('/api/assets/' + name).status_code == 404
