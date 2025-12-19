import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  MessageSquare,
  TrendingUp,
  FileText,
  Users,
  Target,
  Zap,
} from "lucide-react";
import { onAuthStateChanged, signOut, type User } from "firebase/auth";
import { auth } from "../firebase";
import myveLogo from "../assets/myvelogo.png";
import { loginWithGoogle } from "../lib/authClient";

const Landing: React.FC = () => {
  const navigate = useNavigate();

  const [currentUser, setCurrentUser] = useState<User | null>(auth.currentUser);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setCurrentUser(user);
      // Close profile menu whenever auth state changes
      setIsProfileMenuOpen(false);
    });

    return unsubscribe;
  }, []);

  async function handleStartWithIdea() {
    try {
      // If already logged in, skip the Google popup
      if (currentUser) {
        navigate("/onboarding");
        return;
      }

      const { idToken, uid, email, displayName } = await loginWithGoogle();

      console.log("Logged in as:", { uid, email, displayName });
      console.log("Firebase ID token:", idToken);

      navigate("/onboarding");
    } catch (err) {
      console.error("Google login failed", err);
    }
  }

  async function handleSignOut() {
    try {
      await signOut(auth);
      setCurrentUser(null);
      navigate("/");
    } catch (err) {
      console.error("Sign out failed", err);
    }
  }

  return (
    <div className="min-h-screen bg-[#f5f7fb] text-slate-900">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center px-6">
          <div className="flex items-center">
            <img
              src={myveLogo}
              alt="Myve Logo"
              className="h-10 w-auto object-contain"
            />
          </div>

          <div className="ml-auto hidden items-center gap-6 text-sm text-slate-600 md:flex">
            {/* Workspace & Journey visible only when signed in */}
            {currentUser && (
              <>
                <button
                  onClick={() => navigate("/workspace")}
                  className="rounded-full bg-white px-4 py-2 text-sm font-medium text-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition"
                >
                  Workspace
                </button>
                <button
                  onClick={() => navigate("/journey")}
                  className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Journey
                </button>
              </>
            )}

            <a href="#how-it-works" className="hover:text-slate-900">
              How it works
            </a>
            <a href="#for-founders" className="hover:text-slate-900">
              For founders
            </a>
            <a href="#pricing" className="hover:text-slate-900">
              Pricing
            </a>

            {!currentUser && (
              <button
                className="text-sm text-slate-700 hover:text-slate-900"
                onClick={handleStartWithIdea}
              >
                Log in
              </button>
            )}

            <button
              onClick={handleStartWithIdea}
              className="rounded-full bg-[#1b9cc8] px-4 py-2 text-sm font-medium text-white hover:bg-[#1787ad]"
            >
              Start with your idea
              <ArrowRight className="ml-2 inline-block h-4 w-4 align-middle" />
            </button>

            {/* Simple profile chip + dropdown when signed in */}
            {currentUser && (
              <div className="relative">
                <button
                  onClick={() => setIsProfileMenuOpen((prev) => !prev)}
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 text-xs font-semibold text-slate-700"
                >
                  {currentUser.displayName
                    ? currentUser.displayName.charAt(0).toUpperCase()
                    : currentUser.email
                    ? currentUser.email.charAt(0).toUpperCase()
                    : "U"}
                </button>
                {isProfileMenuOpen && (
                  <div className="absolute right-0 mt-2 w-44 rounded-xl border border-slate-200 bg-white p-2 text-xs shadow-lg">
                    <div className="mb-2 border-b border-slate-100 pb-2 text-[11px] text-slate-600">
                      {currentUser.displayName || currentUser.email}
                    </div>
                    <button
                      onClick={() => navigate("/workspace")}
                      className="block w-full rounded-md px-2 py-1 text-left hover:bg-slate-50"
                    >
                      Open workspace
                    </button>
                    <button
                      onClick={() => navigate("/journey")}
                      className="mt-1 block w-full rounded-md px-2 py-1 text-left hover:bg-slate-50"
                    >
                      View journey
                    </button>
                    <button
                      onClick={handleSignOut}
                      className="mt-1 block w-full rounded-md px-2 py-1 text-left text-red-600 hover:bg-red-50"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-6xl px-6 pb-24 pt-12">
        {/* HERO SECTION */}
        <section className="grid gap-10 md:grid-cols-[minmax(0,1.1fr),minmax(0,1fr)] md:items-center">
          {/* Left side */}
          <div>
            <div className="inline-flex items-center rounded-full bg-[#e9f4ff] px-3 py-1 text-[11px] font-medium text-[#0276b4]">
              AI sales manual for zero-data founders
            </div>

            <h1 className="mt-6 text-3xl font-bold leading-tight tracking-tight text-slate-900 sm:text-4xl md:text-5xl">
              Turn your idea into a pilot‑ready system to win customers and seed funding
            </h1>

            <p className="mt-4 max-w-xl text-sm leading-relaxed text-slate-600">
              Myve turns a conversation about your idea into a complete, personalised sales manual – ICP, positioning, outreach scripts and a simple pipeline – even if you have zero data or CRM. It is built to help you land your first 10 customers and move faster towards seed.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-4">
              <button
                onClick={handleStartWithIdea}
                className="rounded-full bg-[#1b9cc8] px-5 py-3 text-sm font-medium text-white shadow-sm hover:bg-[#1787ad]"
              >
                Start Myve Session
                <ArrowRight className="ml-2 inline-block h-4 w-4 align-middle" />
              </button>
              <button className="rounded-full border border-slate-300 bg-white px-5 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50">
                See sample report
              </button>
            </div>
          </div>

          {/* Right side: conversation card */}
          <div className="flex justify-end">
            <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white shadow-sm">
              <div className="flex items-center gap-2 border-b border-slate-200 px-5 py-3 text-sm font-semibold text-slate-800">
                <MessageSquare className="h-4 w-4 text-[#0276b4]" />
                <span>Myve conversation</span>
              </div>
              <div className="space-y-3 px-5 py-4 text-[13px]">
                <div className="flex justify-end">
                  <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-[#e8f4ff] px-3 py-2 text-right text-slate-800">
                    I want to build a tool that helps founders structure their
                    ideas and create their first sales system
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="max-w-[85%] rounded-2xl rounded-bl-sm bg-[#f5f7fb] px-3 py-2 text-slate-800">
                    Great! Let&apos;s structure this. Who specifically are you
                    building this for? First-time founders, repeat
                    entrepreneurs, or a specific niche?
                  </div>
                </div>
              </div>
              <div className="grid gap-3 border-t border-slate-200 px-5 py-4 text-[13px] md:grid-cols-2">
                <div className="rounded-2xl bg-[#edf9f2] px-3 py-3">
                  <div className="text-2xl font-semibold text-[#16a34a]">
                    81
                  </div>
                  <div className="mt-1 text-xs font-medium text-slate-700">
                    Validation Score
                  </div>
                </div>
                <div className="rounded-2xl bg-[#fff4eb] px-3 py-3">
                  <div className="text-xs font-medium text-slate-700">
                    Sales System
                  </div>
                  <div className="mt-1 text-xs text-slate-500">
                    Ready to build
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section
          id="how-it-works"
          className="mt-20 border-t border-slate-200 pt-12"
        >
          <h2 className="text-center text-2xl font-semibold text-slate-900">
            How it works
          </h2>
          <p className="mt-2 text-center text-sm text-slate-600">
            Four simple steps to transform your idea into a structured,
            validated business
          </p>

          <div className="mt-10 grid gap-6 md:grid-cols-4">
            {[
              {
                icon: MessageSquare,
                title: "Talk through your idea",
                desc: "Answer focused questions in a Myve chat – like talking to an experienced sales mentor.",
              },
              {
                icon: TrendingUp,
                title: "Myve builds your sales manual",
                desc: "Behind the scenes, AI turns your answers into ICP, positioning, channels and scripts.",
              },
              {
                icon: Target,
                title: "Reach your first 10 customers",
                desc: "Use ready-to-send LinkedIn, WhatsApp or email messages to book your first pilot calls.",
              },
              {
                icon: FileText,
                title: "Record and learn from your journey",
                desc: "Keep a living log of experiments, wins and updates you can later share with investors.",
              },
            ].map((step, i) => (
              <div
                key={step.title}
                className="rounded-3xl border border-slate-200 bg-white px-5 py-8 text-center shadow-sm"
              >
                <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-[#e9f4ff] text-slate-700">
                  <step.icon className="h-5 w-5" />
                </div>
                <div className="text-sm font-semibold text-slate-900">
                  {step.title}
                </div>
                <p className="mt-2 text-xs text-slate-600">{step.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* WHO IT'S FOR */}
        <section id="for-founders" className="mt-20">
          <h2 className="text-center text-2xl font-semibold text-slate-900">
            Built for founders at every stage
          </h2>

          <div className="mx-auto mt-10 grid max-w-5xl gap-6 md:grid-cols-3">
            {[
              {
                icon: Zap,
                title: "Solo founders",
                desc: "Pre-revenue, idea-stage builders who need a clear path from idea to first 10 paying customers.",
              },
              {
                icon: Users,
                title: "Cohort startups",
                desc: "Accelerator and community founders who want a consistent AI-generated sales manual to share with mentors.",
              },
              {
                icon: FileText,
                title: "Investors & mentors",
                desc: "Partners who prefer a clean Myve report and journey log instead of scattered docs when they review startups.",
              },
            ].map((audience) => (
              <div
                key={audience.title}
                className="rounded-3xl border border-slate-200 bg-white px-5 py-8 shadow-sm"
              >
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-[#fff4eb]">
                  <audience.icon className="h-5 w-5 text-[#f97316]" />
                </div>
                <div className="text-base font-semibold text-slate-900">
                  {audience.title}
                </div>
                <p className="mt-2 text-sm text-slate-600">{audience.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA / PRICING PREVIEW */}
        <section
          id="pricing"
          className="mt-20 rounded-3xl bg-gradient-to-br from-[#e0f4ff] via-[#f1f5ff] to-[#e4f5ff] px-6 py-12 text-center"
        >
          <div className="mx-auto max-w-2xl space-y-6">
            <h2 className="text-2xl font-semibold text-slate-900 md:text-3xl">
              Early access for first believers
            </h2>
            <p className="text-sm text-slate-600 md:text-base">
              Join the waitlist and get an AI-generated sales manual for your current idea. Early access pricing is designed for pre-revenue founders – roughly the cost of a couple of coffees for a complete playbook.
            </p>
            <button
              onClick={handleStartWithIdea}
              className="rounded-full bg-[#1b9cc8] px-6 py-3 text-sm font-medium text-white hover:bg-[#1787ad]"
            >
              Join early access
              <ArrowRight className="ml-2 inline-block h-4 w-4 align-middle" />
            </button>
            <p className="text-xs text-slate-500">
              Built for idea-stage, pre-CRM founders
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-slate-200 py-8">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-sm text-slate-500 md:flex-row">
          <div className="flex items-center gap-2">
            <img
              src={myveLogo}
              alt="Myve Logo"
              className="h-10 w-auto object-contain"
            />
          </div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-slate-800">
              Privacy
            </a>
            <a href="#" className="hover:text-slate-800">
              Terms
            </a>
            <a href="#" className="hover:text-slate-800">
              Contact
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
