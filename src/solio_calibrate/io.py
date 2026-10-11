"""I/O routines for reading and writing Solio team strength CSVs."""

import filecmp
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

from solio_calibrate.mapping import SOLIO_TEAMS

REQUIRED_COLUMNS = ["Team", "Goals", "Goals Conceded"]
CANONICAL_BASE_FILENAME = "team_strengths_base.csv"
CANONICAL_CALIBRATED_FILENAME = "team_strengths_calibrated.csv"


def format_archive_filename(prefix: str = "team_strengths", timestamp: datetime | None = None) -> str:
    """Format a canonical timestamped archive filename."""
    ts = (timestamp or datetime.now().astimezone()).strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}_{ts}.csv"


def load_solio_team_strengths(file_path: str | Path) -> pd.DataFrame:
    """Read and validate Solio team strength CSV export.

    Args:
        file_path: Path to Solio team strength CSV.

    Returns:
        DataFrame with columns ['Team', 'Goals', 'Goals Conceded'].

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If required columns or valid team codes are missing.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    # Read CSV, stripping possible BOM
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {path}: {missing}")

    # Reorder to canonical columns
    df = df[REQUIRED_COLUMNS].copy()

    # Validate team codes
    valid_codes = set(SOLIO_TEAMS.keys())
    for team in df["Team"]:
        if str(team).strip().upper() not in valid_codes:
            raise ValueError(f"Invalid team code encountered: {team}")

    # Validate numeric values
    df["Goals"] = pd.to_numeric(df["Goals"], errors="raise")
    df["Goals Conceded"] = pd.to_numeric(df["Goals Conceded"], errors="raise")

    return df


def save_solio_team_strengths(df: pd.DataFrame, file_path: str | Path) -> Path:
    """Save calibrated team strengths to CSV preserving exact 3-decimal schema.

    Args:
        df: DataFrame with ['Team', 'Goals', 'Goals Conceded'].
        file_path: Target output path.

    Returns:
        Path of written CSV.

    Raises:
        PermissionError: If target path points into a data/raw directory.
        ValueError: If required columns are missing.
    """
    path = Path(file_path).resolve()

    # Safety guard: never overwrite raw files
    if "data/raw" in path.as_posix().lower():
        raise PermissionError(f"Refusing to overwrite raw input CSV file: {path}")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for export: {missing}")

    output_df = df[REQUIRED_COLUMNS].copy()
    output_df["Team"] = output_df["Team"].astype(str).str.strip().str.upper()

    # Format numbers strictly to 3 decimal places
    output_df["Goals"] = output_df["Goals"].apply(lambda v: f"{float(v):.3f}")
    output_df["Goals Conceded"] = output_df["Goals Conceded"].apply(lambda v: f"{float(v):.3f}")

    path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(path, index=False, encoding="utf-8")
    return path


def ingest_and_archive_raw_input(
    input_path: str | Path,
    raw_dir: str | Path = Path("data/raw"),
    now: datetime | None = None,
) -> tuple[Path, Path | None]:
    """Ingest a raw Solio CSV as the active base strength, archiving prior base if content differs.

    Args:
        input_path: Path to the raw input CSV to ingest.
        raw_dir: Root raw directory containing active file and archive subfolder.
        now: Optional datetime for deterministic testing.

    Returns:
        Tuple of (active_base_strength_path, archived_path_or_none).
    """
    src = Path(input_path).resolve()
    target_raw = Path(raw_dir)
    target_active = (target_raw / CANONICAL_BASE_FILENAME).resolve()

    if not src.is_file():
        raise FileNotFoundError(f"Raw input file not found: {src}")

    # Validate that source conforms to schema
    load_solio_team_strengths(src)

    target_raw.mkdir(parents=True, exist_ok=True)
    archive_dir = target_raw / "archive"

    # If the source is already the active file, nothing to ingest/archive
    if src == target_active:
        return target_active, None

    archived_path: Path | None = None
    if target_active.exists() and not filecmp.cmp(src, target_active, shallow=False):
        archive_dir.mkdir(parents=True, exist_ok=True)
        archived_path = archive_dir / format_archive_filename("team_strengths_base", now)
        shutil.copy2(target_active, archived_path)

    shutil.copy2(src, target_active)
    return target_active, archived_path


def save_and_archive_calibrated_strengths(
    df: pd.DataFrame,
    output_path: str | Path | None = None,
    output_dir: str | Path = Path("data/output"),
    now: datetime | None = None,
) -> tuple[Path, Path | None]:
    """Save calibrated strengths. If output_path is None, saves to canonical path and archives copy.

    Args:
        df: DataFrame with ['Team', 'Goals', 'Goals Conceded'].
        output_path: Explicit override destination, if any.
        output_dir: Base output directory.
        now: Optional datetime for deterministic testing.

    Returns:
        Tuple of (written_path, archived_path_or_none).
    """
    if output_path is not None:
        target = Path(output_path)
        written = save_solio_team_strengths(df, target)
        return written, None

    out_base = Path(output_dir)
    canonical_path = out_base / CANONICAL_CALIBRATED_FILENAME
    archive_dir = out_base / "archive"

    written = save_solio_team_strengths(df, canonical_path)

    archive_dir.mkdir(parents=True, exist_ok=True)
    archived_path = archive_dir / format_archive_filename("team_strengths_calibrated", now)
    shutil.copy2(written, archived_path)

    return written, archived_path

