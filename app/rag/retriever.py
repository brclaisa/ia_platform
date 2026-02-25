from langchain_chroma import Chroma

from app.config import settings
from app.rag.embeddings import get_embeddings

_vectorstore: Chroma | None = None


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name="documents",
            persist_directory=settings.chroma_persist_dir,
            embedding_function=get_embeddings(),
        )
    return _vectorstore


def retrieve_documents(query: str, top_k: int | None = None) -> list[dict]:
    k = top_k or settings.retriever_top_k
    vectorstore = get_vectorstore()

    if vectorstore._collection.count() == 0:
        return []

    results = vectorstore.similarity_search_with_score(query, k=k)

    documents = []
    for doc, score in results:
        documents.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "desconhecido"),
            "score": score,
        })

    return documents
