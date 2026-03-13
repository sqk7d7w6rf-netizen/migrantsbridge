"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useCase, useCaseNotes, useAddCaseNote, useCaseHistory } from "@/hooks/queries/use-cases";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { StatusBadge } from "@/components/shared/status-badge";
import { CaseTimeline } from "@/components/features/clients/case-timeline";
import { CASE_STATUSES, PRIORITIES } from "@/lib/constants";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import {
  Pencil,
  Calendar,
  User,
  FileText,
  MessageSquare,
  Clock,
  CheckSquare,
  Send,
} from "lucide-react";
import { format } from "date-fns";

export default function CaseDetailPage() {
  const params = useParams();
  const clientId = params.clientId as string;
  const caseId = params.caseId as string;
  const { data: caseItem, isLoading } = useCase(caseId);
  const { data: notes = [] } = useCaseNotes(caseId);
  const { data: history = [] } = useCaseHistory(caseId);
  const addNote = useAddCaseNote(caseId);

  const [noteContent, setNoteContent] = useState("");
  const [isInternal, setIsInternal] = useState(true);

  if (isLoading) {
    return <LoadingSkeleton variant="detail" />;
  }

  if (!caseItem) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Case not found</p>
      </div>
    );
  }

  const handleAddNote = async () => {
    if (!noteContent.trim()) return;
    await addNote.mutateAsync({
      content: noteContent.trim(),
      is_internal: isInternal,
    });
    setNoteContent("");
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={caseItem.title}
        description={`Case ${caseItem.case_number}`}
        actions={
          <Button variant="outline">
            <Pencil className="mr-2 h-4 w-4" />
            Edit Case
          </Button>
        }
      />

      {/* Case Header Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground">Status</div>
            <div className="mt-1">
              <StatusBadge status={caseItem.status} statusMap={CASE_STATUSES} />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground">Priority</div>
            <div className="mt-1">
              <StatusBadge status={caseItem.priority} statusMap={PRIORITIES} />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground">Assigned To</div>
            <div className="mt-1 flex items-center gap-1">
              <User className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">
                {caseItem.assigned_to_name || "Unassigned"}
              </span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground">Opened</div>
            <div className="mt-1 flex items-center gap-1">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">
                {format(new Date(caseItem.opened_date), "MMM d, yyyy")}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Case Details */}
      {(caseItem.description || caseItem.due_date || caseItem.tags) && (
        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-muted-foreground">Case Type</dt>
                <dd className="font-medium">{caseItem.case_type}</dd>
              </div>
              {caseItem.due_date && (
                <div>
                  <dt className="text-muted-foreground">Due Date</dt>
                  <dd className="font-medium">
                    {format(new Date(caseItem.due_date), "MMM d, yyyy")}
                  </dd>
                </div>
              )}
              {caseItem.closed_date && (
                <div>
                  <dt className="text-muted-foreground">Closed Date</dt>
                  <dd className="font-medium">
                    {format(new Date(caseItem.closed_date), "MMM d, yyyy")}
                  </dd>
                </div>
              )}
              {caseItem.description && (
                <div className="col-span-2">
                  <dt className="text-muted-foreground">Description</dt>
                  <dd className="font-medium whitespace-pre-wrap">
                    {caseItem.description}
                  </dd>
                </div>
              )}
              {caseItem.tags && caseItem.tags.length > 0 && (
                <div className="col-span-2">
                  <dt className="text-muted-foreground mb-1">Tags</dt>
                  <dd className="flex flex-wrap gap-1">
                    {caseItem.tags.map((tag) => (
                      <Badge key={tag} variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </dd>
                </div>
              )}
            </dl>
          </CardContent>
        </Card>
      )}

      {/* Tabbed Content */}
      <Tabs defaultValue="notes" className="w-full">
        <TabsList>
          <TabsTrigger value="notes">
            <MessageSquare className="mr-2 h-4 w-4" />
            Notes
          </TabsTrigger>
          <TabsTrigger value="history">
            <Clock className="mr-2 h-4 w-4" />
            History
          </TabsTrigger>
          <TabsTrigger value="documents" asChild>
            <Link href={`/clients/${clientId}/cases/${caseId}/documents`}>
              <FileText className="mr-2 h-4 w-4" />
              Documents
            </Link>
          </TabsTrigger>
          <TabsTrigger value="tasks">
            <CheckSquare className="mr-2 h-4 w-4" />
            Tasks
          </TabsTrigger>
        </TabsList>

        <TabsContent value="notes" className="mt-4 space-y-4">
          {/* Note Composer */}
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3">
                <Textarea
                  placeholder="Write a note..."
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  rows={3}
                />
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={isInternal}
                      onChange={(e) => setIsInternal(e.target.checked)}
                      className="rounded border-gray-300"
                    />
                    Internal note
                  </label>
                  <Button
                    size="sm"
                    onClick={handleAddNote}
                    disabled={!noteContent.trim() || addNote.isPending}
                  >
                    <Send className="mr-2 h-4 w-4" />
                    {addNote.isPending ? "Sending..." : "Add Note"}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Notes List */}
          {notes.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No notes yet. Add the first note above.
            </p>
          ) : (
            <div className="space-y-3">
              {notes.map((note) => (
                <Card key={note.id}>
                  <CardContent className="pt-4 pb-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">
                          {note.author_name}
                        </span>
                        {note.is_internal && (
                          <Badge variant="secondary" className="text-xs">
                            Internal
                          </Badge>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {format(
                          new Date(note.created_at),
                          "MMM d, yyyy h:mm a"
                        )}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">
                      {note.content}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="history" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Case History</CardTitle>
            </CardHeader>
            <CardContent>
              <CaseTimeline events={history} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tasks" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground text-center py-8">
                No tasks assigned to this case yet.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
