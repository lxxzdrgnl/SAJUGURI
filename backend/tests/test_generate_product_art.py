import importlib.util
from pathlib import Path

import pytest

_p = Path(__file__).resolve().parent.parent / "scripts" / "generate_product_art.py"
_spec = importlib.util.spec_from_file_location("generate_product_art", _p)
gpa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gpa)

EXPECTED = {
    "daily_fortune", "guriguri_counsel", "saju_report", "compatibility", "question",
    "some_heart", "reunion", "career_move", "money_flow", "empty", "login", "search_empty",
}


def test_targets_match_json():
    scenes = gpa.load_prompts()["scenes"]
    assert len(scenes) == 12
    assert set(scenes) == EXPECTED


def test_only_rejects_unknown():
    valid = list(gpa.load_prompts()["scenes"])
    assert gpa.parse_only("reunion, money_flow", valid) == ["reunion", "money_flow"]
    with pytest.raises(ValueError):
        gpa.parse_only("reunion,nope", valid)


def test_plan_skips_existing_unless_force(tmp_path):
    (tmp_path / "reunion.png").write_bytes(b"x")
    assert gpa.plan(["reunion", "empty"], tmp_path, False) == (["empty"], ["reunion"])
    assert gpa.plan(["reunion", "empty"], tmp_path, True) == (["reunion", "empty"], [])
