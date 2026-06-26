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

export async function readLastAlert(): Promise<LastAlert | null> {
  try {
    const text = await Bun.file(LAST_ALERT_FILE).text();
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export async function readAgentState(): Promise<AgentState | null> {
  try {
    const text = await Bun.file(AGENT_STATE_FILE).text();
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export async function writeAgentState(state: AgentState): Promise<void> {
  await Bun.write(AGENT_STATE_FILE, JSON.stringify(state, null, 2));
}
