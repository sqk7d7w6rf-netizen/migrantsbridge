"use client";

import { useParams, useRouter } from "next/navigation";
import { useDocument, useDeleteDocument } from "@/hooks/queries/use-documents";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { DOCUMENT_TYPES } from "@/lib/constants";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Download,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  FileImage,
  FileSpreadsheet,
  File,
} from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

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

function getFileIcon(fileType: string) {
  if (fileType.includes("image")) return FileImage;
  if (fileType.includes("spreadsheet") || fileType.includes("csv"))
    return FileSpreadsheet;
  if (fileType.includes("pdf") || fileType.includes("document"))
    return FileText;
  return File;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function DocumentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const documentId = params.documentId as string;
  const { data: document, isLoading } = useDocument(documentId);
  const deleteDocument = useDeleteDocument();

  if (isLoading) {
    return <LoadingSkeleton variant="detail" />;
  }

  if (!document) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Document not found</p>
      </div>
    );
  }

  const statusConfig = STATUS_CONFIGS[document.status];
  const StatusIcon = statusConfig?.icon ?? Clock;
  const FileIcon = getFileIcon(document.file_type);
  const typeLabel =
    DOCUMENT_TYPES[document.document_type as keyof typeof DOCUMENT_TYPES]
      ?.label ?? document.document_type;

  const handleDelete = async () => {
    await deleteDocument.mutateAsync(document.id);
    router.push("/documents");
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={document.name}
        description={document.file_name}
        actions={
          <div className="flex items-center gap-2">
            {document.url && (
              <Button variant="outline" asChild>
                <a href={document.url} download>
                  <Download className="mr-2 h-4 w-4" />
                  Download
                </a>
              </Button>
            )}
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteDocument.isPending}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </div>
        }
      />

      <div className="grid gap-6 md:grid-cols-3">
        {/* Main Content */}
        <div className="md:col-span-2 space-y-6">
          {/* Preview Area */}
          <Card>
            <CardHeader>
              <CardTitle>Document Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-12 bg-muted/50">
                <FileIcon className="h-16 w-16 text-muted-foreground" />
                <p className="mt-4 text-sm text-muted-foreground">
                  {document.file_name}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatFileSize(document.file_size)} - {document.file_type}
                </p>
                {document.url && (
                  <Button variant="outline" size="sm" className="mt-4" asChild>
                    <a href={document.url} target="_blank" rel="noopener noreferrer">
                      Open in New Tab
                    </a>
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Notes */}
          {document.notes && (
            <Card>
              <CardHeader>
                <CardTitle>Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm whitespace-pre-wrap">{document.notes}</p>
              </CardContent>
            </Card>
          )}

          {/* Version History */}
          {document.versions && document.versions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Version History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {document.versions.map((version) => (
                    <div
                      key={version.id}
                      className="flex items-center justify-between rounded-lg border p-4"
                    >
                      <div>
                        <p className="text-sm font-medium">
                          Version {version.version_number}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {version.uploaded_by_name ?? "Unknown"} -{" "}
                          {format(
                            new Date(version.created_at),
                            "MMM d, yyyy h:mm a"
                          )}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {version.file_name} ({formatFileSize(version.file_size)})
                        </p>
                      </div>
                      {version.url && (
                        <Button variant="ghost" size="sm" asChild>
                          <a href={version.url} download>
                            <Download className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Card */}
          <Card>
            <CardHeader>
              <CardTitle>Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <StatusIcon className="h-5 w-5" />
                <span
                  className={cn(
                    "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                    statusConfig?.color
                  )}
                >
                  {statusConfig?.label ?? document.status}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Metadata Card */}
          <Card>
            <CardHeader>
              <CardTitle>Information</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="space-y-4 text-sm">
                <div>
                  <dt className="text-muted-foreground">Document Type</dt>
                  <dd className="mt-0.5">
                    <Badge variant="secondary">{typeLabel}</Badge>
                  </dd>
                </div>
                <Separator />
                <div>
                  <dt className="text-muted-foreground">File Type</dt>
                  <dd className="mt-0.5 font-medium">{document.file_type}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">File Size</dt>
                  <dd className="mt-0.5 font-medium">
                    {formatFileSize(document.file_size)}
                  </dd>
                </div>
                <Separator />
                <div>
                  <dt className="text-muted-foreground">Uploaded By</dt>
                  <dd className="mt-0.5 font-medium">
                    {document.uploaded_by_name ?? "Unknown"}
                  </dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Uploaded Date</dt>
                  <dd className="mt-0.5 font-medium">
                    {format(
                      new Date(document.created_at),
                      "MMM d, yyyy h:mm a"
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Last Updated</dt>
                  <dd className="mt-0.5 font-medium">
                    {format(
                      new Date(document.updated_at),
                      "MMM d, yyyy h:mm a"
                    )}
                  </dd>
                </div>
                {document.expiry_date && (
                  <div>
                    <dt className="text-muted-foreground">Expiry Date</dt>
                    <dd className="mt-0.5 font-medium">
                      {format(
                        new Date(document.expiry_date),
                        "MMM d, yyyy"
                      )}
                    </dd>
                  </div>
                )}
              </dl>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
