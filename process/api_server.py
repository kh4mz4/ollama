from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import time
from contextlib import asynccontextmanager

from process.chat import start_engine, ask_llm
from system.config import LLM_MODEL


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.engine = start_engine()
    print("✅ Engine is ready!")
    yield
    # Shutdown
    print("👋 Server is stopping...")


app = FastAPI(
    title="RAG Chat API",
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


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    elapsed_ms: float


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest):
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Empty message is not allowed.")

    t0 = time.time()

    answer = await asyncio.to_thread(
        ask_llm, body.message, app.state.engine
    )

    elapsed = (time.time() - t0) * 1000
    return ChatResponse(reply=answer, elapsed_ms=round(elapsed, 1))


@app.post("/api/reindex")
async def reindex_endpoint():
    # ... reindex logikasi
    return {"status": "ok", "message": "Index rebuilt successfully!"}


@app.get("/api/health")
async def health():
    return {"status": "healthy", "model": LLM_MODEL}
