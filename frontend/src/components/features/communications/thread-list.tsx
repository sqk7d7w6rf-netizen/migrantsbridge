"use client";

import { Thread } from "@/types/communication";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Mail, MessageSquare, Smartphone } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface ThreadListProps {
  threads: Thread[];
  selectedThreadId?: string;
  onSelectThread: (thread: Thread) => void;
}

const channelIcons = {
  email: Mail,
  sms: Smartphone,
  in_app: MessageSquare,
};

export function ThreadList({
  threads,
  selectedThreadId,
  onSelectThread,
}: ThreadListProps) {
  if (threads.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <MessageSquare className="h-8 w-8 text-muted-foreground" />
        <p className="mt-2 text-sm text-muted-foreground">No conversations yet</p>
      </div>
    );
  }

  return (
    <div className="divide-y">
      {threads.map((thread) => {
        const ChannelIcon = channelIcons[thread.channel] || MessageSquare;
        const isSelected = selectedThreadId === thread.id;
        const hasUnread = thread.unread_count > 0;

        return (
          <button
            key={thread.id}
            className={cn(
              "flex w-full items-start gap-3 p-4 text-left hover:bg-accent/50 transition-colors",
              isSelected && "bg-accent",
              hasUnread && "bg-primary/5"
            )}
            onClick={() => onSelectThread(thread)}
          >
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-muted">
              <ChannelIcon className="h-4 w-4 text-muted-foreground" />
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <span
                  className={cn(
                    "truncate text-sm",
                    hasUnread ? "font-semibold" : "font-medium"
                  )}
                >
                  {thread.client_name}
                </span>
                <span className="shrink-0 text-xs text-muted-foreground">
                  {thread.last_message
                    ? formatDistanceToNow(
                        new Date(thread.last_message.created_at),
                        { addSuffix: true }
                      )
                    : formatDistanceToNow(new Date(thread.updated_at), {
                        addSuffix: true,
                      })}
                </span>
              </div>

              <p
                className={cn(
                  "truncate text-xs",
                  hasUnread
                    ? "text-foreground font-medium"
                    : "text-muted-foreground"
                )}
              >
                {thread.subject}
              </p>

              {thread.last_message && (
                <p className="mt-0.5 truncate text-xs text-muted-foreground">
                  {thread.last_message.content}
                </p>
              )}
            </div>

            {hasUnread && (
              <Badge
                variant="default"
                className="shrink-0 rounded-full px-1.5 py-0.5 text-[10px]"
              >
                {thread.unread_count}
              </Badge>
            )}
          </button>
        );
      })}
    </div>
  );
}
