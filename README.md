# 인사이트 사주 (Insight Saju)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![Nuxt](https://img.shields.io/badge/Nuxt.js-3.0-00DC82?style=flat-square&logo=nuxt.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![OpenAI](https://img.shields.io/badge/GPT--4o-Planner-412991?style=flat-square&logo=openai&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_Sonnet-Writer-D97757?style=flat-square&logo=anthropic&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-FF6B35?style=flat-square&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-History-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Monorepo-2496ED?style=flat-square&logo=docker&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-3_Tier_Agent-black?style=flat-square&logoColor=white)

**AI가 당신의 사주(四柱)와 오늘의 고민을 함께 읽어드립니다.**

> "재물운" (X)
> "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)

---

## 사주팔자(四柱八字)란?

사주팔자는 태어난 **연·월·일·시** 네 기둥(四柱), 여덟 글자(八字)로 이루어진 동양 명리학의 핵심입니다.
수천 년의 역사를 가진 이 체계는 개인의 타고난 기질, 인생의 흐름, 대인관계, 재물운 등을 분석하는 데 활용됩니다.

| 기둥 | 구성 | 의미 |
|---|---|---|
| 연주(年柱) | 태어난 해의 천간·지지 | 조상·초년운 (0~15세) |
| 월주(月柱) | 태어난 달의 천간·지지 | 부모·청년운 (16~30세) |
| 일주(日柱) | 태어난 날의 천간·지지 | 자신·배우자·중년운 (31~45세) |
| 시주(時柱) | 태어난 시의 천간·지지 | 자녀·말년운 (46세~) |

---

## 기존 사주 서비스의 한계

기존 서비스는 미리 작성된 정적 텍스트를 보여줄 뿐입니다.

- "재물운: 이달은 지출을 조심하세요." — 모든 사람에게 같은 말
- "연애운: 새로운 인연이 찾아올 수 있습니다." — 고민과 무관한 일반론

**인사이트 사주는 다릅니다.**

---

## 핵심 컨셉: Headline-Driven Insights

AI가 당신의 사주 계산 결과와 **지금 이 순간의 고민**을 함께 분석하여,
오직 당신만을 위한 결론형 헤드라인 10개를 생성합니다.

```
입력: 생년월일시 + "회사 상사와 갈등이 심해 이직을 고민 중입니다"

출력:
  탭 1. 경오일주, 강한 자존심이 상사의 권위와 정면 충돌하는 형국
  탭 2. 올해 역마살이 터지는 해 — 이직은 선택이 아닌 운명의 수순
  탭 3. 용신 화(火)의 기운이 강한 남쪽 계열 회사에서 빛을 발할 팔자
  탭 4. 월주 계묘, 동료보다 상사와의 관계에서 더 많이 소모되는 구조
  ...
```

단순한 카테고리가 아닌, 당신의 사주와 고민이 결합된 **살아있는 인사이트**입니다.

---

## 서비스 흐름

```
생년월일시 + 고민 입력
        │
        ▼ [분석 중...]
사주 계산 엔진 (만세력 기반)
  → 4기둥 · 오행 · 십성 · 신살 · 격국 · 용신 계산
        │
        ▼
AI Planner (GPT-4o)
  → 사주 데이터 + 고민을 결합해 10개 헤드라인 기획
        │
        ▼
AI Writer (Claude Sonnet)
  → 명리학 지식 베이스에서 근거를 찾아 각 탭 내용 집필
        │
        ▼ [완성된 리포트 수신]
탭 1 | 탭 2 | 탭 3 | ... | 탭 10
  클릭하면 즉시 전환 — 일반 웹사이트처럼
```

---

## 주요 분석 항목

| 항목 | 설명 |
|---|---|
| 사주팔자 | 연·월·일·시 4기둥 천간지지 계산 |
| 오행(五行) | 목·화·토·금·수 분포 및 강약 |
| 십성(十星) | 비견·식신·재성·관성·인성 등 10가지 관계 |
| 신살(神殺) | 역마살·도화살·천을귀인·공망 등 특수 기운 |
| 격국(格局) | 사주 전체 구조 패턴 (정관격·식신격 등 13종) |
| 용신(用神) | 사주의 균형을 잡아주는 핵심 오행 |
| 대운(大運) | 10년 단위 큰 흐름 |
| 세운·월운 | 해당 연도·월의 기운 |
| 궁합(宮合) | 두 사람의 사주 관계 분석 |

---

## 아키텍처

MCP(Model Context Protocol)로 **계산**과 **해석**을 철저히 분리한 3-Tier 구조입니다.

```
Frontend (Vue.js 3 / Nuxt.js)
        │
        ▼
Backend (FastAPI + LangGraph)
  ├─→ saju-calc MCP  ←  순수 계산만 담당 (숫자·간지 반환)
  └─→ saju-rag MCP   ←  해석 텍스트만 담당 (명리학 지식 RAG)
```

| 레이어 | 링크 | 역할 |
|---|---|---|
| Frontend | [frontend/](./frontend) | Vue.js 3 + Nuxt.js 탭 UI |
| Backend | [backend/](./backend) | FastAPI + AI Agent 오케스트레이션 |
| Saju-Calc MCP | [mcp-servers/saju-calc/](./mcp-servers/saju-calc) | 만세력 계산 엔진 |
| Saju-RAG MCP | [mcp-servers/saju-rag/](./mcp-servers/saju-rag) | 명리학 지식 RAG |

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.10+, TypeScript |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain / LangGraph, MCP SDK |
| AI / LLM | GPT-4o (Planner), Claude Sonnet (Writer) |
| Database | ChromaDB (Vector DB), PostgreSQL (이력) |
| Package Manager | uv (Python), pnpm (Node.js) |
| DevOps | Docker, Docker Compose, MCP Inspector |

---

## 빠른 시작

### Docker (전체 스택)

```bash
# .env 설정
cp .env.example .env
# OPENAI_API_KEY, ANTHROPIC_API_KEY 입력

# 전체 서비스 실행
docker compose up -d

# 서비스 포트
#   frontend   → http://localhost:3000
#   backend    → http://localhost:8000
#   saju-calc  → http://localhost:8001
#   saju-rag   → http://localhost:8002
```

### 로컬 개발 (saju-calc MCP)

```bash
# uv 설치 (최초 1회)
curl -LsSf https://astral.sh/uv/install.sh | sh

cd mcp-servers/saju-calc

# 의존성 설치
uv sync --group dev

# MCP Inspector로 개발 테스트
uv run fastmcp dev main.py

# 단위 테스트
uv run pytest tests/
```
