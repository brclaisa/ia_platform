import os
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from app.config import settings
from app.rag.retriever import get_vectorstore

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def _load_single_file(file_path: str) -> list[Document]:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in (".txt", ".md"):
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        return []

    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = Path(file_path).name

    return docs


def _chunk_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def ingest_file(file_path: str) -> int:
    documents = _load_single_file(file_path)
    if not documents:
        return 0

    chunks = _chunk_documents(documents)
    if not chunks:
        return 0

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)

    return len(chunks)


def ingest_directory(directory: str | None = None) -> dict[str, int]:
    dir_path = directory or settings.documents_dir
    results = {}

    if not os.path.isdir(dir_path):
        return results

    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if not os.path.isfile(file_path):
            continue
        if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        chunks_count = ingest_file(file_path)
        results[filename] = chunks_count

    return results
