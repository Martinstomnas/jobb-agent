import { useState } from "react";
import InputForm from "./components/InputForm";
import AgentPipeline from "./components/AgentPipeline";
import Output from "./components/Output";
import FollowUpQuestion from "./components/FollowUpQuestion";
import "./App.css";

import * as mockData from "./dev/mockData.js";

// Sett til true for å vise dummy-data uten å kjøre backend
const DEV = true;

const AGENTS = [
  "Kravleser",
  "Research",
  "Match",
  "GapDetector",
  "Writer",
  "InterviewPrep",
];

export default function App() {
  const [agentStates, setAgentStates] = useState({});
  const [output, setOutput] = useState(DEV ? mockData.mockOutput : null);
  const [vinklingOutput, setVinklingOutput] = useState(
    DEV ? mockData.mockMatchOutput : null,
  );
  const [running, setRunning] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState(null);
  const [researchSources, setResearchSources] = useState(null);
  const [interviewPrep, setInterviewPrep] = useState(
    DEV ? mockData.mockInterviewPrep : null,
  );

  const handleSubmit = async ({ jobPosting, cv }) => {
    setRunning(true);
    setAgentStates({});
    setPendingQuestion(null);

    const res = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_posting: jobPosting, cv }),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        const raw = line.slice(5).trim();
        if (!raw) continue;

        try {
          const msg = JSON.parse(raw);

          if (msg.agent === "FERDIG") {
            setRunning(false);
            continue;
          }

          if (msg.agent === "GapDetector" && msg.status === "question") {
            setPendingQuestion({
              question: msg.content,
              sessionId: msg.session_id,
              key: Date.now(),
            });
            setAgentStates((prev) => ({
              ...prev,
              GapDetector: { status: "question", content: msg.content },
            }));
            continue;
          }

          if (msg.agent === "GapDetector" && msg.status === "answered") {
            setPendingQuestion(null);
            setAgentStates((prev) => ({
              ...prev,
              GapDetector: {
                status: "done",
                content: msg.content || "Hoppet over",
              },
            }));
            continue;
          }

          setAgentStates((prev) => ({
            ...prev,
            [msg.agent]: { status: msg.status, content: msg.content },
          }));

          if (
            msg.agent === "Research" &&
            msg.status === "done" &&
            msg.sources
          ) {
            setResearchSources(msg.sources);
          }
          if (msg.agent === "Match" && msg.status === "done") {
            setVinklingOutput(msg.content);
          }
          if (msg.agent === "Writer" && msg.status === "done") {
            setOutput(msg.content);
          }
          if (msg.agent === "InterviewPrep" && msg.status === "done") {
            setInterviewPrep(msg.content);
          }
        } catch {
          // ufullstendig chunk, ignorer
        }
      }
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-tag">multi-agent system</div>
        <h1>
          Jobbsøker<span className="accent">.</span>
        </h1>
        <p className="subtitle">Lim inn annonse og CV – agentene gjør resten</p>
      </header>

      <main className="app-main">
        <div className="left-col">
          <InputForm onSubmit={handleSubmit} running={running} />
          {pendingQuestion && (
            <FollowUpQuestion
              key={pendingQuestion.key}
              question={pendingQuestion.question}
              sessionId={pendingQuestion.sessionId}
            />
          )}
        </div>
        <div className="right-col">
          <AgentPipeline
            agents={AGENTS}
            states={agentStates}
            running={running}
          />
        </div>
        <div className="output-row">
          <Output
            content={output}
            running={running}
            vinklingOutput={vinklingOutput}
            sources={researchSources}
            interviewPrep={interviewPrep}
          />
        </div>
      </main>
    </div>
  );
}
