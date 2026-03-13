"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { IntakeFormData } from "@/types/intake";
import { IMMIGRATION_STATUSES, SERVICE_TYPES } from "@/lib/constants";
import { Check, FileText, User, Briefcase } from "lucide-react";
import { format } from "date-fns";

interface StepReviewProps {
  data: IntakeFormData;
  onSubmit: () => void;
  onBack: () => void;
  submitting?: boolean;
}

export function StepReview({
  data,
  onSubmit,
  onBack,
  submitting = false,
}: StepReviewProps) {
  const { personal_info, case_details, documents } = data;

  const serviceLabel =
    SERVICE_TYPES.find((s) => s.value === case_details.service_type)?.label ||
    case_details.service_type;

  const immigrationLabel =
    IMMIGRATION_STATUSES[
      case_details.immigration_status as keyof typeof IMMIGRATION_STATUSES
    ]?.label || case_details.immigration_status;

  const uploadedDocs = documents.filter((d) => d.uploaded);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Review Your Application</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Please review all the information below before submitting your
          application.
        </p>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <User className="h-4 w-4" />
            Personal Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
            <div>
              <span className="text-muted-foreground">Name:</span>{" "}
              <span className="font-medium">
                {personal_info.first_name} {personal_info.last_name}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Date of Birth:</span>{" "}
              <span className="font-medium">
                {personal_info.date_of_birth
                  ? format(
                      new Date(personal_info.date_of_birth + "T00:00:00"),
                      "MMMM d, yyyy"
                    )
                  : "-"}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Email:</span>{" "}
              <span className="font-medium">{personal_info.email}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Phone:</span>{" "}
              <span className="font-medium">{personal_info.phone}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Language:</span>{" "}
              <span className="font-medium capitalize">
                {personal_info.preferred_language}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Nationality:</span>{" "}
              <span className="font-medium">{personal_info.nationality}</span>
            </div>
            {personal_info.gender && (
              <div>
                <span className="text-muted-foreground">Gender:</span>{" "}
                <span className="font-medium capitalize">
                  {personal_info.gender.replace(/_/g, " ")}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Briefcase className="h-4 w-4" />
            Case Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
            <div>
              <span className="text-muted-foreground">Service Type:</span>{" "}
              <span className="font-medium">{serviceLabel}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Immigration Status:</span>{" "}
              <span className="font-medium">{immigrationLabel}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Urgency:</span>{" "}
              <span className="font-medium capitalize">
                {case_details.urgency}
              </span>
            </div>
          </div>
          <Separator className="my-2" />
          <div className="text-sm">
            <span className="text-muted-foreground">Description:</span>
            <p className="mt-1 font-medium whitespace-pre-wrap">
              {case_details.description}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="h-4 w-4" />
            Documents ({uploadedDocs.length} uploaded)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {uploadedDocs.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No documents uploaded
            </p>
          ) : (
            <ul className="space-y-1.5">
              {uploadedDocs.map((doc) => (
                <li key={doc.id} className="flex items-center gap-2 text-sm">
                  <Check className="h-4 w-4 text-green-500" />
                  <span>{doc.name}</span>
                  {doc.file && (
                    <span className="text-muted-foreground">
                      ({doc.file.name})
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <div className="rounded-md border bg-muted/50 p-4">
        <p className="text-sm text-muted-foreground">
          By submitting this application, you confirm that all the information
          provided is accurate and complete to the best of your knowledge. You
          agree to be contacted by MigrantsBridge regarding your application.
        </p>
      </div>

      <div className="flex justify-between pt-4">
        <Button variant="outline" onClick={onBack} disabled={submitting}>
          Back
        </Button>
        <Button onClick={onSubmit} disabled={submitting}>
          {submitting ? "Submitting..." : "Submit Application"}
        </Button>
      </div>
    </div>
  );
}
