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


def test_calculate_team_empirical_form_empty():
    from solio_calibrate.client import calculate_team_empirical_form

    stats = calculate_team_empirical_form([])
    assert "ARS" in stats
    assert stats["ARS"]["matches_played"] == 0
    assert stats["ARS"]["empirical_attack_per_match"] == 0.0
    assert stats["ARS"]["empirical_defense_per_match"] == 0.0


def test_calculate_team_empirical_form_matches():
    from solio_calibrate.client import calculate_team_empirical_form

    matches = [
        {
            "id": 1,
            "event": 1,
            "home_team": "ARS",
            "away_team": "COV",
            "home_goals": 3,
            "away_goals": 0,
            "home_xg": 2.5,
            "away_xg": 0.5,
        },
        {
            "id": 2,
            "event": 2,
            "home_team": "MCI",
            "away_team": "COV",
            "home_goals": 4,
            "away_goals": 1,
            "home_xg": 3.0,
            "away_xg": 0.8,
        },
    ]

    stats = calculate_team_empirical_form(matches)
    assert stats["ARS"]["matches_played"] == 1
    assert stats["MCI"]["matches_played"] == 1
    assert stats["COV"]["matches_played"] == 2
    # Verify rates are positive and clamped
    assert stats["ARS"]["empirical_attack_per_match"] > 0.0
    assert stats["ARS"]["empirical_defense_per_match"] >= 0.0


def test_fpl_client_get_event_live_caching(tmp_path: Path):
    cache_dir = tmp_path / "cache"
    fake_live = {"elements": [{"id": 1, "stats": {"minutes": 90, "expected_goals": "0.50"}}]}

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "event_live_1.json"
    cache_file.write_text(json.dumps(fake_live), encoding="utf-8")

    client = FPLClient(cache_dir=cache_dir)
    result = client.get_event_live(1, force_refresh=False)
    assert result == fake_live


def test_venue_neutralization_in_empirical_form():
    from solio_calibrate.client import calculate_team_empirical_form

    # 1 match: Team ARS at home scoring 1.644, conceding 1.356 to COV
    # With home factor h = 0.096, neutralized attack is 1.644 / (1 + 0.096) = 1.500
    # Neutralized defense is 1.356 / (1 - 0.096) = 1.500
    matches = [
        {
            "id": 1,
            "event": 1,
            "home_team": "ARS",
            "away_team": "COV",
            "home_goals": 2,
            "away_goals": 1,
            "home_xg": 1.288,
            "away_xg": 1.712,
        }
    ]
    # Pass home_factor=0.096
    stats = calculate_team_empirical_form(matches, home_factor=0.096)
    assert stats["ARS"]["raw_attack_per_match"] == pytest.approx(1.500, abs=1e-3)
    assert stats["ARS"]["raw_defense_per_match"] == pytest.approx(1.500, abs=1e-3)
    assert "home_factor" in stats["ARS"]
    assert stats["ARS"]["home_factor"] == pytest.approx(0.096, abs=1e-3)


def test_calculate_team_actual_stats_with_provisional():
    fixtures = [
        {
            "event": 1,
            "finished": False,
            "finished_provisional": True,
            "team_h": 1,
            "team_a": 6,
            "team_h_score": 2,
            "team_a_score": 1,
        }
    ]
    stats = calculate_team_actual_stats(fixtures)
    assert stats["ARS"]["matches_played"] == 1
    assert stats["ARS"]["goals_scored"] == 2
    assert stats["CHE"]["matches_played"] == 1
    assert stats["CHE"]["goals_scored"] == 1


def test_fpl_client_get_match_records_provisional(tmp_path: Path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    fake_bootstrap = {
        "elements": [
            {"id": 101, "team": 1},
            {"id": 202, "team": 6},
        ]
    }
    (cache_dir / "bootstrap_static.json").write_text(json.dumps(fake_bootstrap), encoding="utf-8")

    fixtures = [
        {
            "id": 1,
            "event": 1,
            "finished": True,
            "finished_provisional": False,
            "team_h": 1,
            "team_a": 6,
            "team_h_score": 1,
            "team_a_score": 0,
        },
        {
            "id": 2,
            "event": 2,
            "finished": False,
            "finished_provisional": True,
            "team_h": 6,
            "team_a": 1,
            "team_h_score": 3,
            "team_a_score": 2,
        },
    ]
    (cache_dir / "fixtures.json").write_text(json.dumps(fixtures), encoding="utf-8")

    client = FPLClient(cache_dir=cache_dir)
    records = client.get_match_records(offline=True)

    assert len(records) == 2
    assert records[0]["fixture_id"] == 1
    assert records[0]["is_provisional"] is False
    assert records[1]["fixture_id"] == 2
    assert records[1]["is_provisional"] is True

