"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useDocuments, useDeleteDocument } from "@/hooks/queries/use-documents";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { DocumentGrid } from "@/components/features/documents/document-grid";
import { DocumentUploadDialog } from "@/components/features/documents/document-upload-dialog";
import { DocumentPreviewPanel } from "@/components/features/documents/document-preview-panel";
import { Button } from "@/components/ui/button";
import { Upload, FileText } from "lucide-react";
import { Document } from "@/types/document";

export default function DocumentsPage() {
  const router = useRouter();
  const { data, isLoading } = useDocuments();
  const deleteDocument = useDeleteDocument();
  const [uploadOpen, setUploadOpen] = useState(false);
  const [previewDoc, setPreviewDoc] = useState<Document | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Documents"
          description="Global document library"
        />
        <LoadingSkeleton variant="card" count={6} />
      </div>
    );
  }

  const documents = data?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Documents"
        description="Global document library"
        actions={
          <Button onClick={() => setUploadOpen(true)}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Document
          </Button>
        }
      />

      {documents.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No documents yet"
          description="Upload your first document to get started."
          actionLabel="Upload Document"
          onAction={() => setUploadOpen(true)}
        />
      ) : (
        <DocumentGrid
          documents={documents}
          onView={(doc) => router.push(`/documents/${doc.id}`)}
          onDelete={(doc) => deleteDocument.mutate(doc.id)}
        />
      )}

      <DocumentUploadDialog
        open={uploadOpen}
        onOpenChange={setUploadOpen}
      />

      <DocumentPreviewPanel
        document={previewDoc}
        open={!!previewDoc}
        onOpenChange={(open) => {
          if (!open) setPreviewDoc(null);
        }}
      />
    </div>
  );
}
