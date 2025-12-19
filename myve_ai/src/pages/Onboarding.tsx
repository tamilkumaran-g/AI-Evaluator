import { useEffect, useState } from "react";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { ArrowRight, Shield } from "lucide-react";
import { useNavigate } from "react-router-dom";
import myveLogo from "../assets/myvelogo.png";
import { auth } from "../firebase";

const Onboarding = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    projectName: "",
    stage: "",
    helpWith: [] as string[],
    ideaDescription: "",
    problem: "",
    targetUser: "",
    whyNow: "",
    pitchUrl: ""
  });

  useEffect(() => {
    const user = auth.currentUser;

    if (!user) {
      // No authenticated user – send back to landing
      navigate("/");
      return;
    }

    const fallbackName =
      user.displayName ||
      (user.email ? user.email.split("@")[0] : "") ||
      "";

    setFormData((prev) => ({
      ...prev,
      name: prev.name || fallbackName,
    }));
  }, [navigate]);

  const helpOptions = [
    "Idea clarity",
    "Validation",
    "Sales system",
    "Investor readiness"
  ];

  const handleHelpToggle = (option: string) => {
    setFormData(prev => ({
      ...prev,
      helpWith: prev.helpWith.includes(option)
        ? prev.helpWith.filter(h => h !== option)
        : [...prev.helpWith, option]
    }));
  };

  const handleStartConversation = async () => {
    if (
      !formData.ideaDescription ||
      !formData.problem ||
      !formData.targetUser ||
      !formData.whyNow
    ) {
      return;
    }

    setIsSubmitting(true);

    try {
      const user = auth.currentUser;
      if (!user) {
        console.error("No authenticated user found. Redirecting to landing.");
        navigate("/");
        return;
      }

      const idToken = await user.getIdToken();
      // Only call backend if an API URL is explicitly configured
      const API_URL = import.meta.env.VITE_API_URL;

      const payload = {
        name: formData.name,
        projectName: formData.projectName,
        stage: formData.stage,
        helpWith: formData.helpWith,
        ideaTitle: formData.projectName || "Untitled idea",
        ideaDescription: formData.ideaDescription,
        problem: formData.problem,
        targetUser: formData.targetUser,
        whyNow: formData.whyNow,
        pitchUrl: formData.pitchUrl,
      };

      // Fallback session id for local dev, will be overridden if backend responds
      let sessionId = `local-${Date.now()}`;

      if (API_URL) {
        try {
          const res = await fetch(`${API_URL}/api/onboarding`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${idToken}`,
            },
            body: JSON.stringify(payload),
          });

          if (!res.ok) {
            console.warn("Onboarding submission failed", await res.text());
          } else {
            const data = await res.json();
            if (data.sessionId) {
              sessionId = data.sessionId;
            }
          }
        } catch (err) {
          console.warn(
            "Backend not available yet, using local session only.",
            err
          );
        }
      } else {
        console.warn(
          "VITE_API_URL is not set. Skipping backend call and using local session only."
        );
      }

      // Always go to workspace so you can continue the flow
      navigate(`/workspace?sessionId=${sessionId}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f5f7fb] text-slate-900">
      {/* Header */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center px-6 h-20">
          {/* Logo Left */}
          <div className="flex items-center gap-4">
            <img
              src={myveLogo}
              alt="Myve Logo"
              className="h-14 w-auto object-contain"
            />
            <div className="leading-tight">
              <p className="text-[11px] uppercase tracking-[0.12em] text-slate-500">
                Onboarding
              </p>
              <h1 className="text-[15px] font-semibold text-slate-900">
                Tell Myve about you and your idea
              </h1>
            </div>
          </div>

          {/* Right text */}
          <div className="ml-auto hidden flex-col items-end md:flex">
            {auth.currentUser?.email && (
              <p className="text-[11px] text-slate-500">
                Signed in as {auth.currentUser.email}
              </p>
            )}
            <p className="text-xs text-slate-500">Takes about 3–5 minutes</p>
          </div>
        </div>
      </nav>

      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="mx-auto max-w-5xl">
          {/* Progress */}
          <div className="mb-8 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div
                  className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold ${
                    step === 1 ? "bg-[#1b9cc8] text-white" : "bg-white text-slate-600 border border-slate-200"
                  }`}
                >
                  1
                </div>
                <span className="text-xs font-medium text-slate-700">
                  About you
                </span>
              </div>
              <div className="h-px w-10 bg-slate-200" />
              <div className="flex items-center gap-3">
                <div
                  className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold ${
                    step === 2 ? "bg-[#1b9cc8] text-white" : "bg-white text-slate-600 border border-slate-200"
                  }`}
                >
                  2
                </div>
                <span className="text-xs font-medium text-slate-700">
                  Your idea
                </span>
              </div>
            </div>
            <p className="text-xs text-slate-500">
              Step {step} of 2 &mdash; you can always refine details later in the workspace.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2">
            {/* Left: Form */}
            <div className="space-y-6">
              {step === 1 ? (
                <Card className="space-y-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div>
                    <h2 className="mb-2 text-2xl font-semibold text-slate-900">
                      Tell Myve about you
                    </h2>
                    <p className="text-sm text-slate-500">
                      We’ll grab your details from Google. You can tweak your name and give this idea a working title.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="name">Your name *</Label>
                      <Input
                        id="name"
                        placeholder="Your name"
                        value={formData.name}
                        onChange={(e) =>
                          setFormData(prev => ({ ...prev, name: e.target.value }))
                        }
                        className="mt-1.5"
                      />
                    </div>

                    <div>
                      <Label htmlFor="project">Startup / idea name *</Label>
                      <Input
                        id="project"
                        placeholder="What are you calling this idea?"
                        value={formData.projectName}
                        onChange={(e) =>
                          setFormData(prev => ({ ...prev, projectName: e.target.value }))
                        }
                        className="mt-1.5"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Button
                      className="w-full"
                      disabled={!formData.name || !formData.projectName}
                      onClick={() => setStep(2)}
                    >
                      Next: Share your idea
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                    <p className="text-center text-[11px] text-slate-500">
                      You can always come back and edit these details later.
                    </p>
                  </div>
                </Card>
              ) : (
                <Card className="space-y-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div>
                    <h2 className="mb-2 text-2xl font-semibold text-slate-900">
                      Now, tell Myve what&apos;s in your head
                    </h2>
                    <p className="text-sm text-slate-500">
                      Write freely in your own words. Rough notes are okay &mdash; Myve will help you refine.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="idea">Describe your idea in your own words *</Label>
                      <Textarea
                        id="idea"
                        placeholder="I want to build..."
                        rows={4}
                        value={formData.ideaDescription}
                        onChange={(e) => setFormData(prev => ({ ...prev, ideaDescription: e.target.value }))}
                        className="mt-1.5"
                      />
                    </div>

                    <div>
                      <Label htmlFor="problem">What problem are you solving? *</Label>
                      <Textarea
                        id="problem"
                        placeholder="The problem is..."
                        rows={3}
                        value={formData.problem}
                        onChange={(e) => setFormData(prev => ({ ...prev, problem: e.target.value }))}
                        className="mt-1.5"
                      />
                    </div>

                    <div>
                      <Label htmlFor="user">Who is this for? *</Label>
                      <Textarea
                        id="user"
                        placeholder="This is for..."
                        rows={2}
                        value={formData.targetUser}
                        onChange={(e) => setFormData(prev => ({ ...prev, targetUser: e.target.value }))}
                        className="mt-1.5"
                      />
                    </div>

                    <div>
                      <Label htmlFor="why">Why now? *</Label>
                      <Textarea
                        id="why"
                        placeholder="This matters now because..."
                        rows={2}
                        value={formData.whyNow}
                        onChange={(e) => setFormData(prev => ({ ...prev, whyNow: e.target.value }))}
                        className="mt-1.5"
                      />
                    </div>

                    <div>
                      <Label htmlFor="pitch">Pitch deck / Notion doc URL (optional)</Label>
                      <Input
                        id="pitch"
                        type="url"
                        placeholder="https://..."
                        value={formData.pitchUrl}
                        onChange={(e) => setFormData(prev => ({ ...prev, pitchUrl: e.target.value }))}
                        className="mt-1.5"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex gap-3">
                      <Button
                        variant="outline"
                        onClick={() => setStep(1)}
                        className="flex-1"
                      >
                        Back
                      </Button>
                      <Button
                        className="flex-1"
                        disabled={
                          isSubmitting ||
                          !formData.ideaDescription ||
                          !formData.problem ||
                          !formData.targetUser ||
                          !formData.whyNow
                        }
                        onClick={handleStartConversation}
                      >
                        {isSubmitting ? "Starting..." : "Start Myve Conversation"}
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </div>
                    <p className="text-center text-[11px] text-slate-500">
                      Myve will use this to generate your live chat, validation report, and first sales playbook.
                    </p>
                  </div>
                </Card>
              )}
            </div>

            {/* Right: Info */}
            <div className="space-y-6">
              <Card className="space-y-4 rounded-3xl border border-slate-200 bg-gradient-to-br from-white to-slate-100/60 p-6 shadow-sm">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#1b9cc8]/10 flex items-center justify-center flex-shrink-0">
                    <Shield className="w-5 h-5 text-[#1b9cc8]" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 mb-1">Your data is private</h3>
                    <p className="text-sm text-slate-600">
                      Everything you share with Myve is confidential. We use it only to help structure your thinking and won't share it with anyone.
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="space-y-3 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900">What happens next?</h3>
                <ul className="space-y-2 text-sm text-slate-600">
                  <li className="flex gap-2">
                    <span className="text-[#1b9cc8]">1.</span>
                    <span>Myve will have a conversation with you to understand your idea deeply</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-[#1b9cc8]">2.</span>
                    <span>As you answer, we'll structure your thinking in real-time</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-[#1b9cc8]">3.</span>
                    <span>You'll get a validation report with scores and insights</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-[#1b9cc8]">4.</span>
                    <span>We'll generate your first sales playbook with ICP, offers, and scripts</span>
                  </li>
                </ul>
              </Card>

              {step === 2 && (
                <Card className="border border-slate-200 bg-[#f6f9ff] p-6 rounded-3xl">
                  <p className="text-sm text-slate-900">
                    <span className="font-semibold">Tip:</span> Don't worry about being perfect. Myve will help you refine and structure your thinking through conversation.
                  </p>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
