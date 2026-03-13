"use client";

import { Document } from "@/types/document";
import { DOCUMENT_TYPES } from "@/lib/constants";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Download, CheckCircle, XCircle, Clock } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

interface DocumentPreviewPanelProps {
  document: Document | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const STATUS_CONFIGS: Record<
  string,
  { label: string; color: string; icon: typeof Clock }
> = {
  pending: {
    label: "Pending Review",
    color: "bg-yellow-100 text-yellow-800",
    icon: Clock,
  },
  approved: {
    label: "Approved",
    color: "bg-green-100 text-green-800",
    icon: CheckCircle,
  },
  rejected: {
    label: "Rejected",
    color: "bg-red-100 text-red-800",
    icon: XCircle,
  },
  expired: {
    label: "Expired",
    color: "bg-gray-100 text-gray-800",
    icon: Clock,
  },
};

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function DocumentPreviewPanel({
  document,
  open,
  onOpenChange,
}: DocumentPreviewPanelProps) {
  if (!document) return null;

  const statusConfig = STATUS_CONFIGS[document.status];
  const StatusIcon = statusConfig?.icon ?? Clock;
  const typeLabel =
    DOCUMENT_TYPES[document.document_type as keyof typeof DOCUMENT_TYPES]
      ?.label ?? document.document_type;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader>
          <SheetTitle>{document.name}</SheetTitle>
          <SheetDescription>{document.file_name}</SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Status */}
          <div>
            <h4 className="text-sm font-medium mb-2">Verification Status</h4>
            <div className="flex items-center gap-2">
              <StatusIcon className="h-4 w-4" />
              <span
                className={cn(
                  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                  statusConfig?.color
                )}
              >
                {statusConfig?.label ?? document.status}
              </span>
            </div>
          </div>

          <Separator />

          {/* Metadata */}
          <div>
            <h4 className="text-sm font-medium mb-3">Document Information</h4>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Type</dt>
                <dd>
                  <Badge variant="secondary">{typeLabel}</Badge>
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">File Size</dt>
                <dd>{formatFileSize(document.file_size)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">File Type</dt>
                <dd>{document.file_type}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Uploaded By</dt>
                <dd>{document.uploaded_by_name ?? "Unknown"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Uploaded</dt>
                <dd>
                  {format(new Date(document.created_at), "MMM d, yyyy h:mm a")}
                </dd>
              </div>
              {document.expiry_date && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Expires</dt>
                  <dd>
                    {format(new Date(document.expiry_date), "MMM d, yyyy")}
                  </dd>
                </div>
              )}
            </dl>
          </div>

          <Separator />

          {/* Notes */}
          {document.notes && (
            <>
              <div>
                <h4 className="text-sm font-medium mb-2">Notes</h4>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {document.notes}
                </p>
              </div>
              <Separator />
            </>
          )}

          {/* Version History */}
          {document.versions && document.versions.length > 0 && (
            <div>
              <h4 className="text-sm font-medium mb-3">Version History</h4>
              <div className="space-y-3">
                {document.versions.map((version) => (
                  <div
                    key={version.id}
                    className="flex items-center justify-between text-sm rounded-lg border p-3"
                  >
                    <div>
                      <p className="font-medium">
                        Version {version.version_number}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {version.uploaded_by_name ?? "Unknown"} -{" "}
                        {format(
                          new Date(version.created_at),
                          "MMM d, yyyy"
                        )}
                      </p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatFileSize(version.file_size)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Download */}
          {document.url && (
            <Button asChild className="w-full">
              <a href={document.url} download>
                <Download className="mr-2 h-4 w-4" />
                Download Document
              </a>
            </Button>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
