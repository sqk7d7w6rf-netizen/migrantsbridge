"use client";

import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { IntakeCaseDetails } from "@/types/intake";
import { SERVICE_TYPES, IMMIGRATION_STATUSES } from "@/lib/constants";

interface StepCaseDetailsProps {
  data: IntakeCaseDetails;
  onChange: (data: IntakeCaseDetails) => void;
  onNext: () => void;
  onBack: () => void;
}

const URGENCY_OPTIONS = [
  { value: "low", label: "Low - No immediate deadline" },
  { value: "medium", label: "Medium - Within the next few months" },
  { value: "high", label: "High - Within the next few weeks" },
  { value: "urgent", label: "Urgent - Immediate attention needed" },
];

export function StepCaseDetails({
  data,
  onChange,
  onNext,
  onBack,
}: StepCaseDetailsProps) {
  const updateField = (field: keyof IntakeCaseDetails, value: string) => {
    onChange({ ...data, [field]: value });
  };

  const isValid =
    data.service_type !== "" &&
    data.immigration_status !== "" &&
    data.description.trim() !== "" &&
    data.urgency !== "";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Case Details</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Tell us about the services you need and your current situation.
        </p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="service_type">
            Service Type <span className="text-destructive">*</span>
          </Label>
          <Select
            value={data.service_type}
            onValueChange={(v) => updateField("service_type", v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select the service you need" />
            </SelectTrigger>
            <SelectContent>
              {SERVICE_TYPES.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="immigration_status">
            Current Immigration Status <span className="text-destructive">*</span>
          </Label>
          <Select
            value={data.immigration_status}
            onValueChange={(v) => updateField("immigration_status", v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select your immigration status" />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(IMMIGRATION_STATUSES).map(([key, config]) => (
                <SelectItem key={key} value={key}>
                  {config.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">
            Description <span className="text-destructive">*</span>
          </Label>
          <Textarea
            id="description"
            placeholder="Please describe your situation and what kind of help you are looking for..."
            value={data.description}
            onChange={(e) => updateField("description", e.target.value)}
            rows={5}
          />
          <p className="text-xs text-muted-foreground">
            The more detail you provide, the better we can assist you.
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="urgency">
            Urgency Level <span className="text-destructive">*</span>
          </Label>
          <Select
            value={data.urgency}
            onValueChange={(v) => updateField("urgency", v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select urgency level" />
            </SelectTrigger>
            <SelectContent>
              {URGENCY_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <Button variant="outline" onClick={onBack}>
          Back
        </Button>
        <Button onClick={onNext} disabled={!isValid}>
          Continue
        </Button>
      </div>
    </div>
  );
}
