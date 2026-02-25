from langchain_openai import ChatOpenAI

from app.agents.prompts.direct import DIRECT_SYSTEM_PROMPT, DIRECT_USER_PROMPT
from app.agents.state import AgentState
from app.config import settings


async def direct_node(state: AgentState) -> dict:
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )
    messages = [
        ("system", DIRECT_SYSTEM_PROMPT),
        ("human", DIRECT_USER_PROMPT.format(question=state["question"])),
    ]
    response = await llm.ainvoke(messages)

    return {"answer": response.content}
