"""
신강/신약 8단계 분포 계산 스크립트.
무작위 생년월일시 N건으로 사주 score를 계산해서 각 단계 비율 산출.
결과를 StrengthChart.vue의 DIST 배열로 사용.

실행: uv run python scripts/compute_strength_dist.py
"""

import random
import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.calc.saju import calculate_saju
from engine.calc.ten_gods import calculate_ten_gods_distribution
from engine.calc.day_master_strength import analyze_day_master_strength

LEVELS = ['극약', '태약', '신약', '중화신약', '중화신강', '신강', '태강', '극왕']

# 통계적으로 의미 있는 샘플 수
N_SAMPLES = 10_000
SEED = 42

random.seed(SEED)


def random_birth() -> tuple[str, str | None, str]:
    year  = random.randint(1930, 2005)
    month = random.randint(1, 12)
    # 월별 최대 일수 (윤년 단순화)
    max_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
    day   = random.randint(1, max_day)
    date  = f"{year:04d}-{month:02d}-{day:02d}"

    # 시주 없는 경우도 반영 (약 10%)
    if random.random() < 0.1:
        time = None
    else:
        hour   = random.randint(0, 23)
        minute = 0
        time = f"{hour:02d}:{minute:02d}"

    gender = random.choice(["male", "female"])
    return date, time, gender


def main():
    counter: Counter = Counter()
    errors = 0

    print(f"[샘플 {N_SAMPLES:,}건 계산 중...]")
    for i in range(N_SAMPLES):
        if i % 1000 == 0 and i > 0:
            print(f"  {i:,} / {N_SAMPLES:,} ({errors} 오류)")
        date, time, gender = random_birth()
        try:
            saju = calculate_saju(date, time, gender, "solar", False)
            dist = calculate_ten_gods_distribution(saju)
            strength = analyze_day_master_strength(saju, dist)
            counter[strength["level_8"]] += 1
        except Exception:
            errors += 1

    total = sum(counter.values())
    print(f"\n[완료] 유효 {total:,}건 / 오류 {errors}건\n")

    print("── 분포 결과 ──────────────────────")
    dist_values = []
    for level in LEVELS:
        cnt = counter.get(level, 0)
        pct = cnt / total * 100 if total else 0
        print(f"  {level:6s}: {cnt:5d}건 ({pct:.1f}%)")
        # 만명 단위로 환산 (최대값 기준 25로 정규화)
        dist_values.append(pct)

    # 최대값을 25로 정규화
    max_val = max(dist_values) if dist_values else 1
    normalized = [round(v / max_val * 25, 1) for v in dist_values]

    print("\n── StrengthChart.vue DIST 배열 ────")
    print(f"const DIST = {normalized}")
    print()
    print("── 백분율 기준 ──────────────────")
    rounded_pct = [round(v, 1) for v in dist_values]
    print(f"// 원본 퍼센트: {rounded_pct}")


if __name__ == "__main__":
    main()
