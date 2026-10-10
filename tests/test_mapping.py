import pytest

from solio_calibrate.mapping import (
    code_to_fpl_id,
    fpl_id_to_code,
    get_all_solio_codes,
)


def test_all_20_solio_teams_defined():
    codes = get_all_solio_codes()
    assert len(codes) == 20
    assert "ARS" in codes
    assert "MCI" in codes
    assert "LIV" in codes
    assert "COV" in codes
    assert "SUN" in codes


def test_code_to_fpl_id():
    assert code_to_fpl_id("ARS") == 1
    assert code_to_fpl_id("AVL") == 2
    assert code_to_fpl_id("MCI") == 15
    assert code_to_fpl_id("SUN") == 20


def test_code_to_fpl_id_invalid():
    with pytest.raises(KeyError, match="Unknown Solio team code"):
        code_to_fpl_id("XYZ")


def test_fpl_id_to_code():
    assert fpl_id_to_code(1) == "ARS"
    assert fpl_id_to_code(15) == "MCI"


def test_fpl_id_to_code_invalid():
    with pytest.raises(KeyError, match="Unknown FPL team ID"):
        fpl_id_to_code(999)
