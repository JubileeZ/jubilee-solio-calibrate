import json
from pathlib import Path

import httpx
import pytest

from solio_calibrate.client import (
    FPLClient,
    calculate_team_actual_stats,
)


def test_calculate_team_actual_stats():
    # ARS is id 1, CHE is id 6, MCI is id 15
    fixtures = [
        # GW 1: ARS (h) 3 - 0 CHE (a), finished
        {
            "event": 1,
            "finished": True,
            "team_h": 1,
            "team_a": 6,
            "team_h_score": 3,
            "team_a_score": 0,
        },
        # GW 2: MCI (h) 2 - 1 ARS (a), finished
        {
            "event": 2,
            "finished": True,
            "team_h": 15,
            "team_a": 1,
            "team_h_score": 2,
            "team_a_score": 1,
        },
        # GW 3: CHE (h) 1 - 1 MCI (a), finished
        {
            "event": 3,
            "finished": True,
            "team_h": 6,
            "team_a": 15,
            "team_h_score": 1,
            "team_a_score": 1,
        },
        # GW 4: Unfinished fixture
        {
            "event": 4,
            "finished": False,
            "team_h": 1,
            "team_a": 15,
            "team_h_score": None,
            "team_a_score": None,
        },
    ]

    stats = calculate_team_actual_stats(fixtures)

    # ARS: 2 matches played, scored 3 + 1 = 4 (avg 2.0), conceded 0 + 2 = 2 (avg 1.0)
    assert stats["ARS"]["matches_played"] == 2
    assert stats["ARS"]["goals_scored"] == 4
    assert stats["ARS"]["goals_conceded"] == 2
    assert stats["ARS"]["goals_per_match"] == pytest.approx(2.0)
    assert stats["ARS"]["conceded_per_match"] == pytest.approx(1.0)

    # CHE: 2 matches played, scored 0 + 1 = 1 (avg 0.5), conceded 3 + 1 = 4 (avg 2.0)
    assert stats["CHE"]["matches_played"] == 2
    assert stats["CHE"]["goals_scored"] == 1
    assert stats["CHE"]["goals_conceded"] == 4
    assert stats["CHE"]["goals_per_match"] == pytest.approx(0.5)
    assert stats["CHE"]["conceded_per_match"] == pytest.approx(2.0)

    # MCI: 2 matches played, scored 2 + 1 = 3 (avg 1.5), conceded 1 + 1 = 2 (avg 1.0)
    assert stats["MCI"]["matches_played"] == 2
    assert stats["MCI"]["goals_scored"] == 3
    assert stats["MCI"]["goals_conceded"] == 2
    assert stats["MCI"]["goals_per_match"] == pytest.approx(1.5)
    assert stats["MCI"]["conceded_per_match"] == pytest.approx(1.0)


def test_fpl_client_caching(tmp_path: Path):
    cache_dir = tmp_path / "cache"
    fake_bootstrap = {"teams": [{"id": 1, "name": "Arsenal", "short_name": "ARS"}]}

    # Pre-populate cache
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "bootstrap_static.json"
    cache_file.write_text(json.dumps(fake_bootstrap), encoding="utf-8")

    client = FPLClient(cache_dir=cache_dir)
    # Should read from cache without network call
    result = client.get_bootstrap_static(force_refresh=False)
    assert result == fake_bootstrap


def test_fpl_client_fetches_with_mock(tmp_path: Path):
    cache_dir = tmp_path / "cache"
    fixtures_data = [{"id": 1, "event": 1, "finished": True, "team_h": 1, "team_a": 2, "team_h_score": 1, "team_a_score": 0}]

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if "fixtures" in str(request.url):
            return httpx.Response(200, json=fixtures_data)
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    http_client = httpx.Client(transport=transport)

    client = FPLClient(cache_dir=cache_dir, http_client=http_client)
    fixtures = client.get_fixtures(force_refresh=True)

    assert fixtures == fixtures_data
    assert (cache_dir / "fixtures.json").is_file()
