# SajuNara - AI 사주 상담 서비스

## 1. 프로젝트 핵심 컨셉: "Headline-Driven Insights"

기존의 정적인 운세 서비스와 달리, AI가 사용자의 사주와 현재 고민을 분석하여 맞춤형 목차(헤드라인)를 생성하고 이를 탭 형식으로 제공하는 지능형 상담 리포트 서비스입니다.

> 예시: "재물운" (X) → "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)

---

## 2. 전체 시스템 아키텍처 (MCP 기반 에이전틱 구조)

이 프로젝트는 **Model Context Protocol(MCP)**을 사용하여 로직과 데이터를 철저히 분리한 3-Tier 에이전트 아키텍처를 따릅니다.

### Layer 1: Frontend (Vue.js 3 / Nuxt.js)
- **역할**: 사용자 입력 수신 및 완성된 리포트를 탭 UI로 렌더링.
- **UX 원칙**: 탭 클릭 시 추가 API 호출 없음. 이미 완성된 데이터를 즉시 전환 (일반 웹사이트처럼).
- **핵심 컴포넌트**:
  - **Dynamic Input Form**: 사주 계산에 필요한 정보(생년월일시, 음양력) 및 고민 내용 수집.
  - **Loading State**: 리포트 생성 중 로딩 표시.
  - **Headline Tab UI**: AI가 생성한 10개의 결론형 탭. 클릭 시 이미 완성된 내용으로 즉시 전환.

### Layer 2: Backend (FastAPI - AI Agent Brain)
- **역할**: 전체 워크플로우 제어 및 AI 에이전트 오케스트레이션.
- **처리 방식**: 10개 탭의 헤드라인과 상세 내용을 **한 번에 모두 생성**하여 완성된 JSON 반환.
- **에이전트 구성**:
  - **Planner Agent**: Saju-Calc MCP 결과 + 고민 → 10개 헤드라인 기획.
  - **Writer Agent**: Saju-RAG MCP에서 지식 조회 → 10개 탭 상세 내용 일괄 집필.
- **기술**: LangGraph 또는 LangChain을 활용한 에이전트 제어.

### Layer 3: MCP Servers (Tools & Data)
- **Saju-Calc MCP**: 수학적 계산 엔진. 입춘 시각, 절기, 동경 135도 보정 등을 적용하여 정확한 8글자 및 신살 산출.
- **Saju-RAG MCP**: 지식 베이스. 60갑자 일주론, 십성 해석, 신살 의미 등을 저장하고 Agent의 요청에 따라 관련 텍스트 검색.

---

## 3. 데이터 설계 (RAG Knowledge Base)

AI가 근거 있는 답변을 하기 위해 **Vector DB(ChromaDB)**에 저장될 데이터 구조입니다.

| 카테고리 | 데이터 항목 | 활용 예시 |
|---|---|---|
| 일주론 | 60갑자별 성격, 직업, 연애 특징 | "경오일주: 목표를 향해 질주하는 백마" |
| 십성(十星) | 비견, 겁재, 식신 등 10가지 관계론 | "비견이 많아 동료와의 경쟁이 치열한 상황" |
| 신살(神殺) | 역마살, 도화살, 화개살, 귀인 등 | "도화살의 매력을 유튜브로 발산할 운명" |
| 상황별 조언 | 이직, 재회, 금전 고민에 대한 현대적 해석 | "이별 후 재회 시 주의해야 할 사주적 특징" |

---

## 4. 상세 워크플로우 (Data Flow)

1. **입력 단계**: 사용자가 생년월일시와 "현재 회사 상사와 갈등이 심해 이직하고 싶다"는 고민 입력.
2. **분석 단계**:
   - Saju-Calc MCP 호출 → 사용자의 일주가 '경오(庚午)'임을 파악.
   - Planner Agent가 경오일주 특징과 직장 갈등 상황을 분석.
3. **기획 단계**: AI가 10개의 헤드라인 생성.
   - 탭 1: 본인의 강한 주관이 상사의 권위와 충돌하는 형국입니다.
   - 탭 2: 올해는 역마의 기운이 강해 이직을 하기에 최적의 타이밍...
4. **일괄 생성 단계**: Writer Agent가 Saju-RAG MCP에서 지식을 조회하여 **10개 탭 내용을 모두 한 번에 생성**.
5. **표시 단계**: 완성된 전체 리포트를 Frontend로 반환 → 사용자는 일반 웹사이트처럼 탭을 즉시 클릭해 전환.

> **UX 원칙**: 탭 클릭은 단순 뷰 전환. 추가 API 호출 없음. 실시간 스트리밍 불필요.

---

## 5. 최종 기술 스택

| 구분 | 기술 스택 |
|---|---|
| Language | Python 3.10+ (Main), TypeScript (Frontend) |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain/LangGraph, MCP SDK |
| AI / LLM | GPT-4o (Planner + Writer) |
| Database | ChromaDB (Vector), PostgreSQL (User History) |
| DevOps | Docker, MCP Inspector, Monorepo (Git) |

---

## 6. 프로젝트 구조 (Monorepo)

```
saju-ai-service/
├── /frontend      # Vue.js 웹앱 (Nuxt.js)
├── /backend       # FastAPI 에이전트 서버
└── /mcp-servers   # 독립된 MCP 서버들
    ├── /saju-calc     # 사주 계산 엔진
    └── /saju-rag      # RAG 지식 베이스
```

---

## 7. 개발 원칙

- MCP를 통해 로직(Backend)과 데이터(MCP Servers)를 철저히 분리한다.
- 스트리밍 응답을 기본으로 설계하여 사용자 체감 속도를 높인다.
- 헤드라인은 반드시 결론형 문장으로 생성한다 (단순 카테고리명 금지).
- 모든 명리 해석은 RAG 지식 베이스에 근거하여 생성한다.
