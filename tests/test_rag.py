import os
from pathlib import Path

import pytest

from app.rag.ingestion import _chunk_documents, _load_single_file

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture(autouse=True)
def create_fixtures(tmp_path):
    test_file = tmp_path / "test_doc.txt"
    test_file.write_text(
        "Este é um documento de teste.\n\n"
        "Ele contém múltiplos parágrafos para testar o chunking.\n\n"
        "Cada parágrafo deve ser processado corretamente pelo sistema de ingestão.",
        encoding="utf-8",
    )
    yield tmp_path


class TestLoadSingleFile:
    def test_loads_txt_file(self, create_fixtures):
        file_path = str(create_fixtures / "test_doc.txt")
        docs = _load_single_file(file_path)
        assert len(docs) > 0
        assert "documento de teste" in docs[0].page_content

    def test_returns_empty_for_unsupported_format(self, create_fixtures):
        unsupported = create_fixtures / "test.xyz"
        unsupported.write_text("content")
        docs = _load_single_file(str(unsupported))
        assert docs == []

    def test_sets_source_metadata(self, create_fixtures):
        file_path = str(create_fixtures / "test_doc.txt")
        docs = _load_single_file(file_path)
        assert docs[0].metadata["source"] == "test_doc.txt"


class TestChunkDocuments:
    def test_chunks_long_document(self, create_fixtures):
        file_path = str(create_fixtures / "test_doc.txt")
        docs = _load_single_file(file_path)
        chunks = _chunk_documents(docs)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk.page_content) > 0
