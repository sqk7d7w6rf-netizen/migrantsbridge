"use client";

import { useCallback } from "react";
import { useParams } from "next/navigation";
import {
  useThread,
  useSendNotification,
  useTemplates,
} from "@/hooks/queries/use-communications";
import { PageHeader } from "@/components/layout/page-header";
import { ThreadDetail } from "@/components/features/communications/thread-detail";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { MessageChannel } from "@/types/communication";

export default function ThreadDetailPage() {
  const params = useParams();
  const threadId = params.threadId as string;

  const { data: threadDetail, isLoading } = useThread(threadId);
  const { data: templatesData } = useTemplates();
  const sendNotification = useSendNotification();

  const templates = templatesData?.items ?? [];

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

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Conversation" />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  if (!threadDetail) {
    return (
      <div className="space-y-6">
        <PageHeader title="Conversation Not Found" />
        <p className="text-muted-foreground">
          The requested conversation could not be found.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Conversation with ${threadDetail.client_name}`}
        description={threadDetail.subject}
      />
      <div className="rounded-lg border h-[calc(100vh-250px)]">
        <ThreadDetail
          thread={threadDetail}
          messages={threadDetail.messages || []}
          templates={templates}
          onSendMessage={handleSendMessage}
          sendingMessage={sendNotification.isPending}
          showBackButton
        />
      </div>
    </div>
  );
}
