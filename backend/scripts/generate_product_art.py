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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="쉼표 구분 대상 id")
    ap.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")
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

    if args.dry_run:
        for t in todo:
            rel = (OUT_DIR / f"{t}.png").relative_to(REPO_ROOT)
            print(f"would generate {t} -> {rel} (~${EST_COST_PER_IMAGE_USD:.2f})")
        print(
            f"[dry-run] {len(todo)} image(s), estimated total "
            f"${len(todo) * EST_COST_PER_IMAGE_USD:.2f} (model={MODEL}, {QUALITY}, {SIZE})"
        )
        return 0

    if not todo:
        print("nothing to generate")
        return 0
    if not os.environ.get("OPENAI_API_KEY"):
        print("error: OPENAI_API_KEY is not set", file=sys.stderr)
        return 1
    missing = [str(p) for p in REF_PATHS if not p.exists()]
    if missing:
        print(f"error: missing reference images: {missing}", file=sys.stderr)
        return 1

    from openai import OpenAI

    client = OpenAI()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spent = 0.0
    for t in todo:
        files = [open(p, "rb") for p in REF_PATHS]
        try:
            res = client.images.edit(
                model=MODEL,
                image=files,
                prompt=build_prompt(data, t),
                background="transparent",
                size=SIZE,
                quality=QUALITY,
            )
        finally:
            for f in files:
                f.close()
        (OUT_DIR / f"{t}.png").write_bytes(base64.b64decode(res.data[0].b64_json))
        spent += EST_COST_PER_IMAGE_USD
        print(f"done   {t} (~${EST_COST_PER_IMAGE_USD:.2f}, cumulative ~${spent:.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
