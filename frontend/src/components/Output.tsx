import { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { ResearchSource } from "../types";

type OutputTab = "resultat" | "analyse";

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

function ValidationStatus({ validation }: { validation: string }) {
  const isOk = validation.toLowerCase().includes("ingen avvik");
  return (
    <div className={`faktasjekk-status ${isOk ? "faktasjekk-ok" : "faktasjekk-issues"}`}>
      <span className="faktasjekk-indicator">{isOk ? "✓" : "!"}</span>
      <div className="faktasjekk-body">
        <div className="faktasjekk-title">
          {isOk ? "Ingen avvik funnet" : "Mulige avvik – sjekk før du sender"}
        </div>
        {!isOk && (
          <div className="faktasjekk-detail">
            <ReactMarkdown>{validation}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

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
  const [activeTab, setActiveTab] = useState<OutputTab>("resultat");

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

  const hasValidationIssues = validation ? !validation.toLowerCase().includes("ingen avvik") : false;
  const hasAnalyseContent =
    Object.keys(agentLog).length > 0 ||
    validation !== null ||
    (sources !== null && sources.length > 0);

  return (
    <div className="output">
      <div className="output-tabs">
        <button
          className={`output-tab ${activeTab === "resultat" ? "active" : ""}`}
          onClick={() => setActiveTab("resultat")}
        >
          Resultat
        </button>
        {hasAnalyseContent && (
          <button
            className={`output-tab ${activeTab === "analyse" ? "active" : ""}`}
            onClick={() => setActiveTab("analyse")}
          >
            Analyse
            {validation !== null && (
              <span className={`tab-badge ${hasValidationIssues ? "tab-badge--warning" : "tab-badge--ok"}`}>
                {hasValidationIssues ? "!" : "✓"}
              </span>
            )}
          </button>
        )}
      </div>

      {activeTab === "resultat" && (
        <>
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
        </>
      )}

      {activeTab === "analyse" && (
        <>
          {validation && (
            <Collapsible
              label="Faktasjekk"
              count={hasValidationIssues ? "sjekk" : "ok"}
              defaultOpen
            >
              <ValidationStatus validation={validation} />
            </Collapsible>
          )}
          {agentLog.Kravleser && (
            <Collapsible label="Kravanalyse">
              <ReactMarkdown>{agentLog.Kravleser}</ReactMarkdown>
            </Collapsible>
          )}
          {agentLog.Match && (
            <Collapsible label="Match-analyse">
              <ReactMarkdown>{agentLog.Match}</ReactMarkdown>
            </Collapsible>
          )}
          {agentLog.Research && (
            <Collapsible label="Selskapsresearch">
              <ReactMarkdown>{agentLog.Research}</ReactMarkdown>
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
          {agentLog.Orchestrator && (
            <Collapsible label="Pipeline">
              <ReactMarkdown>{agentLog.Orchestrator}</ReactMarkdown>
            </Collapsible>
          )}
        </>
      )}
    </div>
  );
}
