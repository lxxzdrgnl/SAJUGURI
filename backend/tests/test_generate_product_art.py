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


def test_check_budget_caps():
    c = gpa.check_budget
    assert c(12, 0, 0.0, 1.0) is None  # 0.84
    assert "max-usd" in c(15, 0, 0.0, 1.0)  # 1.05
    assert "total budget" in c(12, 0, 9.5, 5.0)  # 9.5 + 0.84
    assert c(12, 0, 9.0, 5.0) is None  # 9.84


def test_would_exceed_counts_attempts():
    assert not gpa.would_exceed(0.0, 0.14)
    assert not gpa.would_exceed(0.07, 0.14)
    assert gpa.would_exceed(0.14, 0.14)


def test_spend_log_roundtrip(tmp_path):
    log = tmp_path / "s.jsonl"
    assert gpa.read_spend(log) == 0.0
    gpa.append_spend("a", 0.07, True, log=log)
    gpa.append_spend("b", 0.07, False, "boom", log=log)
    assert gpa.read_spend(log) == pytest.approx(0.14)
