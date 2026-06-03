const descriptions = {
  Kravleser: "Analyserer krav og signaler",
  Research: "Henter selskaps-info",
  Match: "Kobler krav med din profil",
  GapDetector: "Avklarer hull i profilen",
  Writer: "Lager søknadsdisposisjon",
  InterviewPrep: "Forbereder intervju",
  Kontroll: "Validerer disposisjonen",
};

export default function AgentPipeline({ agents, states, running }) {
  return (
    <div className="pipeline">
      <div className="pipeline-title">Agenter</div>
      <div className="pipeline-agents">
        {agents.map((agent, i) => {
          const state = states[agent];
          const status = state?.status ?? "idle";

          return (
            <div key={agent} className={`agent-card agent-${status}`}>
              <div className="agent-left">
                <span className="agent-icon">{String(i + 1).padStart(2, "0")}</span>
                <div>
                  <div className="agent-name">{agent}</div>
                  <div className="agent-desc">{descriptions[agent]}</div>
                </div>
              </div>
              <div className="agent-status">
                {status === "running" && <span className="pulse" />}
                {status === "done" && <span className="checkmark">ok</span>}
                {status === "question" && <span className="pulse" style={{ background: "var(--accent2)" }} />}
                {status === "idle" && <span className="idle-dot" />}
              </div>
              {i < agents.length - 1 && (
                <div
                  className={`connector ${status === "done" ? "connector-done" : ""}`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
