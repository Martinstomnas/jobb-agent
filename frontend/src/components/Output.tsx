import { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { ResearchSource } from "../types";

interface CollapsibleProps {
  label: string;
  count?: string | null;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

function Collapsible({ label, count, children, defaultOpen = false }: CollapsibleProps) {
  const [open, setOpen] = useState(defaultOpen);
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

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      if (!navigator.clipboard?.writeText) return;
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore copy failures (e.g. permissions)
    }
  };

  return (
    <div className="copy-icon-wrap">
      <button
        className="copy-icon-btn"
        onClick={handleCopy}
        data-tooltip={copied ? "Kopiert!" : "Kopier"}
      >
        {copied ? (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        ) : (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
        )}
      </button>
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
      {vinklingOutput && (
        <div className="vinkling-callout">
          <span className="vinkling-label">Anbefalt vinkling</span>
          <p>{vinklingOutput}</p>
        </div>
      )}

      <Collapsible label="Søknadsdisposisjon" defaultOpen>
        <ReactMarkdown>{content!}</ReactMarkdown>
        <CopyButton text={content!} />
      </Collapsible>

      {interviewPrep && (
        <Collapsible label="Intervjuforberedelse">
          <ReactMarkdown>{interviewPrep}</ReactMarkdown>
          <CopyButton text={interviewPrep} />
        </Collapsible>
      )}

      {validation && (
        <Collapsible
          label="Faktasjekk"
          count={validation.includes("Ingen avvik funnet") ? "ok" : "funn"}
        >
          <ReactMarkdown>{validation}</ReactMarkdown>
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
