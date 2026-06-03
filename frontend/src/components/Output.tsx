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

interface OutputProps {
  content: string | null;
  running: boolean;
  vinklingOutput: string | null;
  sources: ResearchSource[] | null;
  interviewPrep: string | null;
}

export default function Output({ content, running, vinklingOutput, sources, interviewPrep }: OutputProps) {
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

      <p className="ai-disclaimer">
        AI-generert innhold. Kan inneholde feil eller utdatert informasjon –
        kvalitetssikre alltid før bruk.
      </p>
    </div>
  );
}
