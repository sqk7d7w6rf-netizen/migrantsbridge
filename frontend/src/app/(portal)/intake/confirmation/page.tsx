"use client";

import { useMemo } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  CheckCircle,
  Clock,
  UserCheck,
  CalendarCheck,
  Phone,
  Mail,
  MapPin,
} from "lucide-react";

function generateReferenceNumber(): string {
  const digits = Math.floor(10000 + Math.random() * 90000);
  return `MB-2026-${digits}`;
}

const TIMELINE_STEPS = [
  {
    icon: Clock,
    title: "Application Review",
    description:
      "Our team will review your application within 1-2 business days. We carefully assess each submission to match you with the right services.",
    time: "1-2 business days",
  },
  {
    icon: UserCheck,
    title: "Case Manager Contact",
    description:
      "A dedicated case manager will reach out to you via phone or email to discuss your application and answer any questions.",
    time: "2-3 business days",
  },
  {
    icon: CalendarCheck,
    title: "Initial Appointment",
    description:
      "You will be invited to an in-person or virtual appointment to begin the process and create a personalized support plan.",
    time: "Within 1 week",
  },
];

export default function IntakeConfirmationPage() {
  const referenceNumber = useMemo(() => generateReferenceNumber(), []);

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <CheckCircle className="h-16 w-16 text-green-500" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight">
          Application Submitted
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Thank you for reaching out to MigrantsBridge. Your application has
          been received and our team will begin reviewing it shortly.
        </p>
        <div className="inline-flex items-center gap-2 rounded-lg border bg-muted/50 px-4 py-2">
          <span className="text-sm text-muted-foreground">
            Reference Number:
          </span>
          <span className="font-mono font-semibold text-lg">
            {referenceNumber}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">
          Please save this reference number for your records. You can use it
          to check the status of your application.
        </p>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-center">What Happens Next</h2>
        <div className="space-y-4">
          {TIMELINE_STEPS.map((step, index) => (
            <div
              key={step.title}
              className="relative flex items-start gap-4 rounded-lg border bg-white p-4"
            >
              {index < TIMELINE_STEPS.length - 1 && (
                <div className="absolute left-[2.15rem] top-[3.5rem] h-[calc(100%-1.5rem)] w-px bg-border" />
              )}
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
                <step.icon className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="font-medium text-sm">{step.title}</p>
                  <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
                    {step.time}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Contact Us</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            If you have questions or need to update your application, you can
            reach us through any of the following:
          </p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="flex items-center gap-2 text-sm">
              <Phone className="h-4 w-4 text-muted-foreground shrink-0" />
              <span>(555) 123-4567</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
              <span>intake@migrantsbridge.org</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <MapPin className="h-4 w-4 text-muted-foreground shrink-0" />
              <span>123 Bridge Street, Suite 200</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="text-center">
        <Link href="/intake">
          <Button variant="outline" size="lg">
            Return Home
          </Button>
        </Link>
      </div>
    </div>
  );
}
