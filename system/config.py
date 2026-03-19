from pathlib import Path
import logging

LLM_MODEL = "gemma3:4b"

EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE = 1024
CHUNK_OVERLAP = 200
SIMILARITY_TOP_K = 2

# silence noisy HTTP logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

DOCS_DIR = Path(r"F:\AI\rag_data\docs")  # put your files here
INDEX_DIR = Path(r"F:\AI\rag_data\index")  # index will be stored here

SUPPORTED_EXTS = {".txt", ".md", ".pdf", ".docx", ".py", ".json", ".csv", ".xlsx"}
