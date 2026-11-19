
"use client";

import { useEffect, useMemo, useState } from "react";

type TicketStatus = "Open" | "In Progress" | "Resolved";
type ThemeName = "lobby" | "pearl" | "plum" | "sapphire" | "forest";

type Message = {
  role: string;
  content: string;
};

type Ticket = {
  ticket_id: string;
  conversation_id: string;
  guest_email: string;
  issue: string;
  issue_description: string;
  conversation_transcript: Message[];
  created_at: string;
  status: TicketStatus;
  agent_response_reference: string | null;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const THEMES: { id: ThemeName; label: string }[] = [
  { id: "lobby", label: "Lobby teal" },
  { id: "pearl", label: "Pearl" },
  { id: "plum", label: "Dusk plum" },
  { id: "sapphire", label: "Midnight sapphire" },
  { id: "forest", label: "Forest gold" },
];

const STATUSES: TicketStatus[] = ["Open", "In Progress", "Resolved"];

export default function Home() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [theme, setTheme] = useState<ThemeName>("sapphire");
  const [view, setView] = useState<"overview" | "workspace" | "resolved">("overview");
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState("");
  const [updateMessage, setUpdateMessage] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"All" | TicketStatus>("All");

  useEffect(() => {
    async function loadTickets() {
      try {
        const response = await fetch(`${API_URL}/tickets/`);
        if (!response.ok) throw new Error("Unable to fetch tickets.");

        const data = await response.json();
        const loadedTickets: Ticket[] = data.tickets ?? [];
        setTickets(loadedTickets);

        if (loadedTickets.length > 0) {
          await fetchTicketDetails(loadedTickets[0].ticket_id, false);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Something went wrong.");
      } finally {
        setLoading(false);
      }
    }

    loadTickets();
  }, []);

  async function fetchTicketDetails(ticketId: string, openWorkspace = true) {
    try {
      setDetailsLoading(true);
      setError("");
      setUpdateMessage("");

      const response = await fetch(`${API_URL}/tickets/${ticketId}`);
      if (!response.ok) throw new Error("Unable to fetch ticket details.");

      const data: Ticket = await response.json();
      setSelectedTicket(data);
      if (openWorkspace) setView("workspace");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load ticket.");
    } finally {
      setDetailsLoading(false);
    }
  }

  async function updateStatus(status: TicketStatus) {
    if (!selectedTicket || updating || status === selectedTicket.status) return;

    setUpdating(true);
    setError("");
    setUpdateMessage("");

    try {
      const response = await fetch(
        `${API_URL}/tickets/${selectedTicket.ticket_id}/status`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status }),
        }
      );

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Unable to update status.");
      }

      const updatedTicket = {
        ...selectedTicket,
        status: data.status as TicketStatus,
      };
      
      setSelectedTicket(updatedTicket);
      
      setTickets((previous) =>
        previous.map((ticket) =>
          ticket.ticket_id === updatedTicket.ticket_id
            ? { ...ticket, status: data.status }
            : ticket
        )
      );
      
      setStatusFilter("All");
      
      if (data.status === "Resolved") {
        setView("resolved");
      } else {
        setView("workspace");
      }
      
      setUpdateMessage("Ticket status updated successfully.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Status update failed.");
    } finally {
      setUpdating(false);
    }
  }

  const counts = useMemo(
    () => ({
      total: tickets.length,
      open: tickets.filter((ticket) => ticket.status === "Open").length,
      progress: tickets.filter((ticket) => ticket.status === "In Progress").length,
      resolved: tickets.filter((ticket) => ticket.status === "Resolved").length,
    }),
    [tickets]
  );

  const filteredTickets = useMemo(() => {
    const query = search.trim().toLowerCase();
  
    return tickets.filter((ticket) => {
      const matchesSearch =
        !query ||
        ticket.ticket_id.toLowerCase().includes(query) ||
        ticket.issue.toLowerCase().includes(query) ||
        ticket.guest_email.toLowerCase().includes(query);
  
      const matchesView =
        view === "resolved"
          ? ticket.status === "Resolved"
          : ticket.status !== "Resolved";
  
      const matchesStatus =
        statusFilter === "All" || ticket.status === statusFilter;
  
      return matchesSearch && matchesView && matchesStatus;
    });
  }, [tickets, search, statusFilter, view]);

  if (loading) {
    return (
      <main className="siq loading-screen">
        <div className="loading-mark">S<span>IQ</span></div>
        <p>Preparing your support workspace...</p>
      </main>
    );
  }

  if (error && tickets.length === 0) {
    return (
      <main className="siq loading-screen">
        <div className="glass error-panel">
          <h2>Unable to load SupportIQ</h2>
          <p>{error}</p>
          <button className="gold-button" onClick={() => window.location.reload()}>
            Try again
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className={`siq theme-${theme}`}>
      <div className="app-shell">
        <aside className="sidebar glass">
          <button className="brand" onClick={() => setView("overview")}>
            <span className="brand-mark">S</span>
            <span>
              <strong>Support<span>IQ</span></strong>
              <small>Hospitality support platform</small>
            </span>
          </button>

          <div className="sidebar-label">WORKSPACE</div>
          <button
            className={`nav-item ${view === "overview" ? "active" : ""}`}
            onClick={() => setView("overview")}
          >
            <span className="nav-icon">◈</span>
            Dashboard
          </button>
          <button
  className={`nav-item ${view === "workspace" ? "active" : ""}`}
  onClick={() => {
    setStatusFilter("All");
    setView("workspace");
    if (!selectedTicket && tickets.length > 0) {
      const activeTicket = tickets.find(
        (ticket) => ticket.status !== "Resolved"
      );
      if (activeTicket) fetchTicketDetails(activeTicket.ticket_id, false);
    }
  }}
>
  <span className="nav-icon">▤</span>
  Ticket workspace
  <span className="nav-count">
    {tickets.filter((ticket) => ticket.status !== "Resolved").length}
  </span>
</button>

<button
  className={`nav-item ${view === "resolved" ? "active" : ""}`}
  onClick={() => {
    setStatusFilter("All");
    setView("resolved");
    const resolvedTicket = tickets.find(
      (ticket) => ticket.status === "Resolved"
    );
    if (resolvedTicket) fetchTicketDetails(resolvedTicket.ticket_id, false);
    else setSelectedTicket(null);
  }}
>
  <span className="nav-icon">✓</span>
  Resolved
  <span className="nav-count">
    {counts.resolved}
  </span>
</button>

          <div className="sidebar-note">
            <span className="online-dot" />
            <div>
              <strong>Support system online</strong>
              <small>StayEase agent workspace</small>
            </div>
          </div>

          <div className="profile">
            <div className="avatar">SE</div>
            <div>
              <strong>StayEase Support</strong>
              <small>Agent workspace</small>
            </div>
            <span className="profile-menu">•••</span>
          </div>
        </aside>

        <section className="main-area">
          <header className="topbar">
            <div className="breadcrumb">
              <span>StayEase</span><span>/</span>
              <strong>{view === "overview" ? "Dashboard" : "Ticket workspace"}</strong>
            </div>
            <div className="topbar-right">
              <span className="system-status"><i /> System operational</span>
              <div className="top-avatar">SE</div>
            </div>
          </header>

          {view === "overview" ? (
            <div className="page-content">
              <section className="welcome-panel glass">
                <div className="welcome-copy">
                  <span className="eyebrow">STAYEASE · SUPPORT OPERATIONS</span>
                  <h1>Welcome back,<br /><em>Support Team.</em></h1>
                  <p>Your guest support workspace at a glance. Review incoming requests and keep every guest interaction on track.</p>
                  <button
                    className="gold-button"
                    onClick={() => {
                      if (selectedTicket) setView("workspace");
                      else if (tickets.length) fetchTicketDetails(tickets[0].ticket_id);
                    }}
                  >
                    Open ticket workspace <span>↗</span>
                  </button>
                </div>
                <div className="welcome-art" aria-hidden="true">
                  <div className="orbit orbit-one" />
                  <div className="orbit orbit-two" />
                  <div className="art-center">S<span>IQ</span></div>
                  <div className="art-caption">HOSPITALITY<br />WITH CARE</div>
                  <div className="art-star">✦</div>
                </div>
              </section>

              <section className="theme-section">
                <div className="section-heading">
                  <div>
                    <span className="eyebrow">MAKE IT YOURS</span>
                    <h2>Choose your atmosphere</h2>
                  </div>
                  <span className="section-hint">Personalise your workspace</span>
                </div>
                <div className="theme-picker glass">
                  {THEMES.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setTheme(item.id)}
                      className={`theme-option ${theme === item.id ? "selected" : ""}`}
                      aria-pressed={theme === item.id}
                    >
                      <span className={`theme-swatch swatch-${item.id}`} />
                      {item.label}
                      {theme === item.id && <span className="theme-check">✓</span>}
                    </button>
                  ))}
                </div>
              </section>

              <section className="metrics-grid">
                <MetricCard label="Total tickets" value={counts.total} icon="▤" detail="All support requests" tone="gold" />
                <MetricCard label="Open" value={counts.open} icon="◷" detail="Awaiting attention" tone="amber" />
                <MetricCard label="In progress" value={counts.progress} icon="◌" detail="Being investigated" tone="blue" />
                <MetricCard label="Resolved" value={counts.resolved} icon="✓" detail="Successfully closed" tone="green" />
              </section>

              <section className="overview-grid">
                <div className="glass ticket-overview-card">
                  <div className="card-heading">
                    <div>
                      <span className="eyebrow">YOUR QUEUE</span>
                      <h2>Recent tickets</h2>
                      <p>Guest support requests requiring visibility.</p>
                    </div>
                    <button className="text-action" onClick={() => setView("workspace")}>
                      View workspace <span>→</span>
                    </button>
                  </div>

                  {tickets.length === 0 ? (
                    <EmptyState title="No tickets yet" description="New guest support tickets will appear here." />
                  ) : (
                    <div className="recent-list">
                      {tickets.slice(0, 5).map((ticket) => (
                        <button
                          className={`recent-ticket ${selectedTicket?.ticket_id === ticket.ticket_id ? "chosen" : ""}`}
                          key={ticket.ticket_id}
                          onClick={() => fetchTicketDetails(ticket.ticket_id)}
                        >
                          <span className="ticket-symbol">◇</span>
                          <span className="recent-main">
                            <strong>{ticket.issue}</strong>
                            <small>{ticket.ticket_id} · {ticket.guest_email}</small>
                          </span>
                          <StatusBadge status={ticket.status} />
                          <span className="row-arrow">↗</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <div className="glass overview-side-card">
                  <span className="eyebrow">SUPPORT SNAPSHOT</span>
                  <h2>Every request<br /><em>matters.</em></h2>
                  <p>SupportIQ keeps guest conversations and support investigations together, so your team has the context it needs.</p>
                  <div className="snapshot-line">
                    <span>Tickets resolved</span>
                    <strong>{counts.resolved} <small>/ {counts.total}</small></strong>
                  </div>
                  <div className="progress-track">
                    <span style={{ width: `${counts.total ? (counts.resolved / counts.total) * 100 : 0}%` }} />
                  </div>
                  <small className="snapshot-footnote">Based on current ticket records</small>
                </div>
              </section>

              {error && <div className="inline-alert">{error}</div>}
            </div>
          ) : (
            <div className="page-content workspace-content">
              <div className="workspace-heading">
                <div>
                  <span className="eyebrow">STAYEASE · SUPPORT OPERATIONS</span>
                  <h1>Ticket <em>workspace.</em></h1>
                  <p>Review guest requests and their original conversations.</p>
                </div>
                <button className="subtle-button" onClick={() => setView("overview")}>← Back to overview</button>
              </div>

              <section className="metrics-grid compact-metrics">
                <MetricCard label="Total tickets" value={counts.total} icon="▤" detail="All requests" tone="gold" />
                <MetricCard label="Open" value={counts.open} icon="◷" detail="Awaiting attention" tone="amber" />
                <MetricCard label="In progress" value={counts.progress} icon="◌" detail="Being investigated" tone="blue" />
                <MetricCard label="Resolved" value={counts.resolved} icon="✓" detail="Successfully closed" tone="green" />
              </section>

              <section className="workspace-grid">
                <div className="glass ticket-list-panel">
                  <div className="card-heading">
                    <div>
                      <span className="eyebrow">SUPPORT QUEUE</span>
                      <h2>
  {view === "resolved" ? "Resolved tickets" : "Active tickets"}
  <span className="count-pill">{filteredTickets.length}</span>
</h2>
                    </div>
                  </div>

                  <div className="ticket-tools">
                    <div className="search-box">
                      <span>⌕</span>
                      <input
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                        placeholder="Search tickets..."
                        aria-label="Search tickets"
                      />
                    </div>
                    <select
                      value={statusFilter}
                      onChange={(event) =>
                        setStatusFilter(event.target.value as "All" | TicketStatus)
                      }
                      aria-label="Filter by status"
                    >
                      <option value="All">All statuses</option>
                      {(view === "resolved"
  ? ["Resolved"]
  : ["Open", "In Progress"]
).map((status) => (
  <option key={status} value={status}>
    {status}
  </option>
))}
                    </select>
                  </div>

                  <div className="workspace-ticket-list">
                    {filteredTickets.length === 0 ? (
                      <EmptyState title="No matching tickets" description="Try changing your search or status filter." />
                    ) : (
                      filteredTickets.map((ticket) => (
                        <button
                          key={ticket.ticket_id}
                          className={`workspace-ticket ${selectedTicket?.ticket_id === ticket.ticket_id ? "chosen" : ""}`}
                          onClick={() => fetchTicketDetails(ticket.ticket_id, false)}
                        >
                          <div className="workspace-ticket-top">
                            <strong>{ticket.ticket_id}</strong>
                            <StatusBadge status={ticket.status} />
                          </div>
                          <h3>{ticket.issue}</h3>
                          <p>{ticket.guest_email}</p>
                          <small>{new Date(ticket.created_at).toLocaleDateString("en-IN")}</small>
                        </button>
                      ))
                    )}
                  </div>
                </div>

                <div className="glass detail-panel">
                  {detailsLoading ? (
                    <EmptyState title="Loading ticket..." description="Fetching ticket details." />
                  ) : selectedTicket ? (
                    <TicketDetails
                      ticket={selectedTicket}
                      updating={updating}
                      error={error}
                      updateMessage={updateMessage}
                      onStatusChange={updateStatus}
                    />
                  ) : (
                    <EmptyState title="Select a ticket" description="Choose a ticket from the list to view its details." />
                  )}
                </div>
              </section>
            </div>
          )}

          <footer className="page-footer">
            <span>SUPPORTIQ</span>
            <span>Thoughtful support. Better stays.</span>
            <span>StayEase · Agent workspace</span>
          </footer>
        </section>
      </div>
    </main>
  );
}

function MetricCard({
  label, value, icon, detail, tone,
}: {
  label: string;
  value: number;
  icon: string;
  detail: string;
  tone: string;
}) {
  return (
    <div className={`glass metric-card metric-${tone}`}>
      <div className="metric-top">
        <span>{label}</span>
        <span className="metric-icon">{icon}</span>
      </div>
      <strong>{value.toString().padStart(2, "0")}</strong>
      <small>{detail}</small>
    </div>
  );
}

function StatusBadge({ status }: { status: TicketStatus }) {
  return (
    <span className={`status-badge status-${status.toLowerCase().replace(" ", "-")}`}>
      <i />
      {status}
    </span>
  );
}

function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="empty-state">
      <span>◇</span>
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}

function TicketDetails({
  ticket, updating, error, updateMessage, onStatusChange,
}: {
  ticket: Ticket;
  updating: boolean;
  error: string;
  updateMessage: string;
  onStatusChange: (status: TicketStatus) => void;
}) {
  return (
    <>
      <div className="detail-header">
        <div>
          <span className="eyebrow">TICKET DETAILS</span>
          <h2>{ticket.ticket_id}</h2>
        </div>
        <StatusBadge status={ticket.status} />
      </div>

      <div className="detail-fields">
        <DetailField label="Guest email" value={ticket.guest_email} />
        <DetailField label="Issue" value={ticket.issue} />
        <DetailField label="Description" value={ticket.issue_description} />
        <DetailField label="Conversation ID" value={ticket.conversation_id} />
        <DetailField label="Created on" value={new Date(ticket.created_at).toLocaleString("en-IN")} />
      </div>

      <div className="status-editor">
        <span className="field-label">UPDATE TICKET STATUS</span>
        <div className="status-controls">
          {STATUSES.map((status) => (
            <button
              key={status}
              disabled={updating}
              aria-pressed={ticket.status === status}
              className={ticket.status === status ? "current" : ""}
              onClick={() => onStatusChange(status)}
            >
              {status}
            </button>
          ))}
        </div>
        {updating && <p className="success-message">Updating status...</p>}
        {updateMessage && <p className="success-message">{updateMessage}</p>}
        {error && <p className="error-message">{error}</p>}
      </div>

      {ticket.agent_response_reference && (
        <div className="response-reference">
          <span className="field-label">AGENT EMAIL RESPONSE REFERENCE</span>
          <p>{ticket.agent_response_reference}</p>
        </div>
      )}

      <div className="conversation-section">
        <div className="conversation-heading">
          <div>
            <span className="eyebrow">GUEST INTERACTION</span>
            <h3>Original conversation</h3>
          </div>
          <span className="message-count">{ticket.conversation_transcript.length} messages</span>
        </div>

        {ticket.conversation_transcript.length === 0 ? (
          <p className="conversation-empty">No conversation transcript is available.</p>
        ) : (
          <div className="conversation-list">
            {ticket.conversation_transcript.map((message, index) => {
              const guest = message.role === "user";
              return (
                <div className={`message-bubble ${guest ? "guest-message" : "assistant-message"}`} key={index}>
                  <span>{guest ? "GUEST" : "SUPPORTIQ"}</span>
                  <p>{message.content}</p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div className="detail-field">
      <span className="field-label">{label}</span>
      <p>{value}</p>
    </div>
  );
}
