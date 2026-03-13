"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { IntakePersonalInfo } from "@/types/intake";

interface StepPersonalInfoProps {
  data: IntakePersonalInfo;
  onChange: (data: IntakePersonalInfo) => void;
  onNext: () => void;
}

const LANGUAGES = [
  "English",
  "Spanish",
  "French",
  "Arabic",
  "Chinese (Mandarin)",
  "Portuguese",
  "Hindi",
  "Bengali",
  "Urdu",
  "Tagalog",
  "Vietnamese",
  "Korean",
  "Haitian Creole",
  "Other",
];

const GENDERS = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
  { value: "non_binary", label: "Non-binary" },
  { value: "prefer_not_to_say", label: "Prefer not to say" },
];

export function StepPersonalInfo({
  data,
  onChange,
  onNext,
}: StepPersonalInfoProps) {
  const updateField = (field: keyof IntakePersonalInfo, value: string) => {
    onChange({ ...data, [field]: value });
  };

  const isValid =
    data.first_name.trim() !== "" &&
    data.last_name.trim() !== "" &&
    data.date_of_birth !== "" &&
    data.email.trim() !== "" &&
    data.phone.trim() !== "" &&
    data.preferred_language !== "" &&
    data.nationality.trim() !== "";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Personal Information</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Please provide your basic personal details.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="first_name">
            First Name <span className="text-destructive">*</span>
          </Label>
          <Input
            id="first_name"
            placeholder="Enter your first name"
            value={data.first_name}
            onChange={(e) => updateField("first_name", e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="last_name">
            Last Name <span className="text-destructive">*</span>
          </Label>
          <Input
            id="last_name"
            placeholder="Enter your last name"
            value={data.last_name}
            onChange={(e) => updateField("last_name", e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="date_of_birth">
            Date of Birth <span className="text-destructive">*</span>
          </Label>
          <Input
            id="date_of_birth"
            type="date"
            value={data.date_of_birth}
            onChange={(e) => updateField("date_of_birth", e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="gender">Gender</Label>
          <Select
            value={data.gender}
            onValueChange={(v) => updateField("gender", v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select gender" />
            </SelectTrigger>
            <SelectContent>
              {GENDERS.map((g) => (
                <SelectItem key={g.value} value={g.value}>
                  {g.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">
            Email Address <span className="text-destructive">*</span>
          </Label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            value={data.email}
            onChange={(e) => updateField("email", e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="phone">
            Phone Number <span className="text-destructive">*</span>
          </Label>
          <Input
            id="phone"
            type="tel"
            placeholder="+1 (555) 000-0000"
            value={data.phone}
            onChange={(e) => updateField("phone", e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="preferred_language">
            Preferred Language <span className="text-destructive">*</span>
          </Label>
          <Select
            value={data.preferred_language}
            onValueChange={(v) => updateField("preferred_language", v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent>
              {LANGUAGES.map((lang) => (
                <SelectItem key={lang} value={lang.toLowerCase()}>
                  {lang}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="nationality">
            Nationality <span className="text-destructive">*</span>
          </Label>
          <Input
            id="nationality"
            placeholder="Enter your nationality"
            value={data.nationality}
            onChange={(e) => updateField("nationality", e.target.value)}
          />
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <Button onClick={onNext} disabled={!isValid}>
          Continue
        </Button>
      </div>
    </div>
  );
}
