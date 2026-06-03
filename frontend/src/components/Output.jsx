import { useState } from "react";
import ReactMarkdown from "react-markdown";


function Collapsible({ label, count, children }) {
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

export default function Output({ content, running, vinklingOutput, sources, interviewPrep, onRefine, refining }) {
  const [refinementText, setRefinementText] = useState("");

  const handleSend = () => {
    if (!refinementText.trim() || refining) return;
    onRefine(refinementText.trim());
    setRefinementText("");
  };
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
        <button className="copy-btn" onClick={() => navigator.clipboard.writeText(content)}>
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
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>

      {content && !running && (
        <div className="refinement-form">
          <input
            className="refinement-input"
            placeholder='Endre noe… (f.eks. "gjør åpningen kortere")'
            value={refinementText}
            onChange={(e) => setRefinementText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={refining}
          />
          <button
            className="refinement-btn"
            onClick={handleSend}
            disabled={refining || !refinementText.trim()}
          >
            {refining ? <span className="spinner" /> : "Oppdater"}
          </button>
        </div>
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
    </div>
  );
}
