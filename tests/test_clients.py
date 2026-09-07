# Unit tests for external client integrations (Groq LLM and Overpass API)
from unittest.mock import patch, MagicMock
import requests
from app.clients.llm_client import call_groq_triage
from app.clients.overpass_client import query_overpass


def test_llm_client_no_api_key():
    with patch("app.clients.llm_client.GROQ_API_KEY", ""):
        result = call_groq_triage("I have a fever")
        assert result is None


def test_llm_client_success():
    mock_choice = MagicMock()
    mock_choice.message.content = '{"needs": "hospital", "specialty": "Emergency", "urgency": "high"}'

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.return_value = mock_completion

    with patch("app.clients.llm_client.GROQ_API_KEY", "mock_key_123"):
        with patch("app.clients.llm_client.Groq", return_value=mock_client_instance):
            res = call_groq_triage("Severe head trauma")
            assert res == '{"needs": "hospital", "specialty": "Emergency", "urgency": "high"}'


def test_llm_client_api_exception():
    with patch("app.clients.llm_client.GROQ_API_KEY", "mock_key_123"):
        with patch("app.clients.llm_client.Groq", side_effect=Exception("API connection refused")):
            res = call_groq_triage("Broken leg")
            assert res is None


def test_overpass_client_primary_endpoint_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"elements": [{"id": 1, "lat": 28.0, "lon": 77.0}]}
    mock_response.raise_for_status.return_value = None

    with patch("app.clients.overpass_client.requests.post", return_value=mock_response) as mock_post:
        result = query_overpass("[out:json]; node(around:1000, 28, 77); out;")
        assert result == {"elements": [{"id": 1, "lat": 28.0, "lon": 77.0}]}
        assert mock_post.call_count == 1


def test_overpass_client_primary_fail_fallback_success():
    failed_resp = MagicMock()
    failed_resp.raise_for_status.side_effect = requests.HTTPError("504 Gateway Timeout")

    success_resp = MagicMock()
    success_resp.json.return_value = {"elements": [{"id": 2, "lat": 28.1, "lon": 77.1}]}
    success_resp.raise_for_status.return_value = None

    # First call fails, second call succeeds
    with patch("app.clients.overpass_client.requests.post", side_effect=[requests.RequestException("Timeout"), success_resp]) as mock_post:
        result = query_overpass("[out:json]; node(around:1000, 28, 77); out;")
        assert result == {"elements": [{"id": 2, "lat": 28.1, "lon": 77.1}]}
        assert mock_post.call_count == 2


def test_overpass_client_all_endpoints_fail():
    with patch("app.clients.overpass_client.requests.post", side_effect=requests.RequestException("Connection error")):
        result = query_overpass("[out:json]; node(around:1000, 28, 77); out;")
        assert result is None
