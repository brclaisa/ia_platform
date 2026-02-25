from langchain_openai import ChatOpenAI

from app.agents.prompts.rag import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT
from app.agents.state import AgentState
from app.config import settings
from app.rag.retriever import retrieve_documents

NO_CONTEXT_MESSAGE = (
    "Não encontrei informações suficientes nos documentos disponíveis "
    "para responder a esta pergunta."
)


async def rag_node(state: AgentState) -> dict:
    question = state["question"]
    docs = retrieve_documents(question)

    if not docs:
        return {
            "answer": NO_CONTEXT_MESSAGE,
            "retrieved_context": None,
            "sources": [],
        }

    context_parts = []
    sources = []
    for i, doc in enumerate(docs, 1):
        source = doc["source"]
        context_parts.append(f"[Documento {i} - {source}]\n{doc['content']}")
        if source not in sources:
            sources.append(source)

    context = "\n\n".join(context_parts)

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.1,
    )
    messages = [
        ("system", RAG_SYSTEM_PROMPT.format(context=context)),
        ("human", RAG_USER_PROMPT.format(question=question)),
    ]
    response = await llm.ainvoke(messages)

    return {
        "answer": response.content,
        "retrieved_context": context,
        "sources": sources,
    }
