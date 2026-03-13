"use client";

import { useState, useCallback } from "react";
import {
  useThreads,
  useThread,
  useSendNotification,
  useMarkThreadRead,
  useTemplates,
} from "@/hooks/queries/use-communications";
import { PageHeader } from "@/components/layout/page-header";
import { ThreadList } from "@/components/features/communications/thread-list";
import { ThreadDetail } from "@/components/features/communications/thread-detail";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { SearchInput } from "@/components/shared/search-input";
import { Button } from "@/components/ui/button";
import { MessageSquare, Settings, FileText } from "lucide-react";
import { Thread, MessageChannel } from "@/types/communication";
import Link from "next/link";

export default function CommunicationsPage() {
  const [search, setSearch] = useState("");
  const [selectedThreadId, setSelectedThreadId] = useState<string>("");

  const { data: threadsData, isLoading: threadsLoading } = useThreads({
    search,
  });
  const { data: threadDetail } = useThread(selectedThreadId);
  const { data: templatesData } = useTemplates();
  const sendNotification = useSendNotification();
  const markRead = useMarkThreadRead();

  const threads = threadsData?.items ?? [];
  const templates = templatesData?.items ?? [];

  const handleSelectThread = useCallback(
    (thread: Thread) => {
      setSelectedThreadId(thread.id);
      if (thread.unread_count > 0) {
        markRead.mutate(thread.id);
      }
    },
    [markRead]
  );

  const handleSendMessage = useCallback(
    (content: string, channel: MessageChannel, subject?: string) => {
      if (!threadDetail) return;
      sendNotification.mutate({
        thread_id: threadDetail.id,
        client_id: threadDetail.client_id,
        channel,
        subject,
        content,
      });
    },
    [threadDetail, sendNotification]
  );

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
  }, []);

  if (threadsLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Communications"
          description="Manage client communications"
        />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Communications"
        description="Manage client communications"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/communications/templates">
                <FileText className="mr-2 h-4 w-4" />
                Templates
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/communications/settings">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </Link>
            </Button>
          </div>
        }
      />

      {threads.length === 0 && !search ? (
        <EmptyState
          icon={MessageSquare}
          title="No conversations yet"
          description="Communications with clients will appear here."
        />
      ) : (
        <div className="grid grid-cols-1 gap-0 overflow-hidden rounded-lg border lg:grid-cols-3">
          <div className="border-r lg:col-span-1">
            <div className="border-b p-3">
              <SearchInput
                placeholder="Search conversations..."
                onSearch={handleSearch}
                className="w-full"
              />
            </div>
            <div className="max-h-[calc(100vh-280px)] overflow-y-auto">
              <ThreadList
                threads={threads}
                selectedThreadId={selectedThreadId}
                onSelectThread={handleSelectThread}
              />
            </div>
          </div>

          <div className="hidden lg:col-span-2 lg:block">
            {selectedThreadId && threadDetail ? (
              <div className="h-[calc(100vh-280px)]">
                <ThreadDetail
                  thread={threadDetail}
                  messages={threadDetail.messages || []}
                  templates={templates}
                  onSendMessage={handleSendMessage}
                  sendingMessage={sendNotification.isPending}
                />
              </div>
            ) : (
              <div className="flex h-[calc(100vh-280px)] items-center justify-center">
                <div className="text-center">
                  <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Select a conversation to view messages
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="lg:hidden">
            {threads.length > 0 && !selectedThreadId && (
              <p className="p-4 text-sm text-muted-foreground text-center">
                Tap a conversation to view it
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
