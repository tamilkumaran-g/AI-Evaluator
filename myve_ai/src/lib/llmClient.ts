// src/lib/llmClient.ts
import { auth } from "../firebase";

export type LlmChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type SendWorkspaceMessageExtra = {
  structure?: {
    problem?: string;
    user?: string;
    solution?: string;
    whyNow?: string;
  };
  sessionData?: unknown;
  progress?: number;
};

type SendWorkspaceMessageResult = {
  reply: string;
  updatedStructure?: {
    problem?: string;
    user?: string;
    solution?: string;
    whyNow?: string;
  };
  newProgress?: number;
};

/**
 * Thin client-side wrapper to talk to Gemini directly from the browser.
 *
 * IMPORTANT:
 * - This is ONLY for local / dev testing.
 * - Your API key is exposed in the frontend build.
 * - Do NOT ship this to production.
 *
 * You must set VITE_GEMINI_API_KEY in your `.env.local` or `.env`:
 *
 *   VITE_GEMINI_API_KEY=your_dev_key_here
 */
export async function sendWorkspaceMessage(
  sessionId: string | null,
  messages: LlmChatMessage[],
  extra?: SendWorkspaceMessageExtra
): Promise<SendWorkspaceMessageResult> {
  const user = auth.currentUser;
  if (!user) {
    throw new Error("No authenticated user for LLM call.");
  }

  const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error(
      "VITE_GEMINI_API_KEY is not set. Add it to your .env.local for dev testing."
    );
  }

  // Map our chat messages to Gemini "contents" format
  const contents = messages.map((m) => ({
    role: m.role === "user" ? "user" : "model",
    parts: [{ text: m.content }],
  }));

  // You can tune this prompt later for your framework scoring logic
  const systemPrompt =
    "You are Myve, an AI founder intelligence copilot. " +
    "You help early-stage founders clarify their idea, problem, ICP, solution, and why-now. " +
    "Respond concisely, ask one focused follow-up question at a time, and keep the tone friendly but direct.";

  const body = {
    contents: [
      {
        role: "user",
        parts: [{ text: systemPrompt }],
      },
      ...contents,
    ],
  };

  const endpoint =
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" +
    apiKey;

  const res = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    console.error("Gemini API error:", res.status, text);
    throw new Error("Gemini API returned non-OK response");
  }

  const data = await res.json();

  // Safely extract the first text candidate
  const replyText =
    data?.candidates?.[0]?.content?.parts?.[0]?.text ||
    "I'm here to help you explore your idea. Tell me more about who you're building this for.";

  // For now, we are not doing structured extraction on the frontend.
  // Workspace will still work: it only *optionally* uses updatedStructure and newProgress.
  return {
    reply: replyText,
    updatedStructure: extra?.structure, // you can remove this or keep as-is for now
    newProgress:
      typeof extra?.progress === "number"
        ? Math.min(100, extra.progress + 10)
        : undefined,
  };
}