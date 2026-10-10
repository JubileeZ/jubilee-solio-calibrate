"""FPL API client and actual team statistics aggregator with local caching."""

import json
import logging
from pathlib import Path
from typing import Any

import httpx

from solio_calibrate.mapping import SOLIO_TEAMS, fpl_id_to_code

logger = logging.getLogger(__name__)

BASE_URL = "https://fantasy.premierleague.com/api"
DEFAULT_CACHE_DIR = Path("data/cache")


class FPLClient:
    """Client for fetching and caching official Fantasy Premier League API endpoints."""

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        http_client: httpx.Client | None = None,
    ):
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self._http_client = http_client

    def _get_client(self) -> httpx.Client:
        if self._http_client is not None:
            return self._http_client
        return httpx.Client(timeout=30.0, headers={"User-Agent": "jubilee-solio-calibrate/0.1.0"})

    def _load_cache(self, filename: str) -> Any | None:
        path = self.cache_dir / filename
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to read cache file {path}: {e}")
        return None

    def _save_cache(self, filename: str, data: Any) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path = self.cache_dir / filename
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except (OSError, TypeError) as e:
            logger.warning(f"Failed to save cache file {path}: {e}")

    def get_bootstrap_static(self, force_refresh: bool = False) -> dict[str, Any]:
        """Fetch bootstrap-static metadata with caching."""
        cache_file = "bootstrap_static.json"
        if not force_refresh:
            cached = self._load_cache(cache_file)
            if cached is not None:
                return cached

        url = f"{BASE_URL}/bootstrap-static/"
        client = self._get_client()
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        self._save_cache(cache_file, data)
        return data

    def get_fixtures(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """Fetch all fixtures with caching."""
        cache_file = "fixtures.json"
        if not force_refresh:
            cached = self._load_cache(cache_file)
            if cached is not None:
                return cached

        url = f"{BASE_URL}/fixtures/"
        client = self._get_client()
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        self._save_cache(cache_file, data)
        return data

    def get_event_live(self, event: int, force_refresh: bool = False) -> dict[str, Any]:
        """Fetch live element stats for a specific gameweek with caching."""
        cache_file = f"event_live_{event}.json"
        if not force_refresh:
            cached = self._load_cache(cache_file)
            if cached is not None:
                return cached

        url = f"{BASE_URL}/event/{event}/live/"
        client = self._get_client()
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        self._save_cache(cache_file, data)
        return data

    def get_cached_fixtures(self) -> list[dict[str, Any]]:
        """Return cached fixtures if present on disk, otherwise empty list."""
        cached = self._load_cache("fixtures.json")
        return cached if isinstance(cached, list) else []

    def get_match_records(
        self,
        force_refresh: bool = False,
        max_gameweek: int | None = None,
        offline: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetch fixtures, bootstrap data, and live gameweek stats to build match-level records."""
        if offline:
            fixtures = self.get_cached_fixtures()
            bootstrap = self._load_cache("bootstrap_static.json") or {}
        else:
            fixtures = self.get_fixtures(force_refresh=force_refresh)
            bootstrap = self.get_bootstrap_static(force_refresh=force_refresh)

        # Player ID -> Solio team code
        player_to_team: dict[int, str] = {}
        for el in bootstrap.get("elements", []):
            try:
                player_to_team[el["id"]] = fpl_id_to_code(el["team"])
            except KeyError:
                continue

        finished_fixtures = [
            f
            for f in fixtures
            if (f.get("finished", False) or f.get("finished_provisional", False))
            and f.get("team_h_score") is not None
            and f.get("team_a_score") is not None
        ]
        if max_gameweek is not None:
            finished_fixtures = [
                f
                for f in finished_fixtures
                if f.get("event") is not None and f["event"] <= max_gameweek
            ]

        needed_events = sorted({f["event"] for f in finished_fixtures if f.get("event")})

        gw_team_xg: dict[int, dict[str, float]] = {}
        for ev in needed_events:
            try:
                if offline:
                    live_data = self._load_cache(f"event_live_{ev}.json") or {}
                else:
                    live_data = self.get_event_live(ev, force_refresh=force_refresh)
                gw_team_xg[ev] = {}
                for el in live_data.get("elements", []):
                    mins = el.get("stats", {}).get("minutes", 0)
                    if mins > 0:
                        eid = el.get("id")
                        team_code = player_to_team.get(eid)
                        if team_code:
                            xg = float(el.get("stats", {}).get("expected_goals", 0.0) or 0.0)
                            gw_team_xg[ev][team_code] = gw_team_xg[ev].get(team_code, 0.0) + xg
            except (httpx.HTTPError, OSError, ValueError) as e:
                logger.warning(f"Could not load live xG for gameweek {ev}: {e}")
                gw_team_xg[ev] = {}

        records = []
        for f in finished_fixtures:
            th_id = f["team_h"]
            ta_id = f["team_a"]
            try:
                th_code = fpl_id_to_code(th_id)
                ta_code = fpl_id_to_code(ta_id)
            except KeyError:
                continue

            ev = f.get("event") or 0
            h_score = int(f["team_h_score"])
            a_score = int(f["team_a_score"])
            h_xg = gw_team_xg.get(ev, {}).get(th_code, float(h_score))
            a_xg = gw_team_xg.get(ev, {}).get(ta_code, float(a_score))

            is_provisional = bool(
                f.get("finished_provisional", False) and not f.get("finished", False)
            )

            records.append({
                "fixture_id": f["id"],
                "event": ev,
                "home_team": th_code,
                "away_team": ta_code,
                "home_goals": h_score,
                "away_goals": a_score,
                "home_xg": h_xg,
                "away_xg": a_xg,
                "is_provisional": is_provisional,
            })

        return records

    def get_team_empirical_stats(
        self,
        force_refresh: bool = False,
        max_gameweek: int | None = None,
        pseudo_matches: float = 3.0,
        clamp_min: float = 0.65,
        clamp_max: float = 1.35,
        home_factor: float | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Fetch fixtures and live gameweek stats and calculate empirical form."""
        match_records = self.get_match_records(
            force_refresh=force_refresh, max_gameweek=max_gameweek
        )
        return calculate_team_empirical_form(
            match_records,
            pseudo_matches=pseudo_matches,
            clamp_min=clamp_min,
            clamp_max=clamp_max,
            home_factor=home_factor,
        )

    def get_team_actual_stats(
        self,
        force_refresh: bool = False,
        max_gameweek: int | None = None,
        recent_gw_count: int = 5,
    ) -> dict[str, dict[str, float]]:
        """Fetch fixtures and calculate actual goal stats per team."""
        fixtures = self.get_fixtures(force_refresh=force_refresh)
        return calculate_team_actual_stats(
            fixtures, max_gameweek=max_gameweek, recent_gw_count=recent_gw_count
        )


def calculate_team_actual_stats(
    fixtures: list[dict[str, Any]],
    max_gameweek: int | None = None,
    recent_gw_count: int = 5,
) -> dict[str, dict[str, float]]:
    """Aggregate finished fixture outcomes into per-team goal scoring and conceding rates.

    Args:
        fixtures: List of FPL fixture dicts.
        max_gameweek: Optional upper bound gameweek to include.
        recent_gw_count: Number of recent gameweeks to calculate recent form.

    Returns:
        Mapping of Solio 3-letter team codes to their computed performance metrics.
    """
    finished_fixtures = []
    for f in fixtures:
        if not (f.get("finished", False) or f.get("finished_provisional", False)):
            continue
        if f.get("team_h_score") is None or f.get("team_a_score") is None:
            continue
        gw = f.get("event")
        if gw is not None and max_gameweek is not None and gw > max_gameweek:
            continue
        finished_fixtures.append(f)

    max_gw = 0
    for f in finished_fixtures:
        gw = f.get("event")
        if gw and gw > max_gw:
            max_gw = gw
    recent_start_gw = max(1, max_gw - recent_gw_count + 1) if max_gw > 0 else 1

    # Initialize stats containers for each Solio team
    raw_stats: dict[str, dict[str, Any]] = {}
    for code in SOLIO_TEAMS:
        raw_stats[code] = {
            "matches_played": 0,
            "goals_scored": 0,
            "goals_conceded": 0,
            "home_matches": 0,
            "home_goals": 0,
            "home_conceded": 0,
            "away_matches": 0,
            "away_goals": 0,
            "away_conceded": 0,
            "recent_matches": 0,
            "recent_goals": 0,
            "recent_conceded": 0,
        }

    for f in finished_fixtures:
        th_id = f["team_h"]
        ta_id = f["team_a"]
        try:
            th_code = fpl_id_to_code(th_id)
            ta_code = fpl_id_to_code(ta_id)
        except KeyError:
            continue

        h_score = int(f["team_h_score"])
        a_score = int(f["team_a_score"])
        gw = f.get("event") or 0

        # Home team update
        th = raw_stats[th_code]
        th["matches_played"] += 1
        th["goals_scored"] += h_score
        th["goals_conceded"] += a_score
        th["home_matches"] += 1
        th["home_goals"] += h_score
        th["home_conceded"] += a_score

        # Away team update
        ta = raw_stats[ta_code]
        ta["matches_played"] += 1
        ta["goals_scored"] += a_score
        ta["goals_conceded"] += h_score
        ta["away_matches"] += 1
        ta["away_goals"] += a_score
        ta["away_conceded"] += h_score

        # Recent form update
        if gw >= recent_start_gw:
            th["recent_matches"] += 1
            th["recent_goals"] += h_score
            th["recent_conceded"] += a_score

            ta["recent_matches"] += 1
            ta["recent_goals"] += a_score
            ta["recent_conceded"] += h_score

    # Compute rates
    summary: dict[str, dict[str, float]] = {}
    for code, s in raw_stats.items():
        played = s["matches_played"]
        rec_played = s["recent_matches"]
        h_played = s["home_matches"]
        a_played = s["away_matches"]

        summary[code] = {
            "matches_played": played,
            "goals_scored": s["goals_scored"],
            "goals_conceded": s["goals_conceded"],
            "goals_per_match": (s["goals_scored"] / played) if played > 0 else 0.0,
            "conceded_per_match": (s["goals_conceded"] / played) if played > 0 else 0.0,
            "recent_matches": rec_played,
            "recent_goals_per_match": (s["recent_goals"] / rec_played) if rec_played > 0 else 0.0,
            "recent_conceded_per_match": (
                (s["recent_conceded"] / rec_played) if rec_played > 0 else 0.0
            ),
            "home_goals_per_match": (s["home_goals"] / h_played) if h_played > 0 else 0.0,
            "home_conceded_per_match": (s["home_conceded"] / h_played) if h_played > 0 else 0.0,
            "away_goals_per_match": (s["away_goals"] / a_played) if a_played > 0 else 0.0,
            "away_conceded_per_match": (s["away_conceded"] / a_played) if a_played > 0 else 0.0,
        }

    return summary

from solio_calibrate.calibrate import calculate_team_empirical_form

__all__ = [
    "BASE_URL",
    "DEFAULT_CACHE_DIR",
    "FPLClient",
    "calculate_team_actual_stats",
    "calculate_team_empirical_form",
]
