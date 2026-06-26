import { join } from "path";

const ROOT = join(import.meta.dir, "..", "..");
const LAST_ALERT_FILE = join(ROOT, "last_alert.json");
const AGENT_STATE_FILE = join(import.meta.dir, "..", "agent_state.json");

export interface LastAlert {
  alert_id: string;
  handle: string;
  text: string;
  post_url: string;
  sent_at: string;
}

export interface AgentState {
  agentSessionId: string;
  alert_id: string;
}

export function readLastAlert(): LastAlert | null {
  try {
    return JSON.parse(Bun.file(LAST_ALERT_FILE).toString());
  } catch {
    return null;
  }
}

export function readAgentState(): AgentState | null {
  try {
    return JSON.parse(Bun.file(AGENT_STATE_FILE).toString());
  } catch {
    return null;
  }
}

export function writeAgentState(state: AgentState): void {
  Bun.write(AGENT_STATE_FILE, JSON.stringify(state, null, 2));
}
