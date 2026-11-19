
VALID_EVIDENCE_CLASSIFICATIONS = {
    "sufficient",
    "partial",
    "constraint_only",
    "insufficient",
    "unassessed"
}


def evaluate_evidence(
    evidence_classification: str,
    constraint_answers_question: bool = False
):

    if evidence_classification not in VALID_EVIDENCE_CLASSIFICATIONS:
        raise ValueError(
            f"Invalid evidence classification: {evidence_classification}"
        )

    # 1. All material parts of the question are supported
    if evidence_classification == "sufficient":
        return {
            "classification": "sufficient",
            "decision": "answer",
            "allow_generation": True,
            "offer_human_assistance": False,
            "reason": (
                "Retrieved evidence sufficiently supports "
                "an answer to the guest's question."
            )
        }

    # 2. Some parts are supported, but information is missing
    if evidence_classification == "partial":
        return {
            "classification": "partial",
            "decision": "answer_partially",
            "allow_generation": True,
            "offer_human_assistance": True,
            "reason": (
                "Retrieved evidence supports part of the "
                "guest's question, but some requested "
                "information remains unsupported. Generate "
                "a partial answer using only supported facts "
                "and offer human assistance for the missing "
                "information."
            )
        }

    # 3. Relevant policy restrictions were retrieved
    if evidence_classification == "constraint_only":

        if constraint_answers_question:
            return {
                "classification": "constraint_only",
                "decision": "answer_with_constraints",
                "allow_generation": True,
                "offer_human_assistance": True,
                "reason": (
                    "The policy restriction directly answers "
                    "the guest's question. Generate a limited "
                    "answer using only the supported restriction."
                )
            }

        return {
            "classification": "constraint_only",
            "decision": "abstain",
            "allow_generation": False,
            "offer_human_assistance": True,
            "reason": (
                "Relevant restrictions were found, but they "
                "do not establish the requested outcome. "
                "Abstain rather than speculate."
            )
        }

    # 4. Evidence assessment has not been completed
    if evidence_classification == "unassessed":
        return {
            "classification": "unassessed",
            "decision": "block",
            "allow_generation": False,
            "offer_human_assistance": False,
            "reason": (
                "Evidence has not been assessed. "
                "Answer generation is blocked until assessment "
                "is complete."
            )
        }

    # 5. No meaningful supporting evidence was found
    return {
        "classification": "insufficient",
        "decision": "abstain",
        "allow_generation": False,
        "offer_human_assistance": True,
        "reason": (
            "Retrieved evidence does not support answering "
            "the guest's question. Abstain rather than "
            "provide speculative information."
        )
    }
