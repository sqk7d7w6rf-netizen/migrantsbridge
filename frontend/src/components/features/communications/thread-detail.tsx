"use client";

import { Message, Thread, MessageChannel, MessageTemplate } from "@/types/communication";
import { MessageComposer } from "./message-composer";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { Mail, MessageSquare, Smartphone, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface ThreadDetailProps {
  thread: Thread;
  messages: Message[];
  templates?: MessageTemplate[];
  onSendMessage: (content: string, channel: MessageChannel, subject?: string) => void;
  sendingMessage?: boolean;
  showBackButton?: boolean;
}

const channelIcons = {
  email: Mail,
  sms: Smartphone,
  in_app: MessageSquare,
};

export function ThreadDetail({
  thread,
  messages,
  templates = [],
  onSendMessage,
  sendingMessage = false,
  showBackButton = false,
}: ThreadDetailProps) {
  const ChannelIcon = channelIcons[thread.channel] || MessageSquare;

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 border-b p-4">
        {showBackButton && (
          <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
            <Link href="/communications">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
        )}
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-muted">
          <ChannelIcon className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-medium">{thread.client_name}</h3>
          <p className="truncate text-xs text-muted-foreground">
            {thread.subject}
          </p>
        </div>
        <Badge
          variant={thread.status === "open" ? "default" : "secondary"}
          className="shrink-0"
        >
          {thread.status}
        </Badge>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-muted-foreground">No messages yet</p>
          </div>
        ) : (
          messages.map((message) => {
            const isStaff = message.sender_type === "staff";
            const isSystem = message.sender_type === "system";

            if (isSystem) {
              return (
                <div key={message.id} className="flex justify-center">
                  <div className="rounded-full bg-muted px-3 py-1">
                    <p className="text-xs text-muted-foreground">
                      {message.content}
                    </p>
                  </div>
                </div>
              );
            }

            return (
              <div
                key={message.id}
                className={cn(
                  "flex",
                  isStaff ? "justify-end" : "justify-start"
                )}
              >
                <div
                  className={cn(
                    "max-w-[70%] space-y-1",
                    isStaff ? "items-end" : "items-start"
                  )}
                >
                  <div
                    className={cn(
                      "rounded-lg px-4 py-2.5",
                      isStaff
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    )}
                  >
                    <p className="text-sm whitespace-pre-wrap">
                      {message.content}
                    </p>
                  </div>
                  <div
                    className={cn(
                      "flex items-center gap-1.5 px-1",
                      isStaff ? "justify-end" : "justify-start"
                    )}
                  >
                    <span className="text-[10px] text-muted-foreground">
                      {message.sender_name}
                    </span>
                    <span className="text-[10px] text-muted-foreground">
                      {format(
                        new Date(message.created_at),
                        "MMM d, h:mm a"
                      )}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="border-t p-4">
        <MessageComposer
          onSend={onSendMessage}
          templates={templates}
          defaultChannel={thread.channel}
          loading={sendingMessage}
          showChannelPicker={false}
        />
      </div>
    </div>
  );
}
