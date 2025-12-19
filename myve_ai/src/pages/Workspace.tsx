import { useEffect, useState } from "react";
import LayoutShell from "../components/LayoutShell";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Textarea } from "../components/ui/textarea";
import { Progress } from "../components/ui/progress";
import { Send, FileText, TrendingUp, Target, User, MessageSquare } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { auth } from "../firebase";
import { getFirestore, doc, getDoc } from "firebase/firestore";
import { sendWorkspaceMessage } from "../lib/llmClient";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type SessionData = {
  name?: string;
  projectName?: string;
  ideaTitle?: string;
  ideaDescription?: string;
  problem?: string;
  targetUser?: string;
  whyNow?: string;
  pitchUrl?: string;
};

const Workspace = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Let's start by understanding who you're building this for. In one sentence, who is your target user or customer?",
    },
  ]);

  const [structure, setStructure] = useState({
    problem: "",
    user: "",
    solution: "",
    whyNow: "",
  });

  const [progress, setProgress] = useState(25);
  const [isThinking, setIsThinking] = useState(false);

  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [isLoadingSession, setIsLoadingSession] = useState<boolean>(true);
  const [sessionError, setSessionError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSession() {
      setIsLoadingSession(true);
      setSessionError(null);

      try {
        const params = new URLSearchParams(location.search);
        const sessionId = params.get("sessionId");

        const user = auth.currentUser;
        if (!user || !sessionId) {
          setIsLoadingSession(false);
          return;
        }

        const db = getFirestore();
        const ref = doc(db, "users", user.uid, "sessions", sessionId);
        const snap = await getDoc(ref);

        if (!snap.exists()) {
          setSessionError("We couldn't find this session in your workspace.");
        } else {
          const data = snap.data() as SessionData;
          setSessionData(data);

          // Pre-fill structure panel with any existing onboarding fields
          setStructure((prev) => ({
            ...prev,
            problem: data.problem || prev.problem,
            user: data.targetUser || prev.user,
            whyNow: data.whyNow || prev.whyNow,
          }));
        }
      } catch (err) {
        console.error("Failed to load session from Firestore", err);
        setSessionError("There was an issue loading this session.");
      } finally {
        setIsLoadingSession(false);
      }
    }

    loadSession();
  }, [location.search]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input.trim() };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setIsThinking(true);

    try {
      // Derive sessionId from the current URL
      const params = new URLSearchParams(location.search);
      const sessionId = params.get("sessionId");

      // Call the LLM wrapper – this will talk to your backend/Gemini later
      const result = await sendWorkspaceMessage(sessionId, updatedMessages, {
        structure,
        sessionData,
        progress,
      });

      const reply =
        result?.reply ||
        "That's helpful context. Tell me more about that.";

      if (result?.updatedStructure) {
        setStructure((prev) => ({
          ...prev,
          ...result.updatedStructure,
        }));
      }

      const newProgress =
        typeof result?.newProgress === "number"
          ? result.newProgress
          : Math.min(100, progress + 20);

      setMessages([...updatedMessages, { role: "assistant", content: reply }]);
      setProgress(newProgress);
    } catch (err) {
      console.error("LLM call failed, using fallback conversation logic.", err);

      // Fallback: keep your previous scripted flow so chat still works without backend
      let response = "";
      let newProgress = progress;

      if (messages.length === 1) {
        response =
          "Great! Now, what's the core problem these users face that your solution addresses?";
        setStructure((prev) => ({ ...prev, user: input.trim() }));
        newProgress = 40;
      } else if (messages.length === 3) {
        response =
          "Perfect. And how does your solution specifically solve this problem? What's the key value it delivers?";
        setStructure((prev) => ({ ...prev, problem: input.trim() }));
        newProgress = 60;
      } else if (messages.length === 5) {
        response =
          "Excellent. One more question - why is now the right time for this solution? What's changed in the market or technology?";
        setStructure((prev) => ({ ...prev, solution: input.trim() }));
        newProgress = 80;
      } else if (messages.length === 7) {
        response =
          "I've collected enough insight to generate your validation report and sales system. Ready to see what we've built?";
        setStructure((prev) => ({ ...prev, whyNow: input.trim() }));
        newProgress = 100;
      } else {
        response = "That's helpful context. Tell me more about that.";
      }

      setMessages([
        ...updatedMessages,
        { role: "assistant", content: response },
      ]);
      setProgress(newProgress);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <LayoutShell
      title="Myve session"
      rightActions={
        <div className="text-xs text-slate-500">
          Structured founder conversation
        </div>
      }
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:gap-6">
        {/* Left Sidebar */}
        <div className="order-2 mt-4 flex w-full flex-col rounded-3xl border border-slate-200 bg-white shadow-sm lg:order-1 lg:mt-0 lg:w-64">
          <div className="border-b border-slate-200 p-4">
            <div className="flex items-center gap-2">
              <div>
                <h1 className="text-sm font-semibold text-slate-900">Myve</h1>
                <p className="text-[11px] text-slate-500">Session navigation</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 space-y-2 p-4">
            <button className="flex w-full items-center gap-3 rounded-lg bg-[#e8f4ff] px-3 py-2 text-sm font-medium text-[#1b9cc8]">
              <MessageSquare className="h-4 w-4" />
              <span className="text-sm">Myve Session</span>
            </button>
            <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-500 transition-colors hover:bg-slate-100">
              <FileText className="h-4 w-4" />
              <span className="text-sm">Idea Canvas</span>
            </button>
            <button
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-500 transition-colors hover:bg-slate-100"
              onClick={() => navigate("/validation")}
            >
              <TrendingUp className="h-4 w-4" />
              <span className="text-sm">Validation Report</span>
            </button>
            <button
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-500 transition-colors hover:bg-slate-100"
              onClick={() => navigate("/playbook")}
            >
              <Target className="h-4 w-4" />
              <span className="text-sm">Sales Playbook</span>
            </button>
            <button
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-500 transition-colors hover:bg-slate-100"
              onClick={() => navigate("/journey")}
            >
              <User className="h-4 w-4" />
              <span className="text-sm">Founder Profile</span>
            </button>
          </nav>

          <div className="border-t border-slate-200 p-4">
            <p className="text-xs text-slate-500">
              Session:{" "}
              {sessionData?.ideaTitle ||
                sessionData?.projectName ||
                "Myve idea session"}
            </p>
          </div>
        </div>

        {/* Center: Chat */}
        <div className="order-1 flex min-h-[60vh] flex-1 flex-col rounded-3xl border border-slate-200 bg-white shadow-sm lg:order-2">
          <div className="border-b border-slate-200 p-6">
            <h2 className="text-xl font-semibold text-slate-900">
              {(sessionData?.projectName ||
                sessionData?.ideaTitle ||
                "Myve session") + " – Myve Conversation"}
            </h2>
            <p className="text-sm text-slate-500">
              Structured in real time as you answer
            </p>
            {isLoadingSession && (
              <p className="mt-1 text-xs text-slate-400">
                Loading your session from workspace…
              </p>
            )}
            {sessionError && (
              <p className="mt-1 text-xs text-red-500">{sessionError}</p>
            )}
          </div>

          <div className="flex-1 min-h-0 space-y-4 overflow-y-auto p-6">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-[#e8f4ff] rounded-tr-sm"
                      : "bg-slate-100 rounded-tl-sm"
                  }`}
                >
                  <p className="text-sm text-slate-900">{msg.content}</p>
                </div>
              </div>
            ))}

            {isThinking && (
              <div className="flex justify-start">
                <div className="max-w-[70%] rounded-2xl rounded-tl-sm bg-slate-100 px-4 py-3">
                  <p className="text-sm text-slate-500">Myve is thinking…</p>
                </div>
              </div>
            )}

            {progress === 100 && (
              <div className="flex justify-center pt-4">
                <Card className="w-full max-w-md space-y-3 rounded-2xl border border-slate-200 bg-[#f6f9ff] p-4 text-center">
                  <p className="text-sm text-slate-900">
                    Ready to see your results?
                  </p>
                  <Button
                    onClick={() => navigate("/validation")}
                    className="w-full"
                  >
                    Generate Myve Report
                  </Button>
                </Card>
              </div>
            )}
          </div>

          <div className="rounded-b-3xl border-t border-slate-200 bg-slate-50 p-4 sm:p-6">
            <div className="flex gap-3">
              <Textarea
                placeholder="Type your answer..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                rows={2}
                className="w-full resize-none max-h-32 overflow-y-auto"
              />
              <Button onClick={handleSend} size="icon" className="h-auto">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="order-3 mt-4 flex w-full flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-sm lg:mt-0 lg:w-80 lg:gap-6 lg:p-6">
          {sessionData?.ideaDescription && (
            <Card className="space-y-2 rounded-2xl border border-slate-200 bg-white p-4">
              <h3 className="text-sm font-semibold text-slate-900">
                Idea context
              </h3>
              <p className="text-xs text-slate-600">
                {sessionData.ideaDescription}
              </p>
            </Card>
          )}
          <Card className="space-y-3 rounded-2xl border border-slate-200 bg-white p-4">
            <h3 className="text-sm font-semibold text-slate-900">
              Live Structure
            </h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-slate-500">Problem:</span>
                <p className="mt-0.5 text-slate-900">
                  {structure.problem || "—"}
                </p>
              </div>
              <div>
                <span className="text-slate-500">User:</span>
                <p className="mt-0.5 text-slate-900">
                  {structure.user || "—"}
                </p>
              </div>
              <div>
                <span className="text-slate-500">Solution:</span>
                <p className="mt-0.5 text-slate-900">
                  {structure.solution || "—"}
                </p>
              </div>
              <div>
                <span className="text-slate-500">Why now:</span>
                <p className="mt-0.5 text-slate-900">
                  {structure.whyNow || "—"}
                </p>
              </div>
            </div>
          </Card>

          <Card className="space-y-3 rounded-2xl border border-slate-200 bg-white p-4">
            <h3 className="text-sm font-semibold text-slate-900">
              Session Progress
            </h3>
            <Progress value={progress} className="h-2" />
            <div className="space-y-1.5 text-sm">
              <div
                className={
                  progress >= 25 ? "text-slate-900" : "text-slate-500"
                }
              >
                1/4 Idea clarity
              </div>
              <div
                className={
                  progress >= 50 ? "text-slate-900" : "text-slate-500"
                }
              >
                2/4 Market & ICP
              </div>
              <div
                className={
                  progress >= 75 ? "text-slate-900" : "text-slate-500"
                }
              >
                3/4 Sales system
              </div>
              <div
                className={
                  progress >= 100 ? "text-slate-900" : "text-slate-500"
                }
              >
                4/4 Validation & scores
              </div>
            </div>
          </Card>
        </div>
      </div>
    </LayoutShell>
  );
};

export default Workspace;
