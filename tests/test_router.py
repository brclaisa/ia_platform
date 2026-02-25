import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.nodes.router import router_node


@pytest.mark.asyncio
async def test_router_returns_rag_route():
    state = {"question": "Qual a política de férias da empresa?"}
    mock_response = AsyncMock()
    mock_response.content = json.dumps({"route": "rag"})

    with patch("app.agents.nodes.router.ChatOpenAI") as mock_llm_class:
        mock_llm_class.return_value.ainvoke = AsyncMock(return_value=mock_response)
        result = await router_node(state)

    assert result["route"] == "rag"


@pytest.mark.asyncio
async def test_router_returns_direct_route():
    state = {"question": "O que é machine learning?"}
    mock_response = AsyncMock()
    mock_response.content = json.dumps({"route": "direct"})

    with patch("app.agents.nodes.router.ChatOpenAI") as mock_llm_class:
        mock_llm_class.return_value.ainvoke = AsyncMock(return_value=mock_response)
        result = await router_node(state)

    assert result["route"] == "direct"


@pytest.mark.asyncio
async def test_router_defaults_to_direct_on_invalid_json():
    state = {"question": "Qualquer coisa"}
    mock_response = AsyncMock()
    mock_response.content = "resposta inválida"

    with patch("app.agents.nodes.router.ChatOpenAI") as mock_llm_class:
        mock_llm_class.return_value.ainvoke = AsyncMock(return_value=mock_response)
        result = await router_node(state)

    assert result["route"] == "direct"
