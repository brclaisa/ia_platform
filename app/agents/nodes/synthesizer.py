from langchain_openai import ChatOpenAI

from app.agents.prompts.synthesizer import (
    SYNTHESIZER_SYSTEM_PROMPT,
    SYNTHESIZER_USER_PROMPT,
)
from app.agents.state import AgentState
from app.config import settings


async def synthesizer_node(state: AgentState) -> dict:
    raw_answer = state.get("answer", "")
    if not raw_answer:
        return {"answer": "Não foi possível gerar uma resposta."}

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )
    messages = [
        ("system", SYNTHESIZER_SYSTEM_PROMPT),
        (
            "human",
            SYNTHESIZER_USER_PROMPT.format(
                raw_answer=raw_answer,
                question=state["question"],
            ),
        ),
    ]
    response = await llm.ainvoke(messages)

    return {"answer": response.content}
