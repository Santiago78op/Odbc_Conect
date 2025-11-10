"""
Tests para endpoints de la API
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

from src.main import app
from src.models import QueryResponse, AbendsResponse


@pytest.fixture
def mock_query_service():
    """Mock del QueryService"""
    service = MagicMock()
    service.test_connection = AsyncMock(return_value={
        "connected": True,
        "message": "Conexión exitosa"
    })
    service.execute_custom_query = AsyncMock(return_value=QueryResponse(
        success=True,
        data=[{"test": 1}],
        row_count=1,
        execution_time_ms=100.0
    ))
    service.get_abends = AsyncMock(return_value=AbendsResponse(
        success=True,
        abends=[{"program": "TEST"}],
        total=1,
        filters_applied={}
    ))
    return service


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test del endpoint raíz"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_ping_endpoint():
    """Test del endpoint de ping"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health/ping")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_endpoint(mock_query_service):
    """Test del health check"""
    with patch("src.api.health.get_query_service", return_value=mock_query_service):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/health/")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database_connected" in data


@pytest.mark.asyncio
async def test_execute_query_endpoint(mock_query_service):
    """Test del endpoint de ejecución de query"""
    with patch("src.api.query.get_query_service", return_value=mock_query_service):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/query/execute",
                json={
                    "query": "SELECT * FROM TEST",
                    "fetch_all": True
                }
            )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


@pytest.mark.asyncio
async def test_execute_query_dangerous_keyword():
    """Test que valida keywords peligrosas"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/query/execute",
            json={
                "query": "DROP TABLE TEST",
                "fetch_all": True
            }
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_abends_endpoint(mock_query_service):
    """Test del endpoint de abends"""
    with patch("src.api.query.get_query_service", return_value=mock_query_service):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/query/abends",
                params={"region": "PROD01", "limit": 50}
            )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "abends" in data
