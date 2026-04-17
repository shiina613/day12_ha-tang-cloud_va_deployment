"""
Production AI Chat Agent — Day 12 Lab Complete
"""
import os
import time
import signal
import logging
import json
from datetime import datetime, timezone
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Security, Depends, Request, Response
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn

load_dotenv(Path(__file__).parent.parent / ".env")

from app.config import settings

# ── LLM ──────────────────────────────────────────────────
def get_llm_response(messages: list) -> str:
    if settings.openai_api_key:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            max_tokens=1000,
        )
        return resp.choices[0].message.content
    else:
        # fallback mock
        from utils.mock_llm import ask
        return ask(messages[-1]["content"])

# ── Logging ───────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

START_TIME = time.time()
_is_ready = False
_request_count = 0

# ── Rate limiter ──────────────────────────────────────────
_rate_windows: dict[str, deque] = defaultdict(deque)

def check_rate_limit(key: str):
    now = time.time()
    window = _rate_windows[key]
    while window and window[0] < now - 60:
        window.popleft()
    if len(window) >= settings.rate_limit_per_minute:
        raise HTTPException(429, f"Rate limit: {settings.rate_limit_per_minute} req/min")
    window.append(now)

# ── Cost guard ────────────────────────────────────────────
_daily_cost = 0.0
_cost_reset_day = time.strftime("%Y-%m-%d")

def record_cost(input_tokens: int, output_tokens: int):
    global _daily_cost, _cost_reset_day
    today = time.strftime("%Y-%m-%d")
    if today != _cost_reset_day:
        _daily_cost = 0.0
        _cost_reset_day = today
    if _daily_cost >= settings.daily_budget_usd:
        raise HTTPException(503, "Daily budget exhausted.")
    _daily_cost += (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006

# ── Auth ──────────────────────────────────────────────────
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key or api_key != settings.agent_api_key:
        raise HTTPException(401, "Invalid or missing API key")
    return api_key

# ── Conversation store (in-memory) ───────────────────────
# key: session_id → list of messages
_conversations: dict[str, list] = defaultdict(list)

# ── Lifespan ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info(json.dumps({"event": "startup", "app": settings.app_name}))
    _is_ready = True
    yield
    _is_ready = False
    logger.info(json.dumps({"event": "shutdown"}))

# ── App ───────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    global _request_count
    _request_count += 1
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    if "server" in response.headers:
        del response.headers["server"]
    return response

# ── Models ────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default="default")

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    model: str
    timestamp: str

# ── Endpoints ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, tags=["UI"])
def index():
    """Chat UI"""
    html = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(html.read_text())


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(body: ChatRequest):
    check_rate_limit(body.session_id)

    history = _conversations[body.session_id]
    history.append({"role": "user", "content": body.message})

    # Keep last 20 messages
    if len(history) > 20:
        history = history[-20:]
        _conversations[body.session_id] = history

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ] + history

    input_tokens = sum(len(m["content"].split()) * 2 for m in messages)
    record_cost(input_tokens, 0)

    reply = get_llm_response(messages)

    history.append({"role": "assistant", "content": reply})
    output_tokens = len(reply.split()) * 2
    record_cost(0, output_tokens)

    logger.info(json.dumps({"event": "chat", "session": body.session_id, "q_len": len(body.message)}))

    return ChatResponse(
        reply=reply,
        session_id=body.session_id,
        model=settings.llm_model,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.delete("/chat/{session_id}", tags=["Chat"])
def clear_history(session_id: str):
    _conversations.pop(session_id, None)
    return {"cleared": session_id}


@app.get("/health", tags=["Operations"])
def health():
    return {
        "status": "ok",
        "version": settings.app_version,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "llm": "openai" if settings.openai_api_key else "mock",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready", tags=["Operations"])
def ready():
    if not _is_ready:
        raise HTTPException(503, "Not ready")
    return {"ready": True}


# ── Graceful shutdown ─────────────────────────────────────
def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))

signal.signal(signal.SIGTERM, _handle_signal)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port,
                reload=settings.debug, timeout_graceful_shutdown=30)
