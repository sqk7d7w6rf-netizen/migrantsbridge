"""Basic smoke tests for the FastAPI application."""


class TestHealth:
    def test_health_endpoint_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_payload(self, client):
        body = client.get("/health").json()
        assert body["status"] == "healthy"
        assert body["app"] == "MigrantsBridge"
        assert "version" in body

    def test_openapi_schema_available(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200

    def test_integrations_router_registered(self, client):
        """Integrations routes must appear in the OpenAPI schema."""
        paths = client.get("/openapi.json").json()["paths"]
        integration_paths = [p for p in paths if "/integrations/" in p]
        assert len(integration_paths) >= 5
