from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="Pergunta do usuário")


class AnswerResponse(BaseModel):
    question: str
    answer: str
    is_compliant: bool
    route: str | None = None
    sources: list[str] = Field(default_factory=list)


class DocumentUploadResponse(BaseModel):
    filename: str
    chunks_created: int
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
