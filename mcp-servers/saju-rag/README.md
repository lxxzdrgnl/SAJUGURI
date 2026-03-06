# Saju-RAG MCP

명리학 **지식 베이스 RAG** MCP 서버.

saju-calc가 계산한 구조 데이터를 바탕으로, 관련 명리 해석 텍스트를 Vector DB에서 검색해 반환합니다.

---

## 설계 원칙

- **해석만, 계산 없음**: saju-calc의 계산 결과를 받아 관련 지식을 검색
- **RAG 기반**: ChromaDB에 저장된 명리학 지식을 시맨틱 검색
- **근거 있는 해석**: 모든 텍스트는 지식 베이스에 기반

---

## 지식 베이스 구성 (ChromaDB)

| 카테고리 | 데이터 예시 |
|---|---|
| 일주론 | 60갑자별 성격, 직업, 연애 특징 |
| 십성 해석 | 비견/겁재/식신 등 10가지 의미 |
| 신살 해석 | 역마살/도화살/화개살 등 의미·조언 |
| 격국 해석 | 정관격/식신격 등 13가지 성격·직업 |
| 용신 활용 | 오행별 색상·방향·직업 추천 |
| 상황별 조언 | 이직·재회·금전 현대적 해석 |
| 오행 성격 | 목/화/토/금/수 성격·특징 |

---

## 실행

### 로컬 개발

```bash
# uv 설치 (최초 1회)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync --group dev

# MCP Inspector로 개발 테스트
uv run fastmcp dev main.py
```

### Docker

```bash
# 루트 디렉토리에서
docker compose up saju-rag
```

---

## 구현 예정

> 현재 saju-calc 구현 완료 후 진행 예정
