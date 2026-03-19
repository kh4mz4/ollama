import time

import faiss
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

from process.docs_reader import load_all_documents
from system.config import CHUNK_SIZE, CHUNK_OVERLAP, INDEX_DIR


def get_embed_dim(embed: OllamaEmbedding) -> int:
    """
    Define vector dimension by getting embedding for a test string.
    """
    v = embed.get_text_embedding("dim probe")
    if not v or not isinstance(v, list):
        raise RuntimeError("Embedding returned empty result. Is 'nomic-embed-text' pulled in Ollama?")
    return len(v)


def _create_faiss_index(dim: int, num_vectors: int = 0):
    """Vektor soniga qarab optimal FAISS index tanlaydi."""
    if num_vectors < 1000:
        return faiss.IndexFlatL2(dim)

    elif num_vectors < 50_000:
        nlist = min(int(num_vectors ** 0.5), 100)
        quantizer = faiss.IndexFlatL2(dim)
        index = faiss.IndexIVFFlat(quantizer, dim, nlist)
        return index

    else:
        nlist = int(num_vectors ** 0.5)
        m = 8
        quantizer = faiss.IndexFlatL2(dim)
        index = faiss.IndexIVFPQ(quantizer, dim, nlist, m, 8)
        return index


def build_index(embed: OllamaEmbedding) -> VectorStoreIndex:
    t0 = time.time()
    docs = load_all_documents()

    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    dim = get_embed_dim(embed)
    faiss_index = _create_faiss_index(dim, num_vectors=len(docs))
    vector_store = FaissVectorStore(faiss_index=faiss_index)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        embed_model=embed,
        transformations=[splitter],
    )

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(INDEX_DIR))

    elapsed = time.time() - t0
    print(f"✅ Index built with {len(docs)} document(s) in {elapsed:.1f}s")
    return index


def load_or_build_index(embed: OllamaEmbedding) -> VectorStoreIndex:
    if INDEX_DIR.exists() and any(INDEX_DIR.iterdir()):
        try:
            vector_store = FaissVectorStore.from_persist_dir(str(INDEX_DIR))
            storage = StorageContext.from_defaults(
                vector_store=vector_store,
                persist_dir=str(INDEX_DIR),
            )
            idx = load_index_from_storage(storage, embed_model=embed)
            print("✅ Index loaded from disk.")
            return idx
        except Exception as e:
            print("⚠️ Failed to load existing index:", e)
            print("➡️ Rebuilding index...")

    return build_index(embed)
