export type AgentStatus = "idle" | "running" | "done" | "question" | "warning" | "error";

export interface AgentState {
  status: AgentStatus;
  content?: string;
}

export type AgentStates = Record<string, AgentState>;

export interface ResearchResult {
  title: string;
  url: string;
}

export interface ResearchSource {
  query: string;
  results: ResearchResult[];
}
