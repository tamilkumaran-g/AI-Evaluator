import { Button } from "../components/ui/button"
import { Card } from "../components/ui/card";
import { Avatar, AvatarFallback } from "../components/ui/avatar";
import { Badge } from "../components/ui/badge";
import { Download, Calendar, CheckCircle2, FileText, TrendingUp, Target, Lightbulb } from "lucide-react";
import { useNavigate } from "react-router-dom";
import LayoutShell from "../components/LayoutShell";

const Journey = () => {
  const navigate = useNavigate();

  const timelineEvents = [
    {
      date: "Nov 15, 2024",
      icon: CheckCircle2,
      title: "Completed Myve conversation",
      description: "Structured idea: Founder Sales AI",
      color: "text-emerald-600"
    },
    {
      date: "Nov 15, 2024",
      icon: TrendingUp,
      title: "Validation report generated",
      description: "Overall score: 81/100 - High potential",
      color: "text-emerald-600"
    },
    {
      date: "Nov 15, 2024",
      icon: Target,
      title: "Sales playbook created",
      description: "ICP defined, outreach scripts ready",
      color: "text-sky-600"
    },
    {
      date: "Nov 14, 2024",
      icon: Lightbulb,
      title: "Joined Myve early access",
      description: "Started founder journey tracking",
      color: "text-slate-400"
    }
  ];

  return (
    <LayoutShell
      title="Founder journey"
      rightActions={
        <Button variant="outline" size="sm">
          <Download className="mr-2 h-4 w-4" />
          Export profile
        </Button>
      }
    >
      <div className="space-y-8">
          {/* Profile Header */}
          <Card className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-start gap-6">
              <Avatar className="h-20 w-20">
                <AvatarFallback className="bg-gradient-to-br from-[#1b9cc8] to-[#1787ad] text-2xl text-white">
                  JD
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h1 className="mb-1 text-2xl font-semibold text-slate-900">John Doe</h1>
                    <p className="text-slate-500">Bangalore, India</p>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant="secondary">Idea-stage founder</Badge>
                    <Badge variant="secondary">B2B SaaS</Badge>
                  </div>
                </div>
                <p className="mb-4 text-sm leading-relaxed text-slate-700">
                  Building tools to help first-time founders structure their ideas and create their first sales systems.
                </p>
                <div className="flex gap-8 text-sm">
                  <div>
                    <div className="text-2xl font-semibold text-slate-900">1</div>
                    <div className="text-slate-500">Ideas explored</div>
                  </div>
                  <div>
                    <div className="text-2xl font-semibold text-slate-900">1</div>
                    <div className="text-slate-500">Validations completed</div>
                  </div>
                  <div>
                    <div className="text-2xl font-semibold text-slate-900">1</div>
                    <div className="text-slate-500">Sales playbooks</div>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <div className="grid gap-8 lg:grid-cols-3">
            {/* Timeline */}
            <div className="lg:col-span-2 space-y-6">
              <h2 className="text-xl font-semibold text-slate-900">Founder Journey Timeline</h2>
              
              <div className="space-y-4">
                {timelineEvents.map((event, i) => (
                  <Card key={i} className="cursor-pointer rounded-2xl border border-slate-200 bg-white p-5 transition-shadow hover:shadow-md">
                    <div className="flex gap-4">
                      <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-slate-100 ${event.color}`}>
                        <event.icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-1">
                          <h3 className="font-semibold text-slate-900">{event.title}</h3>
                          <div className="flex items-center gap-1.5 text-xs text-slate-500">
                            <Calendar className="w-3 h-3" />
                            {event.date}
                          </div>
                        </div>
                        <p className="text-sm text-slate-600">{event.description}</p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              <Card className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900">Current Focus</h3>
                <div className="space-y-3">
                  <div>
                    <p className="mb-1 text-sm text-slate-500">Active idea</p>
                    <p className="font-medium text-slate-900">Founder Sales AI</p>
                  </div>
                  <div>
                    <p className="mb-1 text-sm text-slate-500">Stage</p>
                    <Badge>Validating offers</Badge>
                  </div>
                </div>
              </Card>

              <Card className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900">Next Actions</h3>
                <ul className="space-y-2.5 text-sm">
                  <li className="flex gap-2">
                    <div className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-sky-600" />
                    <span className="text-slate-800">Reach out to 20 founders on LinkedIn</span>
                  </li>
                  <li className="flex gap-2">
                    <div className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-sky-600" />
                    <span className="text-slate-800">Test pricing: ₹299 vs ₹499</span>
                  </li>
                  <li className="flex gap-2">
                    <div className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-sky-600" />
                    <span className="text-slate-800">Build minimal conversational MVP</span>
                  </li>
                </ul>
              </Card>

              <Card className="space-y-4 rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900">Mentor & community</h3>
                <p className="text-sm text-slate-600">
                  Connect with mentors and share your journey with communities (coming soon)
                </p>
                <Button variant="outline" className="w-full" disabled>
                  Coming soon
                </Button>
              </Card>

              <Button className="w-full">
                <FileText className="w-4 h-4 mr-2" />
                Download founder snapshot
              </Button>
            </div>
          </div>
        </div>
    </LayoutShell>
  );
};

export default Journey;
