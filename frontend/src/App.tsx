import { useState } from "react";
import InputForm from "./components/InputForm";
import AgentPipeline from "./components/AgentPipeline";
import Output from "./components/Output";
import FollowUpQuestion from "./components/FollowUpQuestion";
import FitWarning from "./components/FitWarning";
import "./App.css";

import type { AgentStates, ResearchSource } from "./types";
import { API_URL } from "./config";

const AGENTS = [
  "Kravleser",
  "Research",
  "Match",
  "GapDetector",
  "Writer",
  "InterviewPrep",
  "Validator",
];

interface PendingQuestion {
  question: string;
  sessionId: string;
  key: number;
}

interface FitWarningState {
  summary: string;
  sessionId: string;
  key: number;
}

export default function App() {
  const [agentStates, setAgentStates] = useState<AgentStates>({});
  const [output, setOutput] = useState<string | null>(null);
  const [vinklingOutput, setVinklingOutput] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState<PendingQuestion | null>(null);
  const [fitWarning, setFitWarning] = useState<FitWarningState | null>(null);
  const [researchSources, setResearchSources] = useState<ResearchSource[] | null>(null);
  const [interviewPrep, setInterviewPrep] = useState<string | null>(null);
  const [validation, setValidation] = useState<string | null>(null);
  const [agentLog, setAgentLog] = useState<Record<string, string>>({});
  const [pipelineError, setPipelineError] = useState<string | null>(null);

  // Nav status helpers
  const runningAgent = AGENTS.find((a) => agentStates[a]?.status === "running");
  const doneCount = AGENTS.filter((a) => agentStates[a]?.status === "done").length;
  const isDone = !running && output !== null;

  const handleSubmit = async ({
    jobPosting,
    cv,
  }: {
    jobPosting: string;
    cv: string;
  }) => {
    setRunning(true);
    setAgentStates({});
    setPendingQuestion(null);
    setFitWarning(null);
    setPipelineError(null);
    setValidation(null);
    setAgentLog({});
    setOutput(null);
    setVinklingOutput(null);
    setResearchSources(null);
    setInterviewPrep(null);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const processEvent = (msg: Record<string, any>) => {
      if (msg.agent === "FERDIG") { setRunning(false); return; }

      if (msg.agent === "Match" && msg.status === "warning") {
        setFitWarning({ summary: msg.content, sessionId: msg.session_id, key: Date.now() });
        setAgentStates((prev) => ({ ...prev, Match: { status: "warning", content: msg.content } }));
        return;
      }
      if (msg.agent === "GapDetector" || msg.agent === "Writer") setFitWarning(null);

      if (msg.agent === "GapDetector" && msg.status === "question") {
        setPendingQuestion({ question: msg.content, sessionId: msg.session_id, key: Date.now() });
        setAgentStates((prev) => ({ ...prev, GapDetector: { status: "question", content: msg.content } }));
        return;
      }
      if (msg.agent === "GapDetector" && msg.status === "answered") {
        setPendingQuestion(null);
        setAgentStates((prev) => ({ ...prev, GapDetector: { status: "done", content: msg.content || "Hoppet over" } }));
        return;
      }

      setAgentStates((prev) => ({ ...prev, [msg.agent]: { status: msg.status, content: msg.content } }));

      if (msg.agent === "Research" && msg.status === "done" && msg.sources) setResearchSources(msg.sources);
      if (msg.agent === "Match" && msg.status === "done") setVinklingOutput(msg.content);
      if (msg.agent === "Writer" && msg.status === "done") setOutput(msg.content);
      if (msg.agent === "InterviewPrep" && msg.status === "done") setInterviewPrep(msg.content);
      if (msg.agent === "Kravleser" && msg.status === "done") setAgentLog((prev) => ({ ...prev, Kravleser: msg.content }));
      if (msg.agent === "Research" && msg.status === "done") setAgentLog((prev) => ({ ...prev, Research: msg.content }));
      if (msg.agent === "Match" && msg.status === "done" && msg.full_match) setAgentLog((prev) => ({ ...prev, Match: msg.full_match }));
      if (msg.agent === "Validator" && msg.status === "done") setValidation(msg.content);
    };

    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_posting: jobPosting, cv }),
      });

      if (!res.ok) {
        throw new Error(`Server svarte med ${res.status}`);
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop()!;

        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const raw = line.slice(5).trim();
          if (!raw) continue;
          try {
            processEvent(JSON.parse(raw));
          } catch {
            // ufullstendig chunk, ignorer
          }
        }
      }
    } catch (e) {
      setRunning(false);
      setPipelineError(e instanceof Error ? e.message : "Noe gikk galt");
    }
  };

  return (
    <div className="app">
      {/* ── Dark nav ── */}
      <nav className="app-nav">
        <span className="nav-brand">
          Jobbsøker<span className="accent">.</span>
        </span>
        <div className="nav-right">
          <div className="nav-status">
            {running && runningAgent ? (
              <>
                <span className="nav-dot nav-dot--running" />
                <span className="nav-status-text">
                  kjører · {runningAgent.toLowerCase()}
                </span>
              </>
            ) : isDone ? (
              <>
                <span className="nav-dot nav-dot--done" />
                <span className="nav-status-text">
                  ferdig · {doneCount}/{AGENTS.length}
                </span>
              </>
            ) : (
              <span className="nav-status-text">multi-agent system</span>
            )}
          </div>
        </div>
      </nav>

      {/* ── Main content ── */}
      <div className="app-content">
        <main className="app-main">
          <div className="left-col">
            <InputForm onSubmit={handleSubmit} running={running} />
            {pipelineError && (
              <div className="pipeline-error">
                <span className="pipeline-error-label">Feil</span>
                <p>{pipelineError}</p>
              </div>
            )}
            {fitWarning && (
              <FitWarning
                key={fitWarning.key}
                summary={fitWarning.summary}
                sessionId={fitWarning.sessionId}
              />
            )}
            {pendingQuestion && (
              <FollowUpQuestion
                key={pendingQuestion.key}
                question={pendingQuestion.question}
                sessionId={pendingQuestion.sessionId}
              />
            )}
          </div>
          <div className="right-col">
            <AgentPipeline agents={AGENTS} states={agentStates} />
          </div>
          <div className="output-row">
            <Output
              content={output}
              running={running}
              vinklingOutput={vinklingOutput}
              sources={researchSources}
              interviewPrep={interviewPrep}
              validation={validation}
              agentLog={agentLog}
            />
          </div>
        </main>
      </div>
    </div>
  );
}
