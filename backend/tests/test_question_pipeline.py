"""한줄 상담 파이프라인 단위 테스트."""

import pytest
from llm.reranker import rerank_chunks, build_question_query, ELEMENT_KEYWORDS


BIRTH = dict(
    birth_date="1990-03-15",
    birth_time="14:30",
    gender="male",
    calendar="solar",
)


class TestReranking:
    """rerank_chunks — 용신 boost / 기신 penalize."""

    def _make_chunk(self, doc: str, tags: str = "") -> dict:
        return {
            "id": "test",
            "document": doc,
            "metadata": {"interpretation_tags": tags},
            "distance": 0.5,
        }

    def test_yong_sin_boost_lowers_score(self):
        """용신(수) 포함 청크는 score가 내려간다 (더 우선)."""
        chunk = self._make_chunk("수기(水氣)가 강해지는 시기에 용기를 내세요")
        result = rerank_chunks([chunk], yong_sin=["수"], ji_sin=["화", "토"], category="general")
        # boost: 0.5 - 0.2 = 0.3
        assert result[0]["_rerank_score"] < 0.5

    def test_ji_sin_penalty_raises_score(self):
        """기신(화) 포함 청크는 score가 올라간다 (후순위)."""
        chunk = self._make_chunk("화기(火氣)로 승부를 걸어보세요")
        result = rerank_chunks([chunk], yong_sin=["수"], ji_sin=["화", "토"], category="general")
        # penalty: 0.5 + 0.3 = 0.8
        assert result[0]["_rerank_score"] > 0.5

    def test_category_bonus_lowers_score(self):
        """category 매칭 interpretation_tag 포함 시 score 추가 감소."""
        chunk = self._make_chunk("직업 변화", tags="career_change,promotion")
        result = rerank_chunks([chunk], yong_sin=[], ji_sin=[], category="career")
        assert result[0]["_rerank_score"] < 0.5

    def test_ordering_yong_before_ji(self):
        """용신 청크가 기신 청크보다 앞에 온다."""
        good = self._make_chunk("수기 관련 조언")
        bad  = self._make_chunk("화기 관련 일반론")
        result = rerank_chunks([bad, good], yong_sin=["수"], ji_sin=["화"], category="general")
        assert "수기" in result[0]["document"]

    def test_chunk_with_both_yong_and_ji_gets_boost_not_penalty(self):
        """용신과 기신 키워드 모두 포함 시 boost만 적용 (penalty 무시)."""
        chunk = self._make_chunk("수기가 강하면 화기를 억제한다")
        result = rerank_chunks([chunk], yong_sin=["수"], ji_sin=["화"], category="general")
        # 용신 boost만: 0.5 - 0.2 = 0.3 (penalty +0.3 미적용)
        assert result[0]["_rerank_score"] < 0.5

    def test_returns_max_four_chunks(self):
        """최대 4개까지만 반환."""
        chunks = [self._make_chunk(f"내용 {i}") for i in range(10)]
        result = rerank_chunks(chunks, yong_sin=[], ji_sin=[], category="general")
        assert len(result) <= 4

    def test_empty_input_returns_empty(self):
        result = rerank_chunks([], yong_sin=["수"], ji_sin=["화"], category="general")
        assert result == []


class TestQueryBuilder:
    """build_question_query — question + category + core_keywords 조합."""

    def test_includes_question(self):
        q = build_question_query("이직해도 될까요?", "career", ["정관", "식신"])
        assert "이직" in q

    def test_includes_category_keyword(self):
        q = build_question_query("어떻게 될까요?", "career", [])
        assert "직업" in q or "career" in q

    def test_includes_core_keywords(self):
        q = build_question_query("질문", "general", ["정관", "역마살"])
        assert "정관" in q

    def test_core_keywords_capped_at_three(self):
        keywords = ["a", "b", "c", "d", "e"]
        q = build_question_query("질문", "general", keywords)
        # 쿼리에 4번째 이후 키워드가 없어야 함
        assert "d" not in q
        assert "e" not in q
