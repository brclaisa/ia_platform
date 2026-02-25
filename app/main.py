import os
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.agents.graph import get_compiled_graph
from app.config import settings
from app.models import (
    AnswerResponse,
    DocumentUploadResponse,
    HealthResponse,
    QuestionRequest,
)
from app.rag.ingestion import SUPPORTED_EXTENSIONS, ingest_directory, ingest_file


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.documents_dir, exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    yield


app = FastAPI(
    title="Plataforma IA MultiAgente",
    description="Assistente inteligente com compliance, RAG e agentes especializados",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")


@app.post("/ask", response_model=AnswerResponse)
async def ask(request: QuestionRequest):
    graph = get_compiled_graph()

    initial_state = {
        "question": request.question,
        "is_compliant": False,
        "compliance_message": None,
        "route": None,
        "retrieved_context": None,
        "sources": [],
        "answer": None,
    }

    try:
        result = await graph.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {e}")

    return AnswerResponse(
        question=result["question"],
        answer=result.get("answer", "Não foi possível gerar uma resposta."),
        is_compliant=result.get("is_compliant", False),
        route=result.get("route"),
        sources=result.get("sources", []),
    )


@app.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo não fornecido.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado. Use: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    file_path = os.path.join(settings.documents_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {e}")

    chunks_count = ingest_file(file_path)

    return DocumentUploadResponse(
        filename=file.filename,
        chunks_created=chunks_count,
        message=f"Documento '{file.filename}' processado com sucesso.",
    )


@app.post("/documents/ingest-all")
async def ingest_all_documents():
    results = ingest_directory()
    total_chunks = sum(results.values())
    return {
        "files_processed": len(results),
        "total_chunks": total_chunks,
        "details": results,
    }
