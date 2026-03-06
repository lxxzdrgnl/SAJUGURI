# Frontend - Vue.js 3 웹앱

사용자 입력 수신 및 AI가 생성한 동적 UI를 렌더링하는 웹 애플리케이션입니다.

---

## 핵심 컴포넌트

| 컴포넌트 | 역할 |
|---|---|
| `DynamicInputForm` | 생년월일시·음양력·고민 입력 수집 |
| `HeadlineTabBar` | AI가 생성한 10개 결론형 헤드라인을 탭으로 표시 |
| `StreamingViewer` | 선택된 탭의 상세 내용을 실시간 스트리밍 출력 |

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| Framework | Vue.js 3 + Nuxt.js |
| 상태관리 | Pinia |
| 스타일 | Tailwind CSS |
| 언어 | TypeScript |
| 스트리밍 | Server-Sent Events (SSE) |

---

## 실행

### 로컬 개발

```bash
# 의존성 설치
pnpm install

# 개발 서버 실행
pnpm dev
# → http://localhost:3000
```

### Docker

```bash
# 루트 디렉토리에서
docker compose up frontend
```

---

## 구현 예정

> 현재 MCP 서버 및 Backend 구현 완료 후 진행 예정
