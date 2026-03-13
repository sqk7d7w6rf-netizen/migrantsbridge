"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Scale,
  Briefcase,
  Users,
  ArrowRight,
  ClipboardList,
  UserCheck,
  FileText,
  Send,
} from "lucide-react";

const SERVICE_CARDS = [
  {
    icon: Scale,
    title: "Immigration Services",
    description:
      "Legal guidance on visa applications, asylum claims, work permits, and immigration status adjustments.",
  },
  {
    icon: Briefcase,
    title: "Job Placement",
    description:
      "Career counseling, resume assistance, job matching, and connections with employers who value diverse talent.",
  },
  {
    icon: Users,
    title: "Community Support",
    description:
      "Language classes, cultural orientation, housing assistance, and a welcoming community network.",
  },
];

const STEPS = [
  {
    icon: ClipboardList,
    number: 1,
    title: "Personal Information",
    description: "Share your basic details so we can get to know you.",
  },
  {
    icon: FileText,
    number: 2,
    title: "Case Details",
    description: "Tell us about the services you need and your current situation.",
  },
  {
    icon: UserCheck,
    number: 3,
    title: "Documents",
    description: "Upload any supporting documents you have available.",
  },
  {
    icon: Send,
    number: 4,
    title: "Review & Submit",
    description: "Review your application and submit it to our team.",
  },
];

export default function IntakeLandingPage() {
  return (
    <div className="space-y-10">
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Welcome to MigrantsBridge
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          We are here to help you build a new life with confidence. Our team
          provides free and confidential support for immigrants and refugees,
          no matter where you are in your journey.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {SERVICE_CARDS.map((card) => (
          <Card key={card.title} className="text-center">
            <CardHeader className="pb-2">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <card.icon className="h-6 w-6 text-primary" />
              </div>
              <CardTitle className="text-base mt-2">{card.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{card.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-center">What to Expect</h2>
        <p className="text-sm text-muted-foreground text-center">
          The application takes about 10-15 minutes. Here is what you will go through:
        </p>
        <div className="space-y-3">
          {STEPS.map((step) => (
            <div
              key={step.number}
              className="flex items-start gap-4 rounded-lg border bg-white p-4"
            >
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-white text-sm font-semibold">
                {step.number}
              </div>
              <div>
                <p className="font-medium text-sm">{step.title}</p>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="text-center space-y-3">
        <Link href="/intake/1">
          <Button size="lg" className="gap-2">
            Start Application
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
        <p className="text-xs text-muted-foreground">
          Your information is kept strictly confidential and will only be shared
          with your assigned case manager.
        </p>
      </div>
    </div>
  );
}
