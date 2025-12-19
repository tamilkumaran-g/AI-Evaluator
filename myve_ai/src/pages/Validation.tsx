import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Progress } from "../components/ui/progress";
import { Download, RefreshCw, CheckCircle2, AlertCircle, TrendingUp } from "lucide-react";
import { useNavigate } from "react-router-dom";
import LayoutShell from "../components/LayoutShell";

const Validation = () => {
  const navigate = useNavigate();

  return (
    <LayoutShell
      title="Validation report"
      rightActions={
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Download PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/workspace")}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Refine with Myve
          </Button>
        </div>
      }
    >
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="mb-2 text-3xl font-semibold text-slate-900">
            Validation report
          </h1>
          <p className="text-sm text-slate-500">
            Draft v1 generated from your Myve session • Founder Sales AI
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Overall Score */}
            <Card className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900">Overall Validation Score</h2>
              <div className="flex items-center gap-4">
                <div className="text-5xl font-bold text-emerald-600">81</div>
                <div>
                  <div className="mb-1 inline-block rounded-full bg-emerald-50 px-3 py-1 text-sm font-medium text-emerald-600">
                    High potential
                  </div>
                  <p className="text-sm text-slate-500">Strong foundation with clear path forward</p>
                </div>
              </div>

              <div className="space-y-3 pt-2">
                <div>
                  <div className="mb-1.5 flex justify-between text-sm">
                    <span className="text-slate-700">Problem clarity</span>
                    <span className="font-semibold text-slate-900">9/10</span>
                  </div>
                  <Progress value={90} className="h-2" />
                </div>
                <div>
                  <div className="mb-1.5 flex justify-between text-sm">
                    <span className="text-slate-700">Market demand</span>
                    <span className="font-semibold text-slate-900">8/10</span>
                  </div>
                  <Progress value={80} className="h-2" />
                </div>
                <div>
                  <div className="mb-1.5 flex justify-between text-sm">
                    <span className="text-slate-700">Differentiation</span>
                    <span className="font-semibold text-slate-900">7/10</span>
                  </div>
                  <Progress value={70} className="h-2" />
                </div>
                <div>
                  <div className="mb-1.5 flex justify-between text-sm">
                    <span className="text-slate-700">Execution complexity</span>
                    <span className="font-semibold text-slate-900">6/10</span>
                  </div>
                  <Progress value={60} className="h-2" />
                  <p className="mt-1 text-xs text-slate-500">Lower is better</p>
                </div>
              </div>
            </Card>

            {/* Key Strengths */}
            <Card className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                <h3 className="font-semibold text-slate-900">Key Strengths</h3>
              </div>
              <ul className="space-y-2.5">
                <li className="flex gap-2 text-sm">
                  <span className="font-bold text-emerald-600">•</span>
                  <span className="text-slate-800">Clear target audience of first-time founders struggling with structure and sales clarity</span>
                </li>
                <li className="flex gap-2 text-sm">
                  <span className="font-bold text-emerald-600">•</span>
                  <span className="text-slate-800">Addresses genuine pain point in founder journey before traditional CRM stage</span>
                </li>
                <li className="flex gap-2 text-sm">
                  <span className="font-bold text-emerald-600">•</span>
                  <span className="text-slate-800">Strong positioning as "pre-CRM for founders" creates unique market category</span>
                </li>
              </ul>
            </Card>

            {/* Key Risks */}
            <Card className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-amber-600" />
                <h3 className="font-semibold text-slate-900">Key Risks & Unknowns</h3>
              </div>
              <ul className="space-y-2.5">
                <li className="flex gap-2 text-sm">
                  <span className="font-bold text-amber-600">•</span>
                  <span className="text-slate-800">Willingness-to-pay unclear: founders at idea stage often have limited budgets</span>
                </li>
                <li className="flex gap-2 text-sm">
                  <span className="font-bold text-amber-600">•</span>
                  <span className="text-slate-800">Competition from free alternatives (notion templates, AI chatbots, communities)</span>
                </li>
                <li className="flex gap-2 text-sm">
                  <span className="font-bold text-amber-600">•</span>
                  <span className="text-slate-800">Distribution challenge: reaching first-time founders requires community access</span>
                </li>
              </ul>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Myve Summary */}
            <Card className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-sky-600" />
                <h3 className="font-semibold text-slate-900">Myve Summary</h3>
              </div>
              <p className="text-sm leading-relaxed text-slate-700">
                This is a conversational AI tool that helps first-time founders move from scattered ideas to structured execution. It combines validation scoring with sales system generation, positioning itself as the "first conversation" a founder has before they're ready for traditional CRM. The core insight is that founders need structure and clarity before they need process and automation.
              </p>
            </Card>

            {/* Signals & Assumptions */}
            <Card className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">Signals & Assumptions</h3>
              <div className="space-y-3">
                <div className="flex gap-2">
                  <div className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-sky-600" />
                  <div className="text-sm">
                    <p className="font-medium text-slate-900">Assumes founders will pay for clarity</p>
                    <p className="mt-0.5 text-xs text-slate-500">Test: Run 20 validation calls at ₹299 vs ₹499</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <div className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-sky-600" />
                  <div className="text-sm">
                    <p className="font-medium text-slate-900">Assumes communities are reachable via LinkedIn / WhatsApp</p>
                    <p className="mt-0.5 text-xs text-slate-500">Test: Reach out to 50 founders in next 7 days</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <div className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-sky-600" />
                  <div className="text-sm">
                    <p className="font-medium text-slate-900">Assumes low initial build cost for MVP</p>
                    <p className="mt-0.5 text-xs text-slate-500">Validate: Can Lovable + OpenAI deliver in 2 weeks?</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <div className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-sky-600" />
                  <div className="text-sm">
                    <p className="font-medium text-slate-900">Assumes founders prefer conversation over templates</p>
                    <p className="mt-0.5 text-xs text-slate-500">Test: Compare engagement vs free Notion template</p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Next Steps */}
            <Card className="space-y-4 rounded-3xl border border-sky-100 bg-gradient-to-br from-[#e0f4ff] via-[#f1f5ff] to-[#e4f5ff] p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">Recommended Next Steps</h3>
              <ol className="space-y-2.5 text-sm">
                <li className="flex gap-2">
                  <span className="font-semibold text-sky-600">1.</span>
                  <span className="text-slate-800">Generate your sales playbook with ICP and outreach scripts</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-semibold text-sky-600">2.</span>
                  <span className="text-slate-800">Run 20 founder conversations in next 14 days to test willingness-to-pay</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-semibold text-sky-600">3.</span>
                  <span className="text-slate-800">Build minimal conversational interface to test value proposition</span>
                </li>
              </ol>
            </Card>
          </div>
        </div>

        {/* CTA */}
        <Card className="flex items-center justify-between rounded-3xl border border-sky-100 bg-gradient-to-r from-[#e0f4ff] via-[#f1f5ff] to-[#e4f5ff] p-6 shadow-sm">
          <div>
            <h3 className="mb-1 font-semibold text-slate-900">Ready to turn this into a sales system?</h3>
            <p className="text-sm text-slate-600">Generate your complete sales playbook with ICP, offers, channels, and scripts</p>
          </div>
          <Button onClick={() => navigate('/playbook')}>
            Generate sales playbook
          </Button>
        </Card>
      </div>
    </LayoutShell>
  );
};

export default Validation;
