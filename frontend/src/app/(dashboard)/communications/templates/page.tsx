"use client";

import { useState, useCallback } from "react";
import { type ColumnDef } from "@tanstack/react-table";
import {
  useTemplates,
  useCreateTemplate,
  useUpdateTemplate,
  useDeleteTemplate,
} from "@/hooks/queries/use-communications";
import { PageHeader } from "@/components/layout/page-header";
import { DataTable } from "@/components/shared/data-table/data-table";
import { DataTableColumnHeader } from "@/components/shared/data-table/data-table-column-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { SearchInput } from "@/components/shared/search-input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Plus,
  FileText,
  MoreHorizontal,
  Pencil,
  Trash2,
} from "lucide-react";
import { format } from "date-fns";
import { MessageTemplate, MessageTemplateCreate, MessageChannel } from "@/types/communication";

export default function TemplatesPage() {
  const [search, setSearch] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<MessageTemplate | null>(null);

  const { data, isLoading } = useTemplates({ search });
  const createTemplate = useCreateTemplate();
  const updateTemplate = useUpdateTemplate(editingTemplate?.id ?? "");
  const deleteTemplate = useDeleteTemplate();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingId, setDeletingId] = useState("");

  const [formName, setFormName] = useState("");
  const [formSubject, setFormSubject] = useState("");
  const [formBody, setFormBody] = useState("");
  const [formChannel, setFormChannel] = useState<MessageChannel>("email");
  const [formCategory, setFormCategory] = useState("");

  const templates = data?.items ?? [];

  const openCreateDialog = () => {
    setEditingTemplate(null);
    setFormName("");
    setFormSubject("");
    setFormBody("");
    setFormChannel("email");
    setFormCategory("");
    setDialogOpen(true);
  };

  const openEditDialog = (template: MessageTemplate) => {
    setEditingTemplate(template);
    setFormName(template.name);
    setFormSubject(template.subject);
    setFormBody(template.body);
    setFormChannel(template.channel);
    setFormCategory(template.category);
    setDialogOpen(true);
  };

  const handleSubmit = () => {
    const payload: MessageTemplateCreate = {
      name: formName,
      subject: formSubject,
      body: formBody,
      channel: formChannel,
      category: formCategory,
    };

    if (editingTemplate) {
      updateTemplate.mutate(payload, {
        onSuccess: () => setDialogOpen(false),
      });
    } else {
      createTemplate.mutate(payload, {
        onSuccess: () => setDialogOpen(false),
      });
    }
  };

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
  }, []);

  const columns: ColumnDef<MessageTemplate>[] = [
    {
      accessorKey: "name",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Name" />
      ),
      cell: ({ row }) => (
        <span className="font-medium">{row.getValue("name")}</span>
      ),
    },
    {
      accessorKey: "category",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Category" />
      ),
      cell: ({ row }) => (
        <Badge variant="secondary">{row.getValue("category")}</Badge>
      ),
    },
    {
      accessorKey: "channel",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Channel" />
      ),
      cell: ({ row }) => (
        <Badge variant="outline" className="capitalize">
          {row.getValue("channel")}
        </Badge>
      ),
    },
    {
      accessorKey: "subject",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Subject" />
      ),
      cell: ({ row }) => (
        <span className="text-muted-foreground truncate max-w-[200px] block">
          {row.getValue("subject")}
        </span>
      ),
    },
    {
      accessorKey: "created_at",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Created" />
      ),
      cell: ({ row }) => {
        const date = row.getValue("created_at") as string;
        return date ? format(new Date(date), "MMM d, yyyy") : "-";
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const template = row.original;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => openEditDialog(template)}>
                <Pencil className="mr-2 h-4 w-4" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-destructive"
                onClick={() => {
                  setDeletingId(template.id);
                  setDeleteDialogOpen(true);
                }}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Message Templates"
          description="Create and manage reusable message templates"
        />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Message Templates"
        description="Create and manage reusable message templates"
        actions={
          <Button onClick={openCreateDialog}>
            <Plus className="mr-2 h-4 w-4" />
            New Template
          </Button>
        }
      />

      {templates.length === 0 && !search ? (
        <EmptyState
          icon={FileText}
          title="No templates yet"
          description="Create message templates to streamline your communications."
          actionLabel="Create Template"
          onAction={openCreateDialog}
        />
      ) : (
        <DataTable
          columns={columns}
          data={templates}
          toolbar={
            <SearchInput
              placeholder="Search templates..."
              className="max-w-sm"
              onSearch={handleSearch}
            />
          }
        />
      )}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {editingTemplate ? "Edit Template" : "New Template"}
            </DialogTitle>
            <DialogDescription>
              {editingTemplate
                ? "Update the message template details."
                : "Create a new reusable message template."}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="template-name">Name</Label>
              <Input
                id="template-name"
                placeholder="Template name"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="template-channel">Channel</Label>
                <Select
                  value={formChannel}
                  onValueChange={(v) => setFormChannel(v as MessageChannel)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="in_app">In-App</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-category">Category</Label>
                <Input
                  id="template-category"
                  placeholder="e.g., Reminder, Welcome"
                  value={formCategory}
                  onChange={(e) => setFormCategory(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="template-subject">Subject</Label>
              <Input
                id="template-subject"
                placeholder="Message subject"
                value={formSubject}
                onChange={(e) => setFormSubject(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="template-body">Body</Label>
              <Textarea
                id="template-body"
                placeholder="Message body. Use {{variable}} for dynamic content."
                value={formBody}
                onChange={(e) => setFormBody(e.target.value)}
                rows={6}
              />
              <p className="text-xs text-muted-foreground">
                Use {"{{client_name}}"}, {"{{appointment_date}}"}, etc. for dynamic
                variables.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={
                !formName || !formSubject || !formBody || !formCategory
              }
            >
              {editingTemplate ? "Update Template" : "Create Template"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        title="Delete Template"
        description="Are you sure you want to delete this template? This action cannot be undone."
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={() => {
          deleteTemplate.mutate(deletingId, {
            onSuccess: () => setDeleteDialogOpen(false),
          });
        }}
        loading={deleteTemplate.isPending}
      />
    </div>
  );
}
