from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import jwt
import pytest

from app.core.config import settings
from app.db.base import Base
from app.db import session as db_session_module
from app.main import app


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _register_user(
    client: httpx.AsyncClient,
    *,
    email: str = "user@example.com",
    password: str = "StrongPassword123!",
    full_name: str = "SafeFlow User",
) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "fullName": full_name,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def isolated_auth_history_db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_path = tmp_path / "auth-history-test.db"
    original_database_url = settings.database_url

    monkeypatch.setattr(settings, "database_url", f"sqlite:///{database_path.as_posix()}")
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "test-secret-key-that-is-long-enough-for-hs256-validation",
    )
    monkeypatch.setattr(settings, "jwt_algorithm", "HS256")
    monkeypatch.setattr(settings, "access_token_expire_minutes", 60)
    monkeypatch.setattr(settings, "analysis_mode", "mock")
    monkeypatch.setattr(settings, "ocr_enabled", True)

    engine = db_session_module.init_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    db_session_module.init_engine(original_database_url)


@pytest.mark.anyio
async def test_register_success_returns_user_and_token(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "USER@example.com",
                "password": "StrongPassword123!",
                "fullName": "Example User",
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["accessToken"]
    assert payload["tokenType"] == "bearer"
    assert payload["user"]["email"] == "user@example.com"
    assert payload["user"]["fullName"] == "Example User"
    assert "password" not in payload["user"]


@pytest.mark.anyio
async def test_duplicate_email_is_rejected(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await _register_user(client)
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "StrongPassword123!",
                "fullName": "Someone Else",
            },
        )

    assert response.status_code == 409
    assert response.json()["errorCode"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.anyio
async def test_login_success_returns_user_and_token(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await _register_user(client, email="login@example.com")
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "login@example.com",
                "password": "StrongPassword123!",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accessToken"]
    assert payload["user"]["email"] == "login@example.com"


@pytest.mark.anyio
async def test_login_with_wrong_password_is_rejected(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await _register_user(client, email="wrong@example.com")
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongPassword123!",
            },
        )

    assert response.status_code == 401
    assert response.json()["errorCode"] == "INVALID_CREDENTIALS"


@pytest.mark.anyio
async def test_me_returns_current_user_with_valid_token(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        register_payload = await _register_user(client, email="me@example.com")
        response = await client.get(
            "/api/auth/me",
            headers=_auth_headers(register_payload["accessToken"]),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "me@example.com"
    assert payload["role"] == "user"


@pytest.mark.anyio
async def test_me_without_token_is_rejected(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["errorCode"] == "UNAUTHORIZED"


@pytest.mark.anyio
async def test_expired_token_is_rejected(isolated_auth_history_db: None) -> None:
    expired_token = jwt.encode(
        {
            "sub": "expired-user",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/auth/me", headers=_auth_headers(expired_token))

    assert response.status_code == 401
    assert response.json()["errorCode"] == "TOKEN_EXPIRED"


@pytest.mark.anyio
async def test_empty_history_returns_empty_items(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        register_payload = await _register_user(client, email="history-empty@example.com")
        response = await client.get(
            "/api/analysis-history",
            headers=_auth_headers(register_payload["accessToken"]),
        )

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}


@pytest.mark.anyio
async def test_unauthenticated_history_is_rejected(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analysis-history")

    assert response.status_code == 401
    assert response.json()["errorCode"] == "UNAUTHORIZED"


@pytest.mark.anyio
async def test_authenticated_analysis_saves_history_record(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        register_payload = await _register_user(client, email="history-save@example.com")
        analysis_response = await client.post(
            "/api/scam-analysis",
            json={
                "inputType": "text",
                "content": "Urgent: verify now and use the new bank details immediately.",
            },
            headers=_auth_headers(register_payload["accessToken"]),
        )

        history_response = await client.get(
            "/api/analysis-history",
            headers=_auth_headers(register_payload["accessToken"]),
        )

    assert analysis_response.status_code == 200
    analysis_payload = analysis_response.json()
    history_payload = history_response.json()
    assert history_payload["total"] == 1
    assert history_payload["items"][0]["analysisId"] == analysis_payload["analysisId"]
    assert history_payload["items"][0]["riskScore"] == analysis_payload["riskScore"]
    assert history_payload["items"][0]["evidence"]
    assert isinstance(history_payload["items"][0]["evidence"], list)
    assert isinstance(history_payload["items"][0]["evidence"][0], dict)


@pytest.mark.anyio
async def test_anonymous_analysis_does_not_create_history(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        anonymous_analysis_response = await client.post(
            "/api/scam-analysis",
            json={
                "inputType": "text",
                "content": "Urgent: pay the invoice immediately.",
            },
        )
        register_payload = await _register_user(client, email="history-anon@example.com")
        history_response = await client.get(
            "/api/analysis-history",
            headers=_auth_headers(register_payload["accessToken"]),
        )

    assert anonymous_analysis_response.status_code == 200
    assert history_response.status_code == 200
    assert history_response.json()["total"] == 0


@pytest.mark.anyio
async def test_history_item_access_is_scoped_to_owner(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        owner = await _register_user(client, email="owner@example.com")
        other_user = await _register_user(client, email="other@example.com")

        analysis_response = await client.post(
            "/api/scam-analysis",
            json={
                "inputType": "text",
                "content": "Please transfer the payment to the new bank details immediately.",
            },
            headers=_auth_headers(owner["accessToken"]),
        )
        analysis_id = analysis_response.json()["analysisId"]

        detail_response = await client.get(
            f"/api/analysis-history/{analysis_id}",
            headers=_auth_headers(other_user["accessToken"]),
        )
        delete_response = await client.delete(
            f"/api/analysis-history/{analysis_id}",
            headers=_auth_headers(other_user["accessToken"]),
        )

    assert detail_response.status_code == 404
    assert detail_response.json()["errorCode"] == "HISTORY_ITEM_NOT_FOUND"
    assert delete_response.status_code == 404
    assert delete_response.json()["errorCode"] == "HISTORY_ITEM_NOT_FOUND"


@pytest.mark.anyio
async def test_owner_can_delete_history_item(isolated_auth_history_db: None) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        owner = await _register_user(client, email="delete-owner@example.com")
        analysis_response = await client.post(
            "/api/scam-analysis",
            json={
                "inputType": "text",
                "content": "Urgent: update the beneficiary bank account for this payment.",
            },
            headers=_auth_headers(owner["accessToken"]),
        )
        analysis_id = analysis_response.json()["analysisId"]

        delete_response = await client.delete(
            f"/api/analysis-history/{analysis_id}",
            headers=_auth_headers(owner["accessToken"]),
        )
        history_response = await client.get(
            "/api/analysis-history",
            headers=_auth_headers(owner["accessToken"]),
        )

    assert delete_response.status_code == 200
    assert delete_response.json() == {"success": True, "message": None}
    assert history_response.json()["total"] == 0