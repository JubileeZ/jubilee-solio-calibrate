"""I/O routines for reading and writing Solio team strength CSVs."""

from pathlib import Path

import pandas as pd

from solio_calibrate.mapping import SOLIO_TEAMS

REQUIRED_COLUMNS = ["Team", "Goals", "Goals Conceded"]


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
