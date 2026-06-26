import { AgentSession, ADAPTERS, FileSessionStore, SessionManager } from "@qlairoslabs/acp-client";
import { readLastAlert, readAgentState, writeAgentState } from "./state";

const sessions = new SessionManager(new FileSessionStore());

export async function handleMessage(userText: string): Promise<string> {
  const lastAlert = readLastAlert();
  const agentState = readAgentState();

  const isNewSession =
    !agentState || !lastAlert || agentState.alert_id !== lastAlert.alert_id;

  const sessionConfig = {
    adapter: ADAPTERS.claude,
    adapterId: "claude",
    sessions,
    defaultPermission: "approve" as const,
    cwd: process.cwd(),
  };

  if (isNewSession) {
    const context = lastAlert
      ? `Context: @${lastAlert.handle} just posted on X:\n"${lastAlert.text}"\n${lastAlert.post_url}\n\nUser message: ${userText}`
      : userText;

    const session = await AgentSession.create(sessionConfig);
    const result = await session.prompt(context);

    writeAgentState({
      agentSessionId: session.agentSessionId ?? "",
      alert_id: lastAlert?.alert_id ?? "",
    });

    await session.stop();
    return result.text ?? "(no response)";
  } else {
    const session = await AgentSession.create({
      ...sessionConfig,
      agentSessionId: agentState.agentSessionId,
    });

    const result = await session.prompt(userText);
    await session.stop();
    return result.text ?? "(no response)";
  }
}
