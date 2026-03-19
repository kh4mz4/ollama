from llama_index.core import (
    Settings,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from tenacity import retry, stop_after_attempt, wait_exponential

from process.index import load_or_build_index
from system.config import EMBED_MODEL, LLM_MODEL, SIMILARITY_TOP_K
from system.prompt import DEFAULT_SYSTEM_PROMPT

_engine = None


def start_engine():
    """
    Chat xotirasi bo'lgan RAG engine yaratadi.
    Birinchi chaqiriqda engine yaratiladi,
    keyingi chaqiriqlarda aynan o'sha instance qaytadi.
    """
    global _engine
    if _engine is not None:
        return _engine

    embed = OllamaEmbedding(model_name=EMBED_MODEL)
    llm = Ollama(
        model=LLM_MODEL,
        request_timeout=600,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
    )

    # Global default sifatida ham qo'yib qo'yamiz
    Settings.embed_model = embed
    Settings.llm = llm

    index = load_or_build_index(embed)

    _engine = index.as_chat_engine(
        llm=llm,
        embed_model=embed,
        chat_mode="context",
        similarity_top_k=SIMILARITY_TOP_K,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
    )

    return _engine


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def ask_llm(question: str, engine) -> str:
    try:
        resp = engine.chat(question)
        return str(resp)
    except ConnectionError:
        raise
    except Exception as e:
        return f"Error occurred!: {str(e)}"
