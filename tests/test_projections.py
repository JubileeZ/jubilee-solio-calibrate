from datetime import UTC, datetime
from pathlib import Path

import pytest

from solio_calibrate.projections import (
    get_projection_gameweeks,
    ingest_and_archive_projections,
    load_solio_projections,
)


@pytest.fixture
def sample_projection_csv(tmp_path: Path) -> Path:
    csv_file = tmp_path / "sample_solio.csv"
    csv_file.write_text(
        "Pos,ID,Name,BV,SV,Team,7_xMins,8_xMins,7_Pts,8_Pts\n"
        "G,1,Raya,6.1,6.1,Arsenal,90.0,90.0,4.5,4.2\n"
        "D,4,Gabriel,7.9,7.9,Arsenal,90.0,90.0,5.1,4.9\n"
        "M,12,Saka,9.6,9.6,Arsenal,85.0,85.0,6.2,5.8\n"
        "F,411,Haaland,15.6,15.6,Man City,90.0,90.0,8.1,7.5\n",
        encoding="utf-8",
    )
    return csv_file


def test_load_solio_projections_valid(sample_projection_csv: Path):
    df = load_solio_projections(sample_projection_csv)
    assert len(df) == 4
    assert list(df["Pos"]) == ["G", "D", "M", "F"]
    assert "7_Pts" in df.columns
    assert "8_Pts" in df.columns
    assert df.iloc[0]["ID"] == 1


def test_load_solio_projections_normalizes_positions(tmp_path: Path):
    csv_file = tmp_path / "long_positions.csv"
    csv_file.write_text(
        "Pos,ID,Name,BV,SV,Team,7_xMins,7_Pts\n"
        "GKP,1,Raya,6.1,6.1,Arsenal,90.0,4.5\n"
        "DEF,4,Gabriel,7.9,7.9,Arsenal,90.0,5.1\n"
        "MID,12,Saka,9.6,9.6,Arsenal,85.0,6.2\n"
        "FWD,411,Haaland,15.6,15.6,Man City,90.0,8.1\n",
        encoding="utf-8",
    )
    df = load_solio_projections(csv_file)
    assert list(df["Pos"]) == ["G", "D", "M", "F"]


def test_load_solio_projections_missing_required_column(tmp_path: Path):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(
        "Pos,Name,BV,SV,Team,7_xMins,7_Pts\nG,Raya,6.1,6.1,Arsenal,90,4.5\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Missing required base columns"):
        load_solio_projections(csv_file)


def test_load_solio_projections_missing_pts_or_xmins(tmp_path: Path):
    csv_file = tmp_path / "bad_gws.csv"
    csv_file.write_text(
        "Pos,ID,Name,BV,SV,Team,7_xMins\nG,1,Raya,6.1,6.1,Arsenal,90\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="No Gameweek projection columns found"):
        load_solio_projections(csv_file)


def test_get_projection_gameweeks(sample_projection_csv: Path):
    df = load_solio_projections(sample_projection_csv)
    gws = get_projection_gameweeks(df)
    assert gws == [7, 8]


def test_ingest_and_archive_projections_new_and_deduplicate(sample_projection_csv: Path, tmp_path: Path):
    proj_dir = tmp_path / "projections"
    ts1 = datetime(2026, 10, 13, 10, 0, 0, tzinfo=UTC)

    # 1. Initial ingestion
    active, archived = ingest_and_archive_projections(
        sample_projection_csv, projections_dir=proj_dir, now=ts1
    )
    assert active == proj_dir / "solio_projections.csv"
    assert active.is_file()
    assert archived is None  # no prior version to archive

    # 2. Ingesting identical file (same content/hash) suppresses duplicate archive
    ts2 = datetime(2026, 10, 13, 10, 15, 0, tzinfo=UTC)
    active2, archived2 = ingest_and_archive_projections(
        sample_projection_csv, projections_dir=proj_dir, now=ts2
    )
    assert active2 == active
    assert archived2 is None
    archives = list((proj_dir / "archive").glob("*.csv"))
    assert len(archives) == 0

    # 3. Ingesting changed file archives prior version
    changed_file = tmp_path / "changed.csv"
    changed_file.write_text(
        "Pos,ID,Name,BV,SV,Team,7_xMins,7_Pts\n"
        "G,1,Raya,6.1,6.1,Arsenal,90.0,4.8\n",
        encoding="utf-8",
    )
    ts3 = datetime(2026, 10, 13, 11, 0, 0, tzinfo=UTC)
    active3, archived3 = ingest_and_archive_projections(
        changed_file, projections_dir=proj_dir, now=ts3
    )
    assert active3 == active
    assert archived3 == proj_dir / "archive" / "solio_projections_2026-10-13_11-00-00.csv"
    assert archived3.is_file()
    # Prior content was preserved in archive
    assert "Haaland" in archived3.read_text(encoding="utf-8")
    assert "Haaland" not in active3.read_text(encoding="utf-8")
