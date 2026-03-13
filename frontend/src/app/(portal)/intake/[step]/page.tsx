"use client";

import { useState, useCallback, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { IntakeStepper } from "@/components/features/intake/intake-stepper";
import { IntakeProgressBar } from "@/components/features/intake/intake-progress-bar";
import { StepPersonalInfo } from "@/components/features/intake/step-personal-info";
import { StepCaseDetails } from "@/components/features/intake/step-case-details";
import { StepDocuments } from "@/components/features/intake/step-documents";
import { StepReview } from "@/components/features/intake/step-review";
import {
  INTAKE_STEPS,
  IntakeFormData,
  IntakePersonalInfo,
  IntakeCaseDetails,
  IntakeDocument,
} from "@/types/intake";

const EMPTY_PERSONAL_INFO: IntakePersonalInfo = {
  first_name: "",
  last_name: "",
  date_of_birth: "",
  gender: "",
  email: "",
  phone: "",
  preferred_language: "",
  nationality: "",
};

const EMPTY_CASE_DETAILS: IntakeCaseDetails = {
  service_type: "",
  immigration_status: "",
  description: "",
  urgency: "low",
};

const INITIAL_FORM_DATA: IntakeFormData = {
  personal_info: EMPTY_PERSONAL_INFO,
  case_details: EMPTY_CASE_DETAILS,
  documents: [],
  preferred_language: "en",
};

// Simple module-level store to persist data across step navigations
let persistedFormData: IntakeFormData = { ...INITIAL_FORM_DATA };
let persistedSubmitting = false;

export default function IntakeStepPage() {
  const params = useParams();
  const router = useRouter();
  const stepParam = params.step as string;
  const stepNumber = parseInt(stepParam, 10);

  const [formData, setFormData] = useState<IntakeFormData>(() => ({
    ...persistedFormData,
  }));
  const [submitting, setSubmitting] = useState(persistedSubmitting);

  const currentStepIndex = useMemo(() => {
    if (isNaN(stepNumber) || stepNumber < 1 || stepNumber > 4) return 0;
    return stepNumber - 1;
  }, [stepNumber]);

  const updatePersonalInfo = useCallback((data: IntakePersonalInfo) => {
    setFormData((prev) => {
      const next = { ...prev, personal_info: data };
      persistedFormData = next;
      return next;
    });
  }, []);

  const updateCaseDetails = useCallback((data: IntakeCaseDetails) => {
    setFormData((prev) => {
      const next = { ...prev, case_details: data };
      persistedFormData = next;
      return next;
    });
  }, []);

  const updateDocuments = useCallback((documents: IntakeDocument[]) => {
    setFormData((prev) => {
      const next = { ...prev, documents };
      persistedFormData = next;
      return next;
    });
  }, []);

  const goNext = useCallback(() => {
    if (stepNumber < 4) {
      router.push(`/intake/${stepNumber + 1}`);
    }
  }, [stepNumber, router]);

  const goBack = useCallback(() => {
    if (stepNumber > 1) {
      router.push(`/intake/${stepNumber - 1}`);
    }
  }, [stepNumber, router]);

  const handleSubmit = useCallback(async () => {
    setSubmitting(true);
    persistedSubmitting = true;
    try {
      // Simulate API submission delay
      await new Promise((resolve) => setTimeout(resolve, 1500));
      // Reset persisted state after successful submission
      persistedFormData = { ...INITIAL_FORM_DATA };
      persistedSubmitting = false;
      router.push("/intake/confirmation");
    } catch {
      setSubmitting(false);
      persistedSubmitting = false;
    }
  }, [router]);

  // Guard invalid step numbers
  if (isNaN(stepNumber) || stepNumber < 1 || stepNumber > 4) {
    router.replace("/intake/1");
    return null;
  }

  const renderStep = () => {
    switch (stepNumber) {
      case 1:
        return (
          <StepPersonalInfo
            data={formData.personal_info}
            onChange={updatePersonalInfo}
            onNext={goNext}
          />
        );
      case 2:
        return (
          <StepCaseDetails
            data={formData.case_details}
            onChange={updateCaseDetails}
            onNext={goNext}
            onBack={goBack}
          />
        );
      case 3:
        return (
          <StepDocuments
            documents={formData.documents}
            onChange={updateDocuments}
            onNext={goNext}
            onBack={goBack}
          />
        );
      case 4:
        return (
          <StepReview
            data={formData}
            onSubmit={handleSubmit}
            onBack={goBack}
            submitting={submitting}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-8">
      <IntakeStepper steps={INTAKE_STEPS} currentStepIndex={currentStepIndex} />
      <IntakeProgressBar currentStep={stepNumber} totalSteps={4} />
      <div>{renderStep()}</div>
    </div>
  );
}
