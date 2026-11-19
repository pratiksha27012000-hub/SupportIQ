# SupportIQ — Product Requirements Document (PRD)

**Product:** SupportIQ  
**Demo organization:** StayEase (fictional hospitality platform)  
**Version:** 1.0  
**Status:** Portfolio project baseline  
**Last updated:** 20 November 2026

---

## 1. Product summary

SupportIQ is a retrieval-augmented generation (RAG) hospitality support assistant. It helps guests answer common questions using a curated set of approved policies, standard operating procedures (SOPs) and knowledge articles.

The product prioritizes evidence-grounded answers. It evaluates retrieved information before generating a response and should answer only to the extent supported by evidence. When evidence is incomplete, it may provide a partial answer while clearly identifying what remains unknown. When an issue requires human investigation, SupportIQ can offer a lightweight ticket workflow.

This portfolio demonstration uses fictional StayEase and synthetic knowledge-base documents.

## 2. Problem statement

Guests ask recurring questions about reservations, cancellations, refunds, payments, check-in/check-out and stay experiences. Support teams need to find the correct policy or SOP and explain it consistently.

A general-purpose generative model may produce plausible but unsupported answers. Incorrect information about refunds, payment status, reservation terms or property procedures can create confusion.

SupportIQ addresses this by retrieving relevant knowledge-base evidence, evaluating whether it supports an answer, and abstaining or seeking human assistance when it does not.

## 3. Product vision

Provide guests with a helpful first point of contact for hospitality questions while keeping answers grounded in approved source material and providing a clear path to human investigation when automation is not appropriate.

## 4. Goals

1. Answer common guest and hotel-partner questions from the synthetic approved knowledge base.
2. Retrieve relevant policy, SOP and knowledge-article content using hybrid retrieval.
3. Evaluate evidence before answer generation.
4. Support complete and partial answers without inventing missing details.
5. Abstain or ask for clarification when evidence is insufficient.
6. Provide source references for traceability.
7. Preserve conversational context for relevant follow-up questions.
8. Offer a simple, consent-based ticket fallback for issues requiring human investigation.
9. Allow agents to inspect tickets and update basic ticket status.

## 5. Non-goals

- Full CRM or enterprise helpdesk functionality.
- Live agent-to-guest chat.
- Booking, cancellation, payment or refund transaction execution.
- PMS, payment gateway or external CRM integrations.
- Automated department routing or complex assignment logic.
- Workload management, agent performance dashboards or complex SLA management.
- Autonomous operational actions.
- Voice-based support.

## 6. Target users

| User | Need | Product value |
|---|---|---|
| Hotel guest | Clear answer to a hospitality question | Faster access to relevant policy information |
| Hotel partner | Understand platform procedures and account policies | Self-service access to partner knowledge |
| Support agent | Investigate issues that cannot be resolved automatically | Ticket details and conversation context |
| Support/product administrator | Maintain demo knowledge and review quality | Traceable documents and evaluation artifacts |

## 7. Product scope and priorities

### P0 — Core experience
- Guest-facing chat interface.
- Natural-language hospitality questions.
- Retrieval from approved guest and hotel-partner policies, SOPs and knowledge articles.
- Dense and keyword retrieval, fusion and reranking.
- Evidence evaluation and approval checks.
- Grounded answer generation with source references.
- Partial answers that distinguish supported facts from missing information.
- Clarification and abstention when needed.
- Contextual follow-up questions.
- Evaluation of retrieval and answer quality.

### P1 — Lightweight human-support fallback
- Offer human assistance when a query requires investigation.
- Ask permission before presenting the ticket form.
- If the guest declines, dismiss the offer without creating a ticket.
- If the guest agrees, collect required ticket details.
- Require explicit consent before submission.
- Create at most one ticket per conversation.
- Store the issue, guest email and relevant conversation transcript.
- Show the ticket reference to the guest.
- Display tickets in a simple internal dashboard.
- Allow agents to inspect ticket details and update basic status.
- Agent follow-up takes place by email, outside the chat.

## 8. Knowledge-base scope

The initial synthetic StayEase knowledge base contains 27 source documents:

| Document type | Count | Identifier range |
|---|---:|---|
| Guest policies (PDF) | 8 | `POL-GST-001` to `POL-GST-008` |
| Hotel-partner policies (PDF) | 6 | `POL-HTL-001` to `POL-HTL-006` |
| SOPs (DOCX) | 8 | `SOP-001` to `SOP-008` |
| Knowledge articles (TXT) | 5 | `KB-001` to `KB-005` |
| **Total** | **27** | |

The document registry manages document metadata and approval status. The demo ingestion process extracts, cleans, chunks and enriches documents before indexing them for retrieval.

All documents are synthetic and marked approved for this portfolio demonstration only. This does not imply approval for real-world hotel operations.

## 9. Supported query taxonomy

| Category | Subcategories |
|---|---|
| Reservations | Booking confirmation, Incorrect details |
| Cancellation | Cancellation policy, Cancellation request |
| Refunds | Refund eligibility, Processing timeline |
| Payments | Payment failure, Duplicate payment |
| Check-in | Early check-in, Requirements |
| Check-out | Late checkout |
| Stay Experience | Cleanliness, Room not as described |
| Hotel Partner | Onboarding, Listing management, Reservations, Settlements, Account procedures |

This taxonomy guides organization and evaluation; it does not mean the assistant can execute the underlying transactions.

## 10. Key user journeys

### 10.1 Guest asks a knowledge-base question
1. Guest opens chat and submits a natural-language question.
2. Backend interprets and, where useful, rewrites the query.
3. Hybrid retrieval finds relevant content.
4. Reranking selects relevant chunks.
5. Context is assembled and evidence is evaluated.
6. An approval check prevents unapproved content from supporting an answer.
7. The assistant generates a grounded response, partial response, clarification or abstention.
8. Guest can ask a follow-up question.

### 10.2 Guest query requires human investigation
1. Assistant determines available evidence cannot resolve the issue.
2. Assistant offers human assistance.
3. Guest chooses Yes or No.
4. If No, the offer is dismissed and no ticket is created.
5. If Yes, the assistant displays the ticket form.
6. Required details are collected, including guest email if not already available.
7. Guest explicitly consents to ticket submission.
8. Backend creates the ticket and stores the relevant conversation transcript.
9. Guest sees the ticket reference.
10. Agent reviews the ticket in the dashboard and follows up by email.

### 10.3 Agent reviews a ticket
1. Agent opens the ticket dashboard.
2. Agent views ticket information and conversation context.
3. Agent updates the ticket status as work progresses.
4. Agent follows up by email outside SupportIQ chat.

## 11. Functional requirements summary

| ID | Requirement | Priority |
|---|---|---|
| PR-01 | Accept natural-language guest and partner questions | P0 |
| PR-02 | Retrieve relevant knowledge using dense and keyword search | P0 |
| PR-03 | Fuse and rerank retrieved results | P0 |
| PR-04 | Evaluate evidence before answer generation | P0 |
| PR-05 | Use approved evidence only for generated answers | P0 |
| PR-06 | Support partial answers and disclose missing information | P0 |
| PR-07 | Abstain when evidence is insufficient | P0 |
| PR-08 | Provide source references for supported answers | P0 |
| PR-09 | Maintain conversation context for follow-ups | P0 |
| PR-10 | Offer human assistance for issues requiring investigation | P1 |
| PR-11 | Ask permission before showing the ticket form | P1 |
| PR-12 | Require explicit consent before ticket submission | P1 |
| PR-13 | Prevent more than one ticket per conversation | P1 |
| PR-14 | Store ticket details and relevant conversation transcript | P1 |
| PR-15 | Display ticket reference and basic status | P1 |
| PR-16 | Allow agents to view tickets and update basic status | P1 |

Detailed behavior is specified in [FRD.md](FRD.md).

## 12. Success measures

No production performance baseline is claimed. Evaluate with measurable indicators:

| Dimension | Example measure |
|---|---|
| Retrieval | Recall@k, Precision@k, MRR or nDCG |
| Evidence evaluation | Classification accuracy across sufficient, partial, constraint-only and insufficient cases |
| Grounded generation | Claim support against selected evidence |
| Citation quality | Citation correctness and source coverage |
| Safety | Unsupported-answer rate and appropriate abstention rate |
| User experience | Task completion and user feedback |
| Ticket workflow | Successful creation, consent compliance and duplicate prevention |
| Performance | End-to-end latency and LLM token/cost usage |

Include answerable, partially answerable, unsupported, ambiguous, wrong-audience and out-of-scope test questions.

## 13. Non-functional requirements

- **Groundedness:** Responses must be supported by selected approved evidence.
- **Traceability:** Evidence chunks and source metadata should be traceable during evaluation.
- **Privacy:** Do not expose secrets in source control or logs. Store only details needed for support.
- **Reliability:** Retrieval, evaluation or generation errors should fail safely rather than fabricate an answer.
- **Maintainability:** Keep retrieval, evidence evaluation, generation and ticket workflows modular.
- **Usability:** Guest and agent interfaces should communicate next steps clearly.
- **Performance:** Measure latency and model usage; tune based on evaluation rather than invented targets.

## 14. Assumptions and constraints

- StayEase is fictional; initial policies, SOPs and articles are synthetic.
- Demo approval status is project configuration, not real operational authorization.
- LLM provider and embedding/reranking models may change.
- The system depends on configured database, model API and runtime services.
- A ticket records a request for human follow-up; it does not guarantee a response time or resolution.
- Email follow-up is outside live chat; live agent chat is not implemented.

## 15. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Irrelevant retrieval | Hybrid retrieval, reranking and retrieval evaluation |
| Unsupported model claims | Evidence evaluation, approval gate and grounded-generation constraints |
| Incomplete evidence | Partial answer with explicit gaps, or abstention |
| Wrong-audience policy | Audience metadata filtering and evaluation |
| Duplicate tickets | Unique conversation reference and backend duplicate prevention |
| Implied SLA promise | Show reference and next steps without inventing a response time |
| Synthetic policy mistaken for real policy | Clearly label demo and synthetic content |

## 16. Release acceptance checklist

- [ ] Guest can submit a natural-language question.
- [ ] Retrieval returns relevant chunks for supported test cases.
- [ ] Only approved evidence is used for answer generation.
- [ ] Partial answers identify missing information.
- [ ] Unsupported questions do not trigger invented policy claims.
- [ ] Source references correspond to retrieved evidence.
- [ ] Follow-ups preserve relevant conversation context.
- [ ] Human assistance is offered when appropriate.
- [ ] Declining ticket creation does not create a ticket.
- [ ] Ticket form appears only after guest permission.
- [ ] Ticket submission requires explicit consent.
- [ ] One conversation cannot create duplicate tickets.
- [ ] Agent can view a ticket and update basic status.
- [ ] Secrets and local runtime artifacts are excluded from source control.

## 17. Future considerations

Potential future work, subject to separate product decisions:
- Better multilingual and colloquial query handling.
- Expanded evaluation datasets and regression testing.
- Knowledge-base versioning and re-indexing workflow.
- Monitoring for latency, model usage and failure rates.
- Configurable property-specific content if a reliable property-data source is introduced.

These are not commitments in the current release scope.
