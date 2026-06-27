import { AgentSession, FileSessionStore, SessionManager } from "@qlairoslabs/acp-client";
import { readLastAlert, readAgentState, writeAgentState } from "./state";

const sessions = new SessionManager(new FileSessionStore());

const CLAUDE_ADAPTER = {
  command: ["claude", "--print"],
  ptyCommand: ["claude"],
};

let activeSession: AgentSession | null = null;
let activeAlertId: string | null = null;

async function getSession(alertId: string): Promise<AgentSession> {
  if (activeSession && activeAlertId === alertId) {
    return activeSession;
  }

  // alert changed or no session — tear down old one and start fresh
  if (activeSession) {
    await activeSession.stop().catch(() => {});
    activeSession = null;
  }

  const session = await AgentSession.create({
    adapter: CLAUDE_ADAPTER,
    adapterId: "claude",
    mode: "degraded",
    sessions,
    defaultPermission: "approve",
    cwd: process.cwd(),
  });

  activeSession = session;
  activeAlertId = alertId;

  await writeAgentState({
    agentSessionId: session.agentSessionId ?? "",
    alert_id: alertId,
  });

  return session;
}

export async function handleMessage(userText: string): Promise<string> {
  const [lastAlert, agentState] = await Promise.all([readLastAlert(), readAgentState()]);

  const alertId = lastAlert?.alert_id ?? "";
  const isNewAlert = alertId !== (agentState?.alert_id ?? "");

  const session = await getSession(alertId);

  let prompt = userText;
  if (isNewAlert && lastAlert) {
    prompt = `Context: @${lastAlert.handle} just posted on X:\n"${lastAlert.text}"\n${lastAlert.post_url}\n\nUser message: ${userText}`;
  }

  const result = await session.prompt(prompt);
  return result.text ?? "(no response)";
}
