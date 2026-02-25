from typing import TypedDict


class AgentState(TypedDict):
    question: str
    is_compliant: bool
    compliance_message: str | None
    route: str | None
    retrieved_context: str | None
    sources: list[str]
    answer: str | None
