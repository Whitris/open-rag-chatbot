import chromadb
import numpy as np
import pytest

from open_rag_bot.config.settings import get_settings
from open_rag_bot.core.loader import load_or_create_collection
from open_rag_bot.core.retriever import get_context_retriever


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
def retriever(settings):
    return get_context_retriever(
        settings.app.collection_dir, settings.app.collection_name
    )


def test_load_index_returns_collection(tmp_path):
    collection = load_or_create_collection(tmp_path, collection_name="test")
    assert collection.name == "test"


def test_retrieve_relevant_docs(tmp_path, retriever):
    client = chromadb.PersistentClient(path=str(tmp_path))
    collection = client.get_or_create_collection(name="test")
    docs = ["a", "b", "c"]
    embeddings = np.array([[1.0], [2.0], [3.0]])
    collection.add(
        documents=docs,
        ids=[str(i) for i in range(len(docs))],
        embeddings=embeddings.tolist(),
    )

    class DummyClient:
        def encode(self, texts):
            return np.array([[1.5]])

    retriever.collection = collection
    retriever.embedding_client = DummyClient()
    results = retriever.retrieve_relevant_docs(
        "question",
        k=2,
    )
    assert results
    assert all(res["content"] in docs for res in results)
