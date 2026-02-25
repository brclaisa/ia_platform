import json
import re

from langchain_openai import ChatOpenAI

from app.agents.prompts.compliance import COMPLIANCE_SYSTEM_PROMPT, COMPLIANCE_USER_PROMPT
from app.agents.state import AgentState
from app.config import settings

BLOCKED_PATTERNS = [
    r"\b(politic[ao]s?(?!\s+d[eao])|eleicao|eleiç[oõ]es|partido|senador|deputad[oa]|president[ea]|vereador|governador|prefeito)\b",
    r"\b(religi[aã]o|religios[ao]|igrej[ao]|pastor|padre|deus|biblia|bíblia|alcorão|alcorao|budismo|hinduísmo)\b",
    r"\b(violenci[ao]|arma|tiro|matar|assassin|terroris|agress[aã]o|tortur|espancament|bomba)\b",
    r"\b(drogas?|cocaina|cocaína|maconha|heroina|heroína|crack|trafic|entorpecent|narcotic)\b",
    r"\b(layoff|demiss[aã]o|demiss[oõ]es|demitir|corte.{0,10}pessoal|reestrutura[çc][aã]o.{0,15}demiss)\b",
    r"\b(ignore.{0,20}regras|finja.{0,10}ser|forget.{0,15}instructions|ignore.{0,15}instructions|jailbreak)\b",
]

BLOCKED_REGEX = re.compile("|".join(BLOCKED_PATTERNS), re.IGNORECASE)

COMPLIANCE_BLOCKED_MESSAGE = (
    "Desculpe, não posso responder a essa pergunta pois ela envolve um tópico "
    "sensível que está fora do escopo deste assistente. "
    "Posso ajudá-lo com outras questões?"
)


def _keyword_check(question: str) -> bool:
    normalized = question.lower()
    normalized = normalized.replace("á", "a").replace("é", "e").replace("í", "i")
    normalized = normalized.replace("ó", "o").replace("ú", "u").replace("ã", "a")
    normalized = normalized.replace("õ", "o").replace("ç", "c").replace("ê", "e")
    normalized = normalized.replace("â", "a").replace("ô", "o")
    return bool(BLOCKED_REGEX.search(question)) or bool(BLOCKED_REGEX.search(normalized))


async def _llm_compliance_check(question: str) -> dict:
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )
    messages = [
        ("system", COMPLIANCE_SYSTEM_PROMPT),
        ("human", COMPLIANCE_USER_PROMPT.format(question=question)),
    ]
    response = await llm.ainvoke(messages)
    try:
        return json.loads(response.content)
    except (json.JSONDecodeError, TypeError):
        return {"is_compliant": False, "reason": "Falha ao classificar conteúdo"}


async def compliance_node(state: AgentState) -> dict:
    question = state["question"]

    if _keyword_check(question):
        return {
            "is_compliant": False,
            "compliance_message": COMPLIANCE_BLOCKED_MESSAGE,
            "answer": COMPLIANCE_BLOCKED_MESSAGE,
        }

    result = await _llm_compliance_check(question)

    if not result.get("is_compliant", False):
        return {
            "is_compliant": False,
            "compliance_message": COMPLIANCE_BLOCKED_MESSAGE,
            "answer": COMPLIANCE_BLOCKED_MESSAGE,
        }

    return {
        "is_compliant": True,
        "compliance_message": None,
    }
