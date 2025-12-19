import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import LayoutShell from "../components/LayoutShell";
import { Download, Copy, CheckCircle, Target, Users, MessageSquare, DollarSign } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

const Playbook = () => {
  const navigate = useNavigate();
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const linkedinScript = `Hi [Name],

I came across your profile and saw you're building [their startup]. I'm working on something that might be useful.

I'm creating Myve - a tool that helps first-time founders structure their ideas and build their first sales system. Think of it as having a structured conversation that ends with a validation report + sales playbook.

Would love to get your perspective. Are you open to a 20-min call this week?

Best,
[Your name]`;

  const whatsappScript = `Hey [Name] 👋

Quick question - are you currently trying to figure out how to validate and sell your startup idea?

I'm building Myve (founder intelligence tool) and running validation conversations with founders like you. 

20 mins, completely free, you'll get a validation report + sales playbook out of it.

Interested?`;

  return (
    <LayoutShell
      title="Sales playbook"
      rightActions={
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Download PDF
          </Button>
          <Button variant="outline" size="sm">
            Copy to Notion
          </Button>
        </div>
      }
    >
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="mb-2 text-3xl font-semibold text-slate-900">
            Sales playbook
          </h1>
          <p className="text-sm text-slate-500">
            Your first 100-customer system • Founder Sales AI
          </p>
        </div>

        {/* Offer */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-sky-600" />
            <h2 className="text-xl font-semibold text-slate-900">Core offer</h2>
          </div>
          <Card className="space-y-3 rounded-3xl border border-slate-200 bg-gradient-to-br from-white to-sky-50 p-6 shadow-sm">
            <h3 className="mb-3 text-lg font-semibold text-slate-900">
              Structured founder conversation → Validation report + Sales playbook
            </h3>
            <ul className="space-y-2">
              <li className="flex gap-2 text-sm">
                <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-600" />
                <span className="text-slate-800">
                  Turn scattered ideas into structured, validated business model in one session
                </span>
              </li>
              <li className="flex gap-2 text-sm">
                <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-600" />
                <span className="text-slate-800">
                  Get validation scores and identify your biggest assumptions/risks
                </span>
              </li>
              <li className="flex gap-2 text-sm">
                <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-600" />
                <span className="text-slate-800">
                  Receive your complete sales system: ICP, offers, channels, and ready-to-use scripts
                </span>
              </li>
            </ul>
          </Card>
        </section>

        {/* ICP */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-sky-600" />
            <h2 className="text-xl font-semibold text-slate-900">
              Ideal customer profiles
            </h2>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="space-y-3 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">
                ICP #1: First-time SaaS founders
              </h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-slate-500">Stage:</span>
                  <p className="text-slate-800">
                    Pre-revenue, working on MVP or just launched
                  </p>
                </div>
                <div>
                  <span className="text-slate-500">Location:</span>
                  <p className="text-slate-800">India, remote-first globally</p>
                </div>
                <div>
                  <span className="text-slate-500">Pain:</span>
                  <p className="text-slate-800">
                    No structure, unclear on validation or how to get first customers
                  </p>
                </div>
                <div>
                  <span className="text-slate-500">Where they are:</span>
                  <p className="text-slate-800">
                    LinkedIn, Twitter/X, founder communities, accelerator cohorts
                  </p>
                </div>
              </div>
            </Card>

            <Card className="space-y-3 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">
                ICP #2: Cohort/accelerator founders
              </h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-slate-500">Stage:</span>
                  <p className="text-slate-800">
                    In accelerator program, need to show progress quickly
                  </p>
                </div>
                <div>
                  <span className="text-slate-500">Location:</span>
                  <p className="text-slate-800">India, Southeast Asia, MENA</p>
                </div>
                <div>
                  <span className="text-slate-500">Pain:</span>
                  <p className="text-slate-800">
                    Time pressure, need validation + sales system before demo day
                  </p>
                </div>
                <div>
                  <span className="text-slate-500">Where they are:</span>
                  <p className="text-slate-800">
                    Accelerator Slack channels, WhatsApp groups, pitch events
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </section>

        {/* Channels & Strategy */}
        <section className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-900">
            Channels &amp; strategy
          </h2>
          <div className="grid gap-6 md:grid-cols-2">
            <Card className="space-y-3 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">Primary channels</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-sky-600" />
                  <span className="text-slate-800">
                    LinkedIn DMs to founders posting about their journey
                  </span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-sky-600" />
                  <span className="text-slate-800">
                    Founder communities (GrowthX, LetsVenture, OnDeck)
                  </span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-sky-600" />
                  <span className="text-slate-800">
                    Accelerator cohorts (direct partnerships)
                  </span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-sky-600" />
                  <span className="text-slate-800">WhatsApp founder groups</span>
                </li>
              </ul>
            </Card>

            <Card className="space-y-3 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">Suggested funnel</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-sky-50">
                    <span className="text-xs font-semibold text-sky-600">1</span>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-slate-900">Awareness</p>
                    <p className="text-xs text-slate-500">
                      Find founders sharing their journey
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-sky-50">
                    <span className="text-xs font-semibold text-sky-600">2</span>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-slate-900">Outreach</p>
                    <p className="text-xs text-slate-500">
                      Personalized DM offering value
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-sky-50">
                    <span className="text-xs font-semibold text-sky-600">3</span>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-slate-900">Validation call</p>
                    <p className="text-xs text-slate-500">
                      20-min structured session
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-sky-50">
                    <span className="text-xs font-semibold text-sky-600">4</span>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-slate-900">Deliver + upsell</p>
                    <p className="text-xs text-slate-500">
                      Report + pitch manual service
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </section>

        {/* Outreach Scripts */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-sky-600" />
            <h2 className="text-xl font-semibold text-slate-900">
              Outreach scripts
            </h2>
          </div>
          <Tabs defaultValue="linkedin" className="w-full">
            <TabsList className="grid w-full max-w-md grid-cols-3">
              <TabsTrigger value="linkedin">LinkedIn DM</TabsTrigger>
              <TabsTrigger value="whatsapp">WhatsApp</TabsTrigger>
              <TabsTrigger value="email">Email</TabsTrigger>
            </TabsList>
            <TabsContent value="linkedin" className="space-y-3">
              <Card className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-4 flex items-start justify-between">
                  <h3 className="font-semibold text-slate-900">
                    LinkedIn DM Script
                  </h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(linkedinScript, "linkedin")}
                  >
                    {copied === "linkedin" ? (
                      <>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="mr-2 h-4 w-4" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
                <pre className="whitespace-pre-wrap rounded-lg bg-slate-100 p-4 font-mono text-sm text-slate-800">
                  {linkedinScript}
                </pre>
              </Card>
            </TabsContent>
            <TabsContent value="whatsapp">
              <Card className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-4 flex items-start justify-between">
                  <h3 className="font-semibold text-slate-900">
                    WhatsApp Message Script
                  </h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(whatsappScript, "whatsapp")}
                  >
                    {copied === "whatsapp" ? (
                      <>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="mr-2 h-4 w-4" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
                <pre className="whitespace-pre-wrap rounded-lg bg-slate-100 p-4 font-mono text-sm text-slate-800">
                  {whatsappScript}
                </pre>
              </Card>
            </TabsContent>
            <TabsContent value="email">
              <Card className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <p className="text-sm text-slate-500">
                  Email script coming soon...
                </p>
              </Card>
            </TabsContent>
          </Tabs>
        </section>

        {/* Pricing */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-sky-600" />
            <h2 className="text-xl font-semibold text-slate-900">
              Pricing &amp; tests
            </h2>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="space-y-3 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">
                Suggested starting price
              </h3>
              <div className="space-y-2">
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-slate-900">
                    ₹299
                  </span>
                  <span className="text-slate-500">per session</span>
                </div>
                <p className="text-sm text-slate-500">
                  Low enough for first-time founders, high enough to signal
                  value
                </p>
              </div>
            </Card>

            <Card className="space-y-3 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">
                Pricing experiments
              </h3>
              <ul className="space-y-2 text-sm">
                <li className="flex gap-2">
                  <span className="font-bold text-sky-600">•</span>
                  <span className="text-slate-800">
                    Test ₹299 vs ₹499 for first 20 users (A/B test)
                  </span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold text-sky-600">•</span>
                  <span className="text-slate-800">
                    Bundle: Idea validation + sales playbook for ₹999
                  </span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold text-sky-600">•</span>
                  <span className="text-slate-800">
                    Offer first 10 customers 50% off (₹150) for feedback
                  </span>
                </li>
              </ul>
            </Card>
          </div>
        </section>

        {/* CTA */}
        <Card className="flex items-center justify-between rounded-3xl border border-emerald-100 bg-gradient-to-r from-emerald-50 via-sky-50 to-emerald-50 p-6 shadow-sm">
          <div>
            <h3 className="mb-1 font-semibold text-slate-900">
              Ready to execute this playbook?
            </h3>
            <p className="text-sm text-slate-600">
              Log this to your founder journey and start tracking progress
            </p>
          </div>
          <Button onClick={() => navigate("/journey")}>Log to journey</Button>
        </Card>
      </div>
    </LayoutShell>
  );
};

export default Playbook;
