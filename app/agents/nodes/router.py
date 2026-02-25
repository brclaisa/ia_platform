import json

from langchain_openai import ChatOpenAI

from app.agents.prompts.router import ROUTER_SYSTEM_PROMPT, ROUTER_USER_PROMPT
from app.agents.state import AgentState
from app.config import settings


async def router_node(state: AgentState) -> dict:
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )
    messages = [
        ("system", ROUTER_SYSTEM_PROMPT),
        ("human", ROUTER_USER_PROMPT.format(question=state["question"])),
    ]
    response = await llm.ainvoke(messages)

    try:
        result = json.loads(response.content)
        route = result.get("route", "direct")
    except (json.JSONDecodeError, TypeError):
        route = "direct"

    if route not in ("rag", "direct"):
        route = "direct"

    return {"route": route}
