"""
Tests para modelos Pydantic
"""
import pytest
from pydantic import ValidationError

from src.models import (
    QueryRequest,
    AbendsFilterRequest,
    TableInfoRequest,
)


def test_query_request_valid():
    """Test de QueryRequest válido"""
    request = QueryRequest(
        query="SELECT * FROM CICS_ABENDS",
        params=["PROD01"],
        fetch_all=True
    )
    assert request.query == "SELECT * FROM CICS_ABENDS"
    assert request.params == ["PROD01"]
    assert request.fetch_all is True


def test_query_request_dangerous_keywords():
    """Test que valida keywords peligrosas"""
    dangerous_queries = [
        "DROP TABLE CICS_ABENDS",
        "DELETE FROM CICS_ABENDS",
        "TRUNCATE TABLE CICS_ABENDS",
    ]

    for query in dangerous_queries:
        with pytest.raises(ValidationError):
            QueryRequest(query=query)


def test_abends_filter_request():
    """Test de AbendsFilterRequest"""
    request = AbendsFilterRequest(
        region="PROD01",
        program="PAYROLL",
        limit=50
    )
    assert request.region == "PROD01"
    assert request.program == "PAYROLL"
    assert request.limit == 50


def test_abends_filter_request_defaults():
    """Test de valores por defecto"""
    request = AbendsFilterRequest()
    assert request.region is None
    assert request.program is None
    assert request.limit == 100


def test_abends_filter_request_limit_validation():
    """Test de validación de límite"""
    # Límite muy bajo
    with pytest.raises(ValidationError):
        AbendsFilterRequest(limit=0)

    # Límite muy alto
    with pytest.raises(ValidationError):
        AbendsFilterRequest(limit=2000)


def test_table_info_request():
    """Test de TableInfoRequest"""
    request = TableInfoRequest(table_name="CICS_ABENDS")
    assert request.table_name == "CICS_ABENDS"


def test_table_info_request_empty():
    """Test que valida tabla vacía"""
    with pytest.raises(ValidationError):
        TableInfoRequest(table_name="")
