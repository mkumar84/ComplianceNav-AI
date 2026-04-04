# responsible_ai/escalation.py

SENSITIVE_KEYWORDS = [
    "lawful", "unlawful", "illegal", "penalty", "fine", "breach",
    "violation", "violate", "consent required", "liable", "liability",
    "enforcement", "prosecut", "prohibited", "mandatory requirement",
    "must comply", "am i allowed", "can we legally", "is it legal",
    "subject to", "regulatory action", "investigation",
]


def check_escalation(
    query: str,
    confidence: str,
    llm_escalation: bool,
    retrieved_chunks: list[dict],
) -> tuple[bool, str | None]:
    """
    Returns (escalation_required, reason).
    Escalates on: low confidence, no retrieval, sensitive keywords, LLM flag.
    """
    if confidence == "LOW":
        return True, (
            "Confidence is LOW — retrieved content does not sufficiently address "
            "this question. Please consult a qualified compliance professional."
        )

    if not retrieved_chunks:
        return True, (
            "No relevant content found in the regulatory corpus. "
            "Please consult a qualified compliance professional."
        )

    for kw in SENSITIVE_KEYWORDS:
        if kw in query.lower():
            return True, (
                f"This question involves a material compliance determination "
                f"(detected: '{kw}'). Do not act on AI-generated advice without "
                "review by a qualified legal or compliance professional."
            )

    if llm_escalation:
        return True, (
            "The AI system flagged this question as requiring human expert review "
            "based on the nature of the compliance determination."
        )

    return False, None
