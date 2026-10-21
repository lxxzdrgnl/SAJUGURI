"""상품 일러스트 생성 스크립트 (gpt-image-1 images.edit, 참조 스티커 기반).

사용:
    cd backend && uv run python scripts/generate_product_art.py [--only a,b] [--force] [--dry-run]

--dry-run 은 네트워크/API 키 없이 대상과 예상 비용만 출력한다.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
PROMPTS_PATH = SCRIPT_DIR / "product_art_prompts.json"
OUT_DIR = REPO_ROOT / "apps" / "web" / "public" / "products"
REF_PATHS = [
    REPO_ROOT / "apps" / "web" / "public" / "mascot" / name
    for name in ("fortune.png", "love.png", "thumbsup.png")
]

MODEL = "gpt-image-1"
SIZE = "1024x1024"
QUALITY = "medium"
# 추정치: gpt-image-1 medium 1024x1024 edit 1장 (참조 이미지 입력 토큰 포함), USD.
EST_COST_PER_IMAGE_USD = 0.07
TOTAL_BUDGET_USD = 10.0  # 재생성 포함 전체 누적 상한
DEFAULT_MAX_USD = 1.00  # 이번 실행 상한 (--max-usd)
SPEND_LOG = SCRIPT_DIR / ".product_art_spend.jsonl"


def load_prompts(path: Path = PROMPTS_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_prompt(data: dict, target: str) -> str:
    return f"{data['scenes'][target]} {data['style']}"


def parse_only(only: str | None, valid: list[str]) -> list[str]:
    """--only 값을 파싱. 알 수 없는 id가 있으면 ValueError."""
    if not only:
        return list(valid)
    ids = [s.strip() for s in only.split(",") if s.strip()]
    unknown = [i for i in ids if i not in valid]
    if unknown:
        raise ValueError(f"unknown target id(s): {', '.join(unknown)}")
    return ids


def plan(targets: list[str], out_dir: Path, force: bool) -> tuple[list[str], list[str]]:
    """(생성할 대상, 건너뛸 대상) 반환."""
    todo, skipped = [], []
    for t in targets:
        if (out_dir / f"{t}.png").exists() and not force:
            skipped.append(t)
        else:
            todo.append(t)
    return todo, skipped


def read_spend(log: Path = SPEND_LOG) -> float:
    """로그의 전체 누적 추정 비용(USD)."""
    if not log.exists():
        return 0.0
    total = 0.0
    for line in log.read_text(encoding="utf-8").splitlines():
        if line.strip():
            total += float(json.loads(line).get("usd", 0.0))
    return total


def append_spend(target: str, usd: float, ok: bool, error: str | None = None, log: Path = SPEND_LOG) -> None:
    rec = {"target": target, "usd": usd, "status": "ok" if ok else "error"}
    if error:
        rec["error"] = error
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def check_budget(n_images: int, run_spent: float, alltime: float, max_usd: float,
                 per_image: float = EST_COST_PER_IMAGE_USD, total: float = TOTAL_BUDGET_USD) -> str | None:
    """오류 사유 문자열 또는 None. n_images: 이번 실행에서 계획된 총 장수, run_spent: 이번 실행 누적."""
    eps = 1e-9
    if n_images * per_image > max_usd + eps:
        return f"plan ${n_images * per_image:.2f} exceeds --max-usd ${max_usd:.2f}"
    if alltime + n_images * per_image > total + eps:
        return f"all-time ${alltime:.2f} + plan ${n_images * per_image:.2f} exceeds total budget ${total:.2f}"
    return None


def would_exceed(run_spent: float, max_usd: float, per_image: float = EST_COST_PER_IMAGE_USD) -> bool:
    """다음 호출이 이번 실행 상한을 넘기는지."""
    return run_spent + per_image > max_usd + 1e-9


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="쉼표 구분 대상 id")
    ap.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")
    ap.add_argument("--max-usd", type=float, default=DEFAULT_MAX_USD, help="이번 실행 추정 비용 상한")
    ap.add_argument("--dry-run", action="store_true", help="호출 없이 대상·예상 비용만 출력")
    args = ap.parse_args(argv)

    data = load_prompts()
    try:
        targets = parse_only(args.only, list(data["scenes"]))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    todo, skipped = plan(targets, OUT_DIR, args.force)
    for t in skipped:
        print(f"skip   {t} (exists; use --force)")

    missing = [str(p) for p in REF_PATHS if not p.exists()]

    if args.dry_run:
        if missing:
            print(f"warning: missing reference images: {missing}", file=sys.stderr)
        for t in todo:
            rel = (OUT_DIR / f"{t}.png").relative_to(REPO_ROOT)
            print(f"would generate {t} -> {rel} (~${EST_COST_PER_IMAGE_USD:.2f})")
        print(
            f"[dry-run] {len(todo)} image(s), estimated total "
            f"${len(todo) * EST_COST_PER_IMAGE_USD:.2f} (model={MODEL}, {QUALITY}, {SIZE})"
        )
        print(f"[dry-run] all-time spend so far ~${read_spend():.2f} / ${TOTAL_BUDGET_USD:.2f}; --max-usd ${args.max_usd:.2f}")
        err = check_budget(len(todo), 0.0, read_spend(), args.max_usd)
        if err:
            print(f"[dry-run] WARNING: a real run would be refused: {err}")
        return 0

    if not todo:
        print("nothing to generate")
        return 0
    if not os.environ.get("OPENAI_API_KEY"):
        print("error: OPENAI_API_KEY is not set", file=sys.stderr)
        return 1
    if missing:
        print(f"error: missing reference images: {missing}", file=sys.stderr)
        return 1
    alltime = read_spend()
    err = check_budget(len(todo), 0.0, alltime, args.max_usd)
    if err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    print(f"all-time spend so far ~${alltime:.2f} / ${TOTAL_BUDGET_USD:.2f}")

    from openai import OpenAI

    client = OpenAI()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spent = 0.0
    failed = []
    for t in todo:
        if would_exceed(spent, args.max_usd):
            print(f"abort: next call would exceed --max-usd ${args.max_usd:.2f}", file=sys.stderr)
            failed.append(t)
            break
        files = [open(p, "rb") for p in REF_PATHS]
        spent += EST_COST_PER_IMAGE_USD  # 시도 자체를 비용으로 계산
        try:
            res = client.images.edit(
                model=MODEL,
                image=files,
                prompt=build_prompt(data, t),
                background="transparent",
                size=SIZE,
                quality=QUALITY,
            )
            b64 = res.data[0].b64_json if res.data else None
            if b64 is None:
                raise RuntimeError("response has no b64_json")
            (OUT_DIR / f"{t}.png").write_bytes(base64.b64decode(b64))
            append_spend(t, EST_COST_PER_IMAGE_USD, True)
            print(f"done   {t} (~${EST_COST_PER_IMAGE_USD:.2f}, run ~${spent:.2f})")
        except Exception as e:  # noqa: BLE001
            append_spend(t, EST_COST_PER_IMAGE_USD, False, str(e))
            failed.append(t)
            print(f"FAILED {t}: {e} (counted ~${EST_COST_PER_IMAGE_USD:.2f}, run ~${spent:.2f})", file=sys.stderr)
        finally:
            for f in files:
                f.close()
    print(f"run spend ~${spent:.2f}; all-time ~${read_spend():.2f} / ${TOTAL_BUDGET_USD:.2f}")
    if failed:
        print(f"failed/aborted: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
