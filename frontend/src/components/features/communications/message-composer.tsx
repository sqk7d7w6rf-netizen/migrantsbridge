"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MessageChannel, MessageTemplate } from "@/types/communication";
import { TemplateSelector } from "./template-selector";
import { FileText, Send } from "lucide-react";

interface MessageComposerProps {
  onSend: (content: string, channel: MessageChannel, subject?: string) => void;
  templates?: MessageTemplate[];
  defaultChannel?: MessageChannel;
  placeholder?: string;
  loading?: boolean;
  showChannelPicker?: boolean;
  showSubject?: boolean;
}

export function MessageComposer({
  onSend,
  templates = [],
  defaultChannel = "email",
  placeholder = "Type your message...",
  loading = false,
  showChannelPicker = true,
  showSubject = false,
}: MessageComposerProps) {
  const [content, setContent] = useState("");
  const [subject, setSubject] = useState("");
  const [channel, setChannel] = useState<MessageChannel>(defaultChannel);
  const [templateSelectorOpen, setTemplateSelectorOpen] = useState(false);

  const handleSend = () => {
    if (!content.trim()) return;
    onSend(content, channel, showSubject ? subject : undefined);
    setContent("");
    setSubject("");
  };

  const handleTemplateSelect = (template: MessageTemplate) => {
    setContent(template.body);
    if (template.subject) {
      setSubject(template.subject);
    }
    setChannel(template.channel);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="space-y-3 rounded-lg border p-3">
      {showSubject && channel === "email" && (
        <input
          type="text"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          placeholder="Subject"
          className="w-full border-b bg-transparent px-1 pb-2 text-sm outline-none placeholder:text-muted-foreground"
        />
      )}

      <Textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={4}
        className="resize-none border-0 p-0 shadow-none focus-visible:ring-0"
      />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {showChannelPicker && (
            <Select
              value={channel}
              onValueChange={(v) => setChannel(v as MessageChannel)}
            >
              <SelectTrigger className="h-8 w-[120px] text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="sms">SMS</SelectItem>
                <SelectItem value="in_app">In-App</SelectItem>
              </SelectContent>
            </Select>
          )}

          {templates.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 text-xs"
              onClick={() => setTemplateSelectorOpen(true)}
            >
              <FileText className="mr-1 h-3.5 w-3.5" />
              Templates
            </Button>
          )}
        </div>

        <Button
          size="sm"
          onClick={handleSend}
          disabled={!content.trim() || loading}
          className="h-8"
        >
          {loading ? (
            "Sending..."
          ) : (
            <>
              <Send className="mr-1 h-3.5 w-3.5" />
              Send
            </>
          )}
        </Button>
      </div>

      <TemplateSelector
        open={templateSelectorOpen}
        onOpenChange={setTemplateSelectorOpen}
        templates={templates}
        onSelect={handleTemplateSelect}
      />
    </div>
  );
}
