"use client";

import { useState } from "react";
import { MessageTemplate } from "@/types/communication";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { FileText, Search } from "lucide-react";
import { cn } from "@/lib/utils";

interface TemplateSelectorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  templates: MessageTemplate[];
  onSelect: (template: MessageTemplate) => void;
}

export function TemplateSelector({
  open,
  onOpenChange,
  templates,
  onSelect,
}: TemplateSelectorProps) {
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const filtered = templates.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.category.toLowerCase().includes(search.toLowerCase()) ||
      t.subject.toLowerCase().includes(search.toLowerCase())
  );

  const selectedTemplate = templates.find((t) => t.id === selectedId);

  const handleConfirm = () => {
    if (selectedTemplate) {
      onSelect(selectedTemplate);
      onOpenChange(false);
      setSelectedId(null);
      setSearch("");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Select Message Template</DialogTitle>
          <DialogDescription>
            Choose a template to pre-fill your message.
          </DialogDescription>
        </DialogHeader>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="grid grid-cols-2 gap-2 max-h-[300px] overflow-y-auto">
          <div className="space-y-1">
            {filtered.length === 0 ? (
              <p className="p-4 text-sm text-muted-foreground text-center">
                No templates found
              </p>
            ) : (
              filtered.map((template) => (
                <button
                  key={template.id}
                  className={cn(
                    "flex w-full items-start gap-2 rounded-md border p-3 text-left transition-colors hover:bg-accent",
                    selectedId === template.id &&
                      "border-primary bg-primary/5"
                  )}
                  onClick={() => setSelectedId(template.id)}
                >
                  <FileText className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">
                      {template.name}
                    </p>
                    <div className="flex items-center gap-1 mt-0.5">
                      <Badge variant="secondary" className="text-[10px] px-1">
                        {template.category}
                      </Badge>
                      <Badge variant="outline" className="text-[10px] px-1">
                        {template.channel}
                      </Badge>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>

          <div className="rounded-md border p-4">
            {selectedTemplate ? (
              <div className="space-y-3">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase">
                    Subject
                  </p>
                  <p className="text-sm">{selectedTemplate.subject}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase">
                    Body
                  </p>
                  <p className="text-sm whitespace-pre-wrap">
                    {selectedTemplate.body}
                  </p>
                </div>
                {selectedTemplate.variables.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase">
                      Variables
                    </p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedTemplate.variables.map((v) => (
                        <Badge key={v} variant="outline" className="text-xs">
                          {`{{${v}}}`}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                Select a template to preview
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={!selectedId}>
            Use Template
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
