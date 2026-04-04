# main.py
# ComplianceNav AI — FastAPI Backend
# Deployed on Railway. Called by the Lovable React frontend.
#
# Local dev:  uvicorn main:app --reload --port 8000
# API docs:   http://localhost:8000/docs
# Health:     http://localhost:8000/health

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from rag.retriever import retrieve, build_context
from llm.system_prompt import build_prompt
from llm.claude_client import call_claude
from responsible_ai.confidence import compute_final_confidence
from responsible_ai.escalation import check_escalation


# ── Lifespan: pre-load the FAISS index on startup ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting ComplianceNav AI backend...")
    try:
        # Warm up — loads index and embedding model into memory
        retrieve("PIPEDA consent requirements")
        print("✅ FAISS index and embedding model loaded successfully.")
    except Exception as e:
        print(f"⚠️  Startup warning: {e}")
    yield
    print("Shutting down ComplianceNav AI backend.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ComplianceNav AI",
    description="Responsible AI Compliance Agent for Canadian Banking",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allows the Lovable frontend (any origin) to call this backend.
# In production you can tighten this to your specific Lovable domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Lovable app URL — tighten after launch
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str


class SourceItem(BaseModel):
    document:  str
    section:   str
    relevance: str


class RetrievedChunk(BaseModel):
    source:           str
    section:          str
    similarity_score: float
    text_preview:     str   # First 200 chars for transparency panel


class QueryResponse(BaseModel):
    answer:               str
    sources:              list[SourceItem]
    confidence:           str   # HIGH | MEDIUM | LOW
    confidence_rationale: str
    override_note:        str | None
    escalation_required:  bool
    escalation_reason:    str | None
    retrieved_chunks:     list[RetrievedChunk]
    disclaimer:           str


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    """Health check — Railway uses this to confirm the server is running."""
    return {"status": "ok", "service": "ComplianceNav AI"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Main endpoint. Called by the Lovable frontend on every user query.
    Steps:
    1. Retrieve relevant chunks from FAISS
    2. Build context string
    3. Call Claude with system prompt
    4. Apply responsible AI layer (confidence + escalation)
    5. Return structured response
    """
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if len(question) > 2000:
        raise HTTPException(status_code=400, detail="Question too long (max 2000 characters).")

    # Step 1 — Retrieve
    retrieved = retrieve(question)

    # Step 2 — Build context
    context = build_context(retrieved)

    # Step 3 — Call Claude
    prompt   = build_prompt(question=question, context=context)
    response = call_claude(prompt)

    # Step 4 — Responsible AI layer
    llm_confidence = response.get("confidence", "LOW")
    final_confidence, override_note = compute_final_confidence(retrieved, llm_confidence)

    escalation_required, escalation_reason = check_escalation(
        query=question,
        confidence=final_confidence,
        llm_escalation=response.get("escalation_required", False),
        retrieved_chunks=retrieved,
    )

    # Step 5 — Build response
    return QueryResponse(
        answer=               response.get("answer", "No answer generated."),
        sources=              [SourceItem(**s) for s in response.get("sources", [])],
        confidence=           final_confidence,
        confidence_rationale= response.get("confidence_rationale", ""),
        override_note=        override_note,
        escalation_required=  escalation_required,
        escalation_reason=    escalation_reason,
        retrieved_chunks=[
            RetrievedChunk(
                source=           c["source"],
                section=          c["section"],
                similarity_score= c["similarity_score"],
                text_preview=     c["text"][:200],
            )
            for c in retrieved
        ],
        disclaimer=response.get(
            "disclaimer",
            "This response is for informational purposes only and does not "
            "constitute legal or compliance advice."
        ),
    )
