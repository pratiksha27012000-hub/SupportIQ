
"use client";

import { FormEvent, useState } from "react";

type Citation = {
  chunk_id?: string;
  document_id?: string;
  document_name?: string;
  section?: string | null;
  page_number?: number | null;
  status?: string;
};

type Message = {
  role: "guest" | "assistant";
  content: string;
  citations?: Citation[];
  ticketOffer?: boolean;
};

type ChatResponse = {
  conversation_id: string;
  rag_result?: {
    evidence_gate?: {
      offer_human_assistance?: boolean;
    };
    approval_assessment?: {
      approved?: boolean;
    };
    generation_control?: {
      allowed?: boolean;
      status?: string;
    };
    generation?: {
      answer?: string | null;
      citations?: Citation[];
      status?: string;
      reason?: string;
    };
    context?: {
      citations?: Citation[];
    };
  };
};

type TicketResponse = {
  message: string;
  ticket_id: string;
  conversation_id: string;
  status: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const suggestions = [
  {
    icon: "✦",
    title: "Booking & reservations",
    question: "How can I check my booking confirmation?",
  },
  {
    icon: "↗",
    title: "Cancellations & refunds",
    question: "What is the cancellation and refund policy?",
  },
  {
    icon: "◷",
    title: "Payments",
    question: "I think I was charged twice. What should I do?",
  },
  {
    icon: "⌂",
    title: "Check-in & check-out",
    question: "What are the check-in requirements?",
  },
];

export default function GuestChat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Ticket creation states
  const [ticketEmail, setTicketEmail] = useState("");
  const [ticketIssue, setTicketIssue] = useState("");
  const [ticketDescription, setTicketDescription] = useState("");
  const [ticketConsent, setTicketConsent] = useState(false);
  const [ticketDecision, setTicketDecision] = useState<"pending" | "accepted" | "declined" | null>(null);
  const [ticketLoading, setTicketLoading] = useState(false);
  const [ticketReference, setTicketReference] = useState("");
  const [ticketError, setTicketError] = useState("");

  async function sendQuestion(question: string) {
    if (!question.trim() || loading) return;

    if (!API_URL) {
      setError("Backend API URL is not configured.");
      return;
    }

    const currentConversationId =
      conversationId ?? crypto.randomUUID();

    setConversationId(currentConversationId);
    setError("");
    setLoading(true);

    setMessages((previous) => [
      ...previous,
      { role: "guest", content: question },
    ]);

    try {
      const response = await fetch(`${API_URL}/chat/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          conversation_id: currentConversationId,
          audience: "Guest",
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to process your question."
        );
      }

      const result = data as ChatResponse;

      const generation = result.rag_result?.generation;
      const evidenceGate = result.rag_result?.evidence_gate;
      // Human assistance is a separate decision from document approval.
      // The backend evidence gate controls whether a ticket can be offered.
      const shouldOfferTicket =
        evidenceGate?.offer_human_assistance === true;

      const citations =
        generation?.citations ??
        result.rag_result?.context?.citations ??
        [];

      const assistantMessage: Message = {
        role: "assistant",
        // Keep the answer separate from the ticket permission prompt.
        // The ticket offer below asks permission before showing the form.
        content:
          generation?.answer ||
          "I'm sorry, I couldn't verify enough information to resolve this automatically.",
        citations,
        ticketOffer: shouldOfferTicket,
      };

      if (shouldOfferTicket && !ticketReference) {
        setTicketDecision("pending");
        setTicketError("");
      }

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);

      if (result.conversation_id) {
        setConversationId(result.conversation_id);
      }
    } catch (err) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          // Keep API keys, provider errors and internal exception details
          // out of the guest-facing conversation.
          content:
            "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function createGuestTicket() {
    if (!conversationId || !API_URL || ticketLoading) return;

    if (
      !ticketEmail.trim() ||
      !ticketIssue.trim() ||
      !ticketDescription.trim()
    ) {
      setTicketError("Please complete all ticket details.");
      return;
    }

    if (!ticketConsent) {
      setTicketError("Please provide consent before creating a ticket.");
      return;
    }

    setTicketLoading(true);
    setTicketError("");

    try {
      const transcript = messages.map((message) => ({
        role: message.role === "guest" ? "user" : "assistant",
        content: message.content,
      }));

      const response = await fetch(`${API_URL}/tickets/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          guest_email: ticketEmail.trim(),
          issue: ticketIssue.trim(),
          issue_description: ticketDescription.trim(),
          conversation_transcript: transcript,
          consent: true,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to create your ticket."
        );
      }

      const result = data as TicketResponse;

      setTicketReference(result.ticket_id);
      setTicketDecision(null);
      setTicketConsent(false);
      setTicketError("");
    } catch (err) {
      setTicketError(
        err instanceof Error
          ? err.message
          : "Something went wrong while creating your ticket."
      );
    } finally {
      setTicketLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    void sendQuestion(question);
  }

  function startSuggestion(question: string) {
    void sendQuestion(question);
  }

  function startNewConversation() {
    if (loading || ticketLoading) return;

    setMessages([]);
    setConversationId(null);
    setInput("");
    setError("");

    setTicketEmail("");
    setTicketIssue("");
    setTicketDescription("");
    setTicketConsent(false);
    setTicketDecision(null);
    setTicketReference("");
    setTicketError("");
  }

  return (
    <main className="min-h-screen bg-[#f5f2ec] text-[#263c40]">
      <div className="mx-auto flex min-h-screen max-w-[1500px] flex-col px-5 md:px-12">

        <header className="flex h-20 items-center justify-between border-b border-[#dedbd3]">
          <a href="/chat" className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-full bg-[#185d5b] text-lg font-semibold text-white">
              S
            </div>

            <div>
              <h1 className="text-xl font-semibold tracking-tight">
                Support<span className="text-[#b38b4d]">IQ</span>
              </h1>

              <p className="text-[10px] uppercase tracking-[0.2em] text-[#788681]">
                Powered by StayEase
              </p>
            </div>
          </a>

          <button
            onClick={startNewConversation}
            disabled={loading || ticketLoading}
            className="rounded-full border border-[#d8d5cd] px-4 py-2 text-sm transition hover:bg-white disabled:opacity-40"
          >
            + New conversation
          </button>
        </header>

        <section className="mx-auto flex w-full max-w-5xl flex-1 flex-col py-10 md:py-14">

          {messages.length === 0 ? (
            <div className="flex flex-1 flex-col justify-center">
              <div className="mb-10 text-center">
                <div className="mx-auto mb-6 grid h-16 w-16 place-items-center rounded-2xl bg-[#e4ebe5] text-3xl text-[#185d5b]">
                  ✦
                </div>

                <p className="mb-4 text-xs font-semibold uppercase tracking-[0.25em] text-[#a17c43]">
                  Your StayEase assistant
                </p>

                <h2 className="font-serif text-4xl leading-tight md:text-6xl">
                  How can we make
                  <br />
                  your stay <em>better?</em>
                </h2>

                <p className="mx-auto mt-5 max-w-xl text-base leading-7 text-[#71807b]">
                  Ask us about your reservation, payments, cancellations or
                  anything related to your stay. We're here to help.
                </p>
              </div>

              <div className="mb-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
                {suggestions.map((item) => (
                  <button
                    key={item.title}
                    onClick={() => startSuggestion(item.question)}
                    disabled={loading}
                    className="group rounded-2xl border border-[#dedbd3] bg-white/70 p-5 text-left transition hover:-translate-y-0.5 hover:border-[#9baf9f] hover:bg-white disabled:opacity-50"
                  >
                    <span className="mb-3 block text-xl text-[#b18b50]">
                      {item.icon}
                    </span>

                    <strong className="block text-sm font-semibold">
                      {item.title}
                    </strong>

                    <span className="mt-2 block text-sm leading-6 text-[#7c8983]">
                      {item.question}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 space-y-8 pb-10">
              <div className="text-center">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#a17c43]">
                  StayEase · Guest assistance
                </p>
              </div>

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "guest"
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-3xl px-6 py-5 md:max-w-[75%] ${
                      message.role === "guest"
                        ? "rounded-br-md bg-[#185d5b] text-white"
                        : "rounded-bl-md border border-[#dedbd3] bg-white"
                    }`}
                  >
                    <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.18em] opacity-70">
                      {message.role === "guest" ? "You" : "SupportIQ"}
                    </p>

                    <p className="whitespace-pre-wrap text-[15px] leading-7">
                      {message.content}
                    </p>

                    {/* Citations remain in message data for internal use.
                        They are intentionally hidden from the guest UI. */}

                    {/* Human assistance and ticket creation */}
                    {message.role === "assistant" &&
                      message.ticketOffer &&
                      !ticketReference && (
                        <div className="mt-5 border-t border-[#e8e4dc] pt-4">
                          <p className="text-sm leading-6 text-[#71807b]">
                            This query may need assistance from our support team.
                            Would you like us to create a support ticket?
                          </p>

                          {ticketDecision === "pending" && (
                            <div className="mt-4 flex flex-wrap gap-3">
                              <button
                                type="button"
                                onClick={() => {
                                  setTicketDecision("accepted");
                                  setTicketError("");
                                }}
                                className="rounded-full bg-[#185d5b] px-5 py-3 text-sm font-medium text-white transition hover:bg-[#124846]"
                              >
                                Yes, create a ticket
                              </button>

                              <button
                                type="button"
                                onClick={() => {
                                  setTicketDecision("declined");
                                  setTicketError("");
                                }}
                                className="rounded-full border border-[#d8d5cd] px-5 py-3 text-sm transition hover:bg-white"
                              >
                                No, thanks
                              </button>
                            </div>
                          )}

                          {ticketDecision === "declined" && (
                            <p className="mt-4 text-sm leading-6 text-[#71807b]">
                              No problem. We won't create a ticket. You can
                              continue asking me questions whenever you like.
                            </p>
                          )}

                          {ticketDecision === "accepted" && !ticketReference && (
                            <div className="mt-4 space-y-4 rounded-2xl bg-[#f7f5f0] p-4">
                              <h3 className="font-semibold text-[#36504c]">
                                Create a support ticket
                              </h3>

                              <div>
                                <label className="mb-1 block text-xs font-medium text-[#71807b]">
                                  Guest email
                                </label>

                                <input
                                  type="email"
                                  value={ticketEmail}
                                  onChange={(event) =>
                                    setTicketEmail(event.target.value)
                                  }
                                  placeholder="you@example.com"
                                  className="w-full rounded-xl border border-[#dedbd3] bg-white px-4 py-3 text-sm outline-none focus:border-[#185d5b]"
                                  required
                                />
                              </div>

                              <div>
                                <label className="mb-1 block text-xs font-medium text-[#71807b]">
                                  Issue title
                                </label>

                                <input
                                  type="text"
                                  value={ticketIssue}
                                  onChange={(event) =>
                                    setTicketIssue(event.target.value)
                                  }
                                  placeholder="Briefly describe your issue"
                                  className="w-full rounded-xl border border-[#dedbd3] bg-white px-4 py-3 text-sm outline-none focus:border-[#185d5b]"
                                  required
                                />
                              </div>

                              <div>
                                <label className="mb-1 block text-xs font-medium text-[#71807b]">
                                  Issue description
                                </label>

                                <textarea
                                  value={ticketDescription}
                                  onChange={(event) =>
                                    setTicketDescription(event.target.value)
                                  }
                                  placeholder="Provide details to help our support team investigate."
                                  rows={4}
                                  className="w-full resize-y rounded-xl border border-[#dedbd3] bg-white px-4 py-3 text-sm outline-none focus:border-[#185d5b]"
                                  required
                                />
                              </div>

                              <label className="flex items-start gap-3 text-xs leading-5 text-[#71807b]">
                                <input
                                  type="checkbox"
                                  checked={ticketConsent}
                                  onChange={(event) =>
                                    setTicketConsent(event.target.checked)
                                  }
                                  className="mt-1 accent-[#185d5b]"
                                />

                                <span>
                                  I consent to sharing my email, issue details
                                  and conversation with the StayEase support team
                                  for assistance.
                                </span>
                              </label>

                              {ticketError && (
                                <p className="rounded-xl bg-red-50 p-3 text-xs text-red-700">
                                  {ticketError}
                                </p>
                              )}

                              <div className="flex flex-wrap gap-3">
                                <button
                                  type="button"
                                  onClick={createGuestTicket}
                                  disabled={
                                    ticketLoading ||
                                    !ticketEmail.trim() ||
                                    !ticketIssue.trim() ||
                                    !ticketDescription.trim() ||
                                    !ticketConsent
                                  }
                                  className="rounded-full bg-[#185d5b] px-5 py-3 text-sm font-medium text-white transition hover:bg-[#124846] disabled:cursor-not-allowed disabled:opacity-40"
                                >
                                  {ticketLoading
                                    ? "Creating ticket..."
                                    : "Submit ticket"}
                                </button>

                                <button
                                  type="button"
                                  onClick={() => {
                                    setTicketDecision("pending");
                                    setTicketError("");
                                  }}
                                  disabled={ticketLoading}
                                  className="rounded-full border border-[#d8d5cd] px-5 py-3 text-sm transition hover:bg-white disabled:opacity-40"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-3xl rounded-bl-md border border-[#dedbd3] bg-white px-6 py-5">
                    <p className="text-sm text-[#788681]">
                      A little digging… almost there! ✨
                    </p>
                  </div>
                </div>
              )}

              {/* Ticket creation confirmation */}
              {ticketReference && (
                <div className="rounded-2xl border border-[#b8d5c3] bg-[#edf5ee] p-5">
                  <p className="text-sm font-semibold text-[#285d42]">
                    Your support ticket has been created successfully.
                  </p>

                  <p className="mt-2 text-sm text-[#456b54]">
                    Ticket reference:
                  </p>

                  <p className="mt-1 text-lg font-bold tracking-wide text-[#285d42]">
                    {ticketReference}
                  </p>

                  <p className="mt-2 text-sm leading-6 text-[#456b54]">
                    Our support team can review your request and respond
                    through email.
                  </p>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="mb-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="sticky bottom-4 mt-8 rounded-3xl border border-[#dedbd3] bg-white p-3 shadow-[0_12px_40px_rgba(40,50,40,0.08)]"
          >
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  event.currentTarget.form?.requestSubmit();
                }
              }}
              rows={2}
              disabled={loading}
              placeholder="Ask SupportIQ anything about your stay..."
              className="w-full resize-none bg-transparent px-4 py-3 text-[15px] leading-7 outline-none placeholder:text-[#9aa39d]"
            />

            <div className="flex items-center justify-between px-3 pb-2">
              <span className="text-xs text-[#929b95]">
                {loading
                  ? "A little digging… almost there! ✨"
                  : "StayEase guest assistance"}
              </span>

              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="rounded-full bg-[#185d5b] px-6 py-3 text-sm font-medium text-white transition hover:bg-[#124846] disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? "Thinking..." : "Send ↗"}
              </button>
            </div>
          </form>

          <p className="mt-5 text-center text-xs text-[#929b95]">
            SupportIQ can make mistakes. Please verify important information.
          </p>
        </section>

        <footer className="border-t border-[#dedbd3] py-5 text-center text-xs tracking-wide text-[#929b95]">
          STAYEASE · THOUGHTFUL HOSPITALITY, EVERY STEP OF THE WAY
        </footer>
      </div>
    </main>
  );
}
