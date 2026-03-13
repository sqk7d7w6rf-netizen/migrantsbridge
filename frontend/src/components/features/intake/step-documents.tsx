"use client";

import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { IntakeDocument } from "@/types/intake";
import { cn } from "@/lib/utils";
import { Upload, Check, X, FileText, AlertCircle } from "lucide-react";

interface StepDocumentsProps {
  documents: IntakeDocument[];
  onChange: (documents: IntakeDocument[]) => void;
  onNext: () => void;
  onBack: () => void;
}

const REQUIRED_DOCUMENTS: Omit<IntakeDocument, "id" | "file" | "uploaded">[] = [
  { name: "Government-issued ID", type: "id", required: true },
  { name: "Proof of Address", type: "address_proof", required: true },
  { name: "Immigration Documents (if applicable)", type: "immigration", required: false },
  { name: "Employment Verification", type: "employment", required: false },
  { name: "Supporting Letters or References", type: "supporting", required: false },
];

export function StepDocuments({
  documents,
  onChange,
  onNext,
  onBack,
}: StepDocumentsProps) {
  const fileInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const initDocuments = (): IntakeDocument[] => {
    if (documents.length > 0) return documents;
    return REQUIRED_DOCUMENTS.map((doc, index) => ({
      ...doc,
      id: `doc-${index}`,
      uploaded: false,
    }));
  };

  const currentDocuments = initDocuments();

  const handleFileSelect = (docId: string, file: File) => {
    const updated = currentDocuments.map((doc) =>
      doc.id === docId ? { ...doc, file, uploaded: true } : doc
    );
    onChange(updated);
  };

  const handleRemoveFile = (docId: string) => {
    const updated = currentDocuments.map((doc) =>
      doc.id === docId ? { ...doc, file: undefined, uploaded: false } : doc
    );
    onChange(updated);
  };

  const requiredUploaded = currentDocuments
    .filter((d) => d.required)
    .every((d) => d.uploaded);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Documents</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Upload the required documents to support your application. Items
          marked with an asterisk are required.
        </p>
      </div>

      <div className="space-y-3">
        {currentDocuments.map((doc) => (
          <Card
            key={doc.id}
            className={cn(
              "transition-colors",
              doc.uploaded && "border-green-200 bg-green-50/50"
            )}
          >
            <CardContent className="flex items-center gap-4 p-4">
              <div
                className={cn(
                  "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
                  doc.uploaded
                    ? "bg-green-100 text-green-600"
                    : "bg-muted text-muted-foreground"
                )}
              >
                {doc.uploaded ? (
                  <Check className="h-5 w-5" />
                ) : (
                  <FileText className="h-5 w-5" />
                )}
              </div>

              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">
                  {doc.name}
                  {doc.required && (
                    <span className="text-destructive ml-1">*</span>
                  )}
                </p>
                {doc.uploaded && doc.file ? (
                  <p className="text-xs text-muted-foreground truncate">
                    {doc.file.name} (
                    {(doc.file.size / 1024).toFixed(1)} KB)
                  </p>
                ) : (
                  <p className="text-xs text-muted-foreground">
                    PDF, JPG, or PNG up to 10MB
                  </p>
                )}
              </div>

              <div className="flex items-center gap-2">
                {doc.uploaded ? (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-destructive"
                    onClick={() => handleRemoveFile(doc.id)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                ) : (
                  <>
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      className="hidden"
                      ref={(el) => {
                        fileInputRefs.current[doc.id] = el;
                      }}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFileSelect(doc.id, file);
                      }}
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        fileInputRefs.current[doc.id]?.click()
                      }
                    >
                      <Upload className="mr-1.5 h-3.5 w-3.5" />
                      Upload
                    </Button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {!requiredUploaded && (
        <div className="flex items-center gap-2 rounded-md border border-yellow-200 bg-yellow-50 p-3">
          <AlertCircle className="h-4 w-4 text-yellow-600 shrink-0" />
          <p className="text-xs text-yellow-700">
            Please upload all required documents before proceeding.
          </p>
        </div>
      )}

      <div className="flex justify-between pt-4">
        <Button variant="outline" onClick={onBack}>
          Back
        </Button>
        <Button onClick={onNext} disabled={!requiredUploaded}>
          Continue
        </Button>
      </div>
    </div>
  );
}
