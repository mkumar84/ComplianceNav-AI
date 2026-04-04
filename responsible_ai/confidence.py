# responsible_ai/confidence.py

def compute_final_confidence(
    retrieved_chunks: list[dict],
    llm_confidence: str,
) -> tuple[str, str | None]:
    """
    Combine retrieval similarity scores with LLM self-assessment.
    Retrieval score is the objective override — prevents overconfident LLM responses.
    Returns (final_confidence, override_note | None)
    """
    if not retrieved_chunks:
        return "LOW", "No content retrieved from corpus."

    avg  = sum(c["similarity_score"] for c in retrieved_chunks) / len(retrieved_chunks)
    best = max(c["similarity_score"] for c in retrieved_chunks)

    # Hard downgrade — retrieval too weak regardless of LLM confidence
    if avg < 0.40:
        note = None
        if llm_confidence in ("HIGH", "MEDIUM"):
            note = f"Weak retrieval (avg similarity {avg:.2f}) — downgraded from {llm_confidence} to LOW."
        return "LOW", note

    # Soft downgrade — mediocre retrieval, overconfident LLM
    if avg < 0.55 and llm_confidence == "HIGH":
        return "MEDIUM", f"Moderate retrieval (avg {avg:.2f}) — downgraded from HIGH to MEDIUM."

    # Soft upgrade — strong retrieval, conservative LLM
    if avg > 0.75 and best > 0.85 and llm_confidence == "LOW":
        return "MEDIUM", f"Strong retrieval (avg {avg:.2f}) — upgraded from LOW to MEDIUM. Verify independently."

    return llm_confidence, None
