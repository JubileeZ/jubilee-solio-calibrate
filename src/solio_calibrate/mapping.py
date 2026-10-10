"""Bidirectional mapping between Solio 3-letter team codes and FPL API IDs."""

from typing import Any

# Map of Solio 3-letter code -> metadata including FPL ID and full club name
SOLIO_TEAMS: dict[str, dict[str, Any]] = {
    "ARS": {"fpl_id": 1, "short_name": "ARS", "name": "Arsenal"},
    "AVL": {"fpl_id": 2, "short_name": "AVL", "name": "Aston Villa"},
    "BOU": {"fpl_id": 3, "short_name": "BOU", "name": "Bournemouth"},
    "BRE": {"fpl_id": 4, "short_name": "BRE", "name": "Brentford"},
    "BHA": {"fpl_id": 5, "short_name": "BHA", "name": "Brighton"},
    "CHE": {"fpl_id": 6, "short_name": "CHE", "name": "Chelsea"},
    "COV": {"fpl_id": 7, "short_name": "COV", "name": "Coventry City"},
    "CRY": {"fpl_id": 8, "short_name": "CRY", "name": "Crystal Palace"},
    "EVE": {"fpl_id": 9, "short_name": "EVE", "name": "Everton"},
    "FUL": {"fpl_id": 10, "short_name": "FUL", "name": "Fulham"},
    "HUL": {"fpl_id": 11, "short_name": "HUL", "name": "Hull City"},
    "IPS": {"fpl_id": 12, "short_name": "IPS", "name": "Ipswich Town"},
    "LEE": {"fpl_id": 13, "short_name": "LEE", "name": "Leeds"},
    "LIV": {"fpl_id": 14, "short_name": "LIV", "name": "Liverpool"},
    "MCI": {"fpl_id": 15, "short_name": "MCI", "name": "Man City"},
    "MUN": {"fpl_id": 16, "short_name": "MUN", "name": "Man Utd"},
    "NEW": {"fpl_id": 17, "short_name": "NEW", "name": "Newcastle"},
    "NFO": {"fpl_id": 18, "short_name": "NFO", "name": "Nott'm Forest"},
    "TOT": {"fpl_id": 19, "short_name": "TOT", "name": "Spurs"},
    "SUN": {"fpl_id": 20, "short_name": "SUN", "name": "Sunderland"},
}

_FPL_ID_TO_CODE: dict[int, str] = {
    info["fpl_id"]: code for code, info in SOLIO_TEAMS.items()
}


def get_all_solio_codes() -> list[str]:
    """Return all supported Solio 3-letter team codes."""
    return list(SOLIO_TEAMS.keys())


def code_to_fpl_id(code: str) -> int:
    """Convert Solio 3-letter code to official FPL team ID."""
    code_upper = code.upper()
    if code_upper not in SOLIO_TEAMS:
        raise KeyError(f"Unknown Solio team code: {code}")
    return SOLIO_TEAMS[code_upper]["fpl_id"]


def fpl_id_to_code(fpl_id: int) -> str:
    """Convert official FPL team ID to Solio 3-letter code."""
    if fpl_id not in _FPL_ID_TO_CODE:
        raise KeyError(f"Unknown FPL team ID: {fpl_id}")
    return _FPL_ID_TO_CODE[fpl_id]
