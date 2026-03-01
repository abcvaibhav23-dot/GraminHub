import httpx

from app.core.config import settings


def test_ai_search_disabled_returns_404(client):
    settings.AI_SEARCH_ENABLED = False
    settings.AI_SEARCH_ALLOWED_HOSTS = "testserver"

    res = client.post("/api/v2/ai/search", json={"query": "cement", "language": "english"})
    assert res.status_code == 404


def test_ai_search_enabled_missing_key_returns_503(client):
    settings.AI_SEARCH_ENABLED = True
    settings.AI_SEARCH_ALLOWED_HOSTS = "testserver"
    settings.OPENAI_API_KEY = ""

    res = client.post("/api/v2/ai/search", json={"query": "cement", "language": "english"})
    assert res.status_code == 503, res.text


def test_ai_search_returns_structured_json(client, monkeypatch):
    settings.AI_SEARCH_ENABLED = True
    settings.AI_SEARCH_ALLOWED_HOSTS = "testserver"
    settings.OPENAI_API_KEY = "sk-test"
    settings.OPENAI_BASE_URL = "https://api.openai.com/v1"
    settings.OPENAI_MODEL = "gpt-test"

    class FakeResponse:
        status_code = 200
        text = '{"ok": true}'

        def json(self):
            return {
                "output_text": (
                    '{"answer":"Try cement suppliers near Sonbhadra.","suggested_query":"cement sonbhadra",'
                    '"category_hint":"materials","tags":["cement","sonbhadra"]}'
                )
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, headers=None, json=None):
            assert url.endswith("/responses")
            assert headers and headers.get("Authorization", "").startswith("Bearer ")
            assert json and json.get("model") == "gpt-test"
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    res = client.post("/api/v2/ai/search", json={"query": "cement", "language": "english"})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["provider"] == "openai"
    assert body["category_hint"] == "materials"
    assert "cement" in body["suggested_query"]

