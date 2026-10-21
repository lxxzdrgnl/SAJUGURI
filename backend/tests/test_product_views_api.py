"""POST /api/products/views — 게스트/로그인 기록, 잘못된 입력 400, IP 레이트 리밋 429."""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from core.security import create_access_token
from db.models import ProductView
from main import app


def _client(token=None):
    cookies = {"access_token": token} if token else None
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://t", cookies=cookies)


async def _rows_and_cleanup(test_sessionmaker, product_id):
    async with test_sessionmaker() as db:
        rows = list((await db.execute(
            select(ProductView).where(ProductView.product_id == product_id)
        )).scalars().all())
        await db.execute(delete(ProductView).where(ProductView.product_id == product_id))
        await db.commit()
    return rows


async def test_record_view_guest(test_sessionmaker, override_db):
    async with _client() as c:
        r = await c.post("/api/products/views", json={"product_id": "reunion"})
    assert r.status_code == 204, r.text
    rows = await _rows_and_cleanup(test_sessionmaker, "reunion")
    assert len(rows) == 1 and rows[0].user_id is None


async def test_record_view_logged_in(db_user, test_sessionmaker, override_db):
    token = create_access_token(db_user.id)
    body = {"product_id": "daily_fortune", "day_stem": "임", "age_band": "25-29", "gender": "male"}
    async with _client(token) as c:
        r = await c.post("/api/products/views", json=body)
    assert r.status_code == 204, r.text
    rows = await _rows_and_cleanup(test_sessionmaker, "daily_fortune")
    assert len(rows) == 1
    assert rows[0].user_id == db_user.id and rows[0].day_stem == "임"


async def test_record_view_rejects_bad_id(override_db):
    async with _client() as c:
        r = await c.post("/api/products/views", json={"product_id": "DROP TABLE"})
    # 앱 전역 RequestValidationError 핸들러가 검증 실패를 400(VALIDATION_FAILED)으로 매핑
    assert r.status_code == 400


@pytest.mark.parametrize("extra", [
    {"gender": "other"}, {"gender": "남"}, {"day_stem": "자"}, {"day_stem": "임임"}, {"day_stem": "x"},
])
async def test_record_view_rejects_invalid_optional_fields(override_db, extra):
    async with _client() as c:
        r = await c.post("/api/products/views", json={"product_id": "reunion", **extra})
    assert r.status_code == 400


class _FakeRedis:
    def __init__(self, fail=False):
        self.counts, self.fail = {}, fail

    async def incr(self, key):
        if self.fail:
            raise ConnectionError("down")
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key, sec):
        return True


async def test_record_view_rate_limited(test_sessionmaker, override_db, monkeypatch):
    from routers import product_views
    monkeypatch.setattr(product_views, "VIEWS_PER_MINUTE", 2)
    monkeypatch.setattr(app.state, "arq", _FakeRedis(), raising=False)
    async with _client() as c:
        codes = [(await c.post("/api/products/views", json={"product_id": "rl_test"})).status_code for _ in range(3)]
    rows = await _rows_and_cleanup(test_sessionmaker, "rl_test")
    assert codes == [204, 204, 429]
    assert len(rows) == 2


async def test_record_view_fails_open_when_redis_down(test_sessionmaker, override_db, monkeypatch):
    monkeypatch.setattr(app.state, "arq", _FakeRedis(fail=True), raising=False)
    async with _client() as c:
        r = await c.post("/api/products/views", json={"product_id": "rl_open"})
    await _rows_and_cleanup(test_sessionmaker, "rl_open")
    assert r.status_code == 204
