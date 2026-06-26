import { handleMessage } from "./handler";

const TELEGRAM_API = `https://api.telegram.org/bot${process.env.TELEGRAM_TOKEN}`;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID!;
const PORT = parseInt(process.env.AGENT_PORT ?? "3000");

async function sendReply(text: string): Promise<void> {
  await fetch(`${TELEGRAM_API}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: CHAT_ID, text }),
  });
}

Bun.serve({
  port: PORT,
  async fetch(req) {
    if (req.method !== "POST") return new Response("ok");

    let update: any;
    try {
      update = await req.json();
    } catch {
      return new Response("bad request", { status: 400 });
    }

    const text = update?.message?.text;
    if (!text) return new Response("ok");

    // handle async — respond to Telegram immediately
    (async () => {
      try {
        const reply = await handleMessage(text);
        await sendReply(reply);
      } catch (err) {
        console.error("Handler error:", err);
        await sendReply("Something went wrong. Check logs.");
      }
    })();

    return new Response("ok");
  },
});

console.log(`Agent webhook listening on port ${PORT}`);
