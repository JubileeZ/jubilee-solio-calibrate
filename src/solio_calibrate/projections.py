"""Routines for reading, validating, and archiving Solio player projections."""

import re
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

from solio_calibrate.io import calculate_file_sha256, format_archive_filename
from solio_calibrate.mapping import SOLIO_TEAMS

REQUIRED_BASE_COLUMNS = ["Pos", "ID", "Name", "BV", "SV", "Team"]
CANONICAL_PROJECTIONS_FILENAME = "solio_projections.csv"
POSITION_NORMALIZATION = {
    "GKP": "G",
    "GK": "G",
    "G": "G",
    "DEF": "D",
    "D": "D",
    "MID": "M",
    "M": "M",
    "FWD": "F",
    "F": "F",
}


def load_solio_projections(file_path: str | Path) -> pd.DataFrame:
    """Read and validate Solio player projection CSV export.

    Args:
        file_path: Path to Solio player projection CSV.

    Returns:
        DataFrame with normalized positions and validated GW columns.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If required base columns or gameweek columns are missing or malformed.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Projections file not found: {path}")

    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    missing_base = [c for c in REQUIRED_BASE_COLUMNS if c not in df.columns]
    if missing_base:
        raise ValueError(f"Missing required base columns in {path}: {missing_base}")

    # Identify gameweek columns
    gw_mins: set[int] = set()
    gw_pts: set[int] = set()
    for col in df.columns:
        if m := re.match(r"^(\d+)_xMins$", col):
            gw_mins.add(int(m.group(1)))
        elif m := re.match(r"^(\d+)_Pts$", col):
            gw_pts.add(int(m.group(1)))

    if not gw_pts or not gw_mins:
        raise ValueError(f"No Gameweek projection columns found in {path}")

    common_gws = gw_mins.intersection(gw_pts)
    if not common_gws:
        raise ValueError(f"No matching _xMins and _Pts Gameweek pairs found in {path}")

    # Validate and normalize positions
    df["Pos"] = df["Pos"].astype(str).str.strip().str.upper()
    invalid_pos = [p for p in df["Pos"] if p not in POSITION_NORMALIZATION]
    if invalid_pos:
        raise ValueError(f"Invalid position codes found: {set(invalid_pos)}")

    df["Pos"] = df["Pos"].map(POSITION_NORMALIZATION)

    # Validate team names/codes against SOLIO_TEAMS
    valid_team_names = {v["name"].lower(): k for k, v in SOLIO_TEAMS.items()}
    valid_team_codes = set(SOLIO_TEAMS.keys())
    for t in df["Team"]:
        clean_t = str(t).strip()
        if clean_t.upper() not in valid_team_codes and clean_t.lower() not in valid_team_names:
            raise ValueError(f"Unrecognized team name/code in projections: {clean_t}")

    # Ensure numeric ID, BV, SV
    df["ID"] = pd.to_numeric(df["ID"], errors="raise").astype(int)
    df["BV"] = pd.to_numeric(df["BV"], errors="coerce").fillna(0.0)
    df["SV"] = pd.to_numeric(df["SV"], errors="coerce").fillna(0.0)

    for gw in common_gws:
        df[f"{gw}_xMins"] = pd.to_numeric(df[f"{gw}_xMins"], errors="coerce").fillna(0.0)
        df[f"{gw}_Pts"] = pd.to_numeric(df[f"{gw}_Pts"], errors="coerce").fillna(0.0)

    return df


def get_projection_gameweeks(df: pd.DataFrame) -> list[int]:
    """Extract sorted list of gameweeks covered by the projection DataFrame."""
    gws: list[int] = []
    for col in df.columns:
        if m := re.match(r"^(\d+)_Pts$", col):
            gws.append(int(m.group(1)))
    return sorted(gws)


def ingest_and_archive_projections(
    input_path: str | Path,
    projections_dir: str | Path = Path("data/projections"),
    now: datetime | None = None,
) -> tuple[Path, Path | None]:
    """Ingest a Solio projection CSV, archiving previous active projection if content changed.

    Deduplication: If active projection already exists and has identical SHA256 content
    to the new input, archiving is suppressed. Redundant archive snapshots with identical
    hashes are also suppressed.

    Args:
        input_path: Source CSV to ingest.
        projections_dir: Directory where active projection and archive/ live.
        now: Optional datetime for deterministic testing.

    Returns:
        Tuple of (active_projection_path, archived_path_or_none).
    """
    src = Path(input_path).resolve()
    target_dir = Path(projections_dir)
    target_active = (target_dir / CANONICAL_PROJECTIONS_FILENAME).resolve()

    if not src.is_file():
        raise FileNotFoundError(f"Projections input file not found: {src}")

    # Validate schema
    load_solio_projections(src)

    target_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = target_dir / "archive"

    if src == target_active:
        return target_active, None

    archived_path: Path | None = None
    if target_active.exists():
        src_hash = calculate_file_sha256(src)
        active_hash = calculate_file_sha256(target_active)
        if src_hash != active_hash:
            archive_dir.mkdir(parents=True, exist_ok=True)
            existing_archives = sorted(archive_dir.glob("solio_projections_*.csv"))
            if not existing_archives or calculate_file_sha256(existing_archives[-1]) != active_hash:
                archived_path = archive_dir / format_archive_filename("solio_projections", now)
                shutil.copy2(target_active, archived_path)
        else:
            # Identical content, no copy or archive needed
            return target_active, None

    shutil.copy2(src, target_active)
    return target_active, archived_path
