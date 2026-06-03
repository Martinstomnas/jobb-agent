import type { AgentStates, AgentStatus } from "../types";

const descriptions: Record<string, string> = {
  Kravleser: "Analyserer krav og signaler",
  Research: "Henter selskaps-info",
  Match: "Kobler krav med din profil",
  Orchestrator: "Bestemmer pipeline-strategi",
  GapDetector: "Avklarer hull i profilen",
  Writer: "Lager søknadsdisposisjon",
  InterviewPrep: "Forbereder intervju",
  Critic: "Evaluerer og forbedrer utkastet",
};

interface AgentPipelineProps {
  agents: string[];
  states: AgentStates;
  running: boolean;
}

export default function AgentPipeline({ agents, states, running: _running }: AgentPipelineProps) {
  return (
    <div className="pipeline">
      <div className="pipeline-title">Agenter</div>
      <div className="pipeline-agents">
        {agents.map((agent, i) => {
          const state = states[agent];
          const status: AgentStatus = state?.status ?? "idle";

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
                {status === "warning" && <span className="pulse" style={{ background: "var(--running)" }} />}
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
