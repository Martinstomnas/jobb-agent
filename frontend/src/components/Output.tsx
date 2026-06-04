import { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { ResearchSource } from "../types";

interface CollapsibleProps {
  label: string;
  count?: string | null;
  children: React.ReactNode;
}

function Collapsible({ label, count, children }: CollapsibleProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="sources-section">
      <button className="sources-toggle" onClick={() => setOpen((o) => !o)}>
        <span className="sources-toggle-label">{label}</span>
        {count != null && <span className="sources-toggle-count">{count}</span>}
        <span className="sources-toggle-arrow">{open ? "–" : "+"}</span>
      </button>
      {open && <div className="sources-list interview-content">{children}</div>}
    </div>
  );
}

const LOG_ORDER = ["Kravleser", "Research", "Match", "Orchestrator"] as const;
const LOG_LABELS: Record<string, string> = {
  Kravleser: "Kravleser — ekstraherte krav",
  Research: "Research — selskapsinfo",
  Match: "Match — full analyse",
  Orchestrator: "Orchestrator — pipeline-plan",
};

interface OutputProps {
  content: string | null;
  running: boolean;
  vinklingOutput: string | null;
  sources: ResearchSource[] | null;
  interviewPrep: string | null;
  validation: string | null;
  agentLog: Record<string, string>;
}

export default function Output({ content, running, vinklingOutput, sources, interviewPrep, validation, agentLog }: OutputProps) {
  if (!content && !running) {
    return (
      <div className="output output-empty">
        <div className="output-placeholder">
          <p>Søknadsdisposisjonen vises her når agentene er ferdige</p>
        </div>
      </div>
    );
  }

  if (running && !content) {
    return (
      <div className="output output-loading">
        <div className="output-placeholder">
          <span className="spinner large" />
          <p>Agentene jobber...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="output">
      <div className="output-header">
        {running ? (
          <span className="output-done-badge" style={{ color: "var(--running)", display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="spinner" />
            Oppdaterer...
          </span>
        ) : (
          <span className="output-done-badge">Søknadsdisposisjon</span>
        )}
        <button className="copy-btn" onClick={() => navigator.clipboard.writeText(content!)}>
          Kopier
        </button>
      </div>

      {vinklingOutput && (
        <div className="vinkling-callout">
          <span className="vinkling-label">Anbefalt vinkling</span>
          <p>{vinklingOutput}</p>
        </div>
      )}

      <div className="output-content">
        <ReactMarkdown>{content!}</ReactMarkdown>
      </div>

      {validation && (
        <Collapsible
          label="Faktasjekk"
          count={validation.includes("Ingen avvik funnet") ? "ok" : "funn"}
        >
          <ReactMarkdown>{validation}</ReactMarkdown>
        </Collapsible>
      )}

      {interviewPrep && (
        <Collapsible label="Intervjuforberedelse">
          <ReactMarkdown>{interviewPrep}</ReactMarkdown>
        </Collapsible>
      )}

      {sources && sources.length > 0 && (
        <Collapsible label="Søkelogg" count={`${sources.length} søk`}>
          {sources.map((s, i) => (
            <div key={i} className="source-group">
              <div className="source-query">"{s.query}"</div>
              <ul className="source-urls">
                {s.results.map((r, j) => (
                  <li key={j}>
                    <span className="source-title">{r.title}</span>
                    <span className="source-url">{r.url}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </Collapsible>
      )}

      {LOG_ORDER.some(a => agentLog[a]) && (
        <Collapsible label="Agentlogg" count={`${LOG_ORDER.filter(a => agentLog[a]).length} agenter`}>
          {LOG_ORDER.filter(a => agentLog[a]).map(agent => (
            <div key={agent} className="log-entry">
              <div className="log-agent-label">{LOG_LABELS[agent]}</div>
              <ReactMarkdown>{agentLog[agent]}</ReactMarkdown>
            </div>
          ))}
        </Collapsible>
      )}
    </div>
  );
}
