

def assess_evidence_status(selected_chunks: list):
    """
    Prototype assessment using explicit evidence annotations.
    Does not independently understand policy text.
    """

    valid_classifications = {
        "sufficient",
        "constraint_only",
        "insufficient"
    }

    classifications = {
        chunk.get("evidence_type")
        for chunk in selected_chunks
        if chunk.get("evidence_type") in valid_classifications
    }

    if not classifications:
        return "unassessed"

    if "sufficient" in classifications:
        return "sufficient"

    if "constraint_only" in classifications:
        return "constraint_only"

    return "insufficient"





def classify_evidence(question: str, selected_chunks: list):
    """
    Prototype classifier combining:
    1. Context and audience validation
    2. Explicit evidence annotation assessment

    Does not independently understand policy text.
    """

    if not selected_chunks:
        return {
            "classification": "insufficient",
            "reason": "No supporting context was retrieved.",
            "evidence_chunk_ids": [],
            "assessment_status": "completed"
        }

    # Only Guest audience documents are eligible
    eligible_chunks = [
        chunk for chunk in selected_chunks
        if chunk.get("audience") == "Guest"
    ]

    if not eligible_chunks:
        return {
            "classification": "insufficient",
            "reason": "No eligible Guest evidence was found.",
            "evidence_chunk_ids": [],
            "assessment_status": "completed"
        }

    evidence_chunk_ids = [
        chunk["chunk_id"]
        for chunk in eligible_chunks
    ]

    draft_chunks = [
        chunk for chunk in eligible_chunks
        if chunk.get("status") == "Draft"
    ]

    # Assess explicit evidence annotations
    classification = assess_evidence_status(eligible_chunks)

    if classification == "unassessed":
        reason = (
            "Eligible context was retrieved, but semantic "
            "evidence assessment is still pending."
        )
    elif classification == "sufficient":
        reason = "Evidence is marked as sufficient by the evaluator."
    elif classification == "constraint_only":
        reason = "Evidence contains restrictions but cannot confirm the requested fact."
    else:
        reason = "The evaluator marked the evidence as insufficient."

    return {
        "classification": classification,
        "question": question,
        "reason": reason,
        "evidence_chunk_ids": evidence_chunk_ids,
        "draft_evidence_present": bool(draft_chunks),
        "assessment_status": (
            "pending" if classification == "unassessed"
            else "completed"
        )
    }
