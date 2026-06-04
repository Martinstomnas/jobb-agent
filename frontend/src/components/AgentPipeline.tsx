import type { AgentStates, AgentStatus } from "../types";

interface AgentPipelineProps {
  agents: string[];
  states: AgentStates;
}

export default function AgentPipeline({ agents, states }: AgentPipelineProps) {
  const doneCount = agents.filter((a) => states[a]?.status === "done").length;
  const progressPct = agents.length > 0 ? (doneCount / agents.length) * 100 : 0;
  const hasStarted = Object.keys(states).length > 0;

  return (
    <div className="pipeline">
      <div className="pipeline-header">
        <span className="pipeline-title">Agenter</span>
        {hasStarted && doneCount > 0 && (
          <span className="pipeline-count">
            {doneCount} / {agents.length}
          </span>
        )}
      </div>

      {hasStarted && doneCount > 0 && (
        <div className="pipeline-progress">
          <div
            className="pipeline-progress-fill"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      )}

      <div className="pipeline-agents">
        {agents.map((agent, i) => {
          const state = states[agent];
          const status: AgentStatus = state?.status ?? "idle";

          return (
            <div key={agent} className={`agent-card agent-${status}`}>
              <div className="agent-left">
                <span className="agent-icon">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div className="agent-name">{agent}</div>
              </div>
              <div className="agent-status">
                {status === "running" && <span className="pulse" />}
                {status === "done" && <span className="checkmark">✓</span>}
                {status === "question" && (
                  <span
                    className="pulse"
                    style={{ background: "var(--accent2)" }}
                  />
                )}
                {status === "warning" && (
                  <span
                    className="pulse"
                    style={{ background: "var(--running)" }}
                  />
                )}
                {status === "error" && <span className="error-mark">!</span>}
                {status === "idle" && <span className="idle-dot" />}
              </div>
              {i < agents.length - 1 && (
                <div
                  className={`connector ${
                    status === "done" ? "connector-done" : ""
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
