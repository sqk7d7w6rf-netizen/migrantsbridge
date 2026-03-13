"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import apiClient from "@/lib/api-client";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, Mail, Phone, MessageCircle } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

interface Communication {
  id: string;
  client_id: string;
  type: "email" | "phone" | "sms" | "note";
  direction: "inbound" | "outbound";
  subject?: string;
  body: string;
  sender_name: string;
  created_at: string;
}

const typeIcons: Record<string, typeof Mail> = {
  email: Mail,
  phone: Phone,
  sms: MessageCircle,
  note: MessageSquare,
};

const typeColors: Record<string, string> = {
  email: "bg-blue-100 text-blue-800",
  phone: "bg-green-100 text-green-800",
  sms: "bg-purple-100 text-purple-800",
  note: "bg-gray-100 text-gray-800",
};

export default function ClientCommunicationsPage() {
  const params = useParams();
  const clientId = params.clientId as string;

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.communications.list({ client_id: clientId }),
    queryFn: async () => {
      const { data } = await apiClient.get("/communications", {
        params: { client_id: clientId },
      });
      return data;
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Communications"
          description="Message history with this client"
        />
        <LoadingSkeleton variant="card" count={4} />
      </div>
    );
  }

  const communications: Communication[] = data?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Communications"
        description="Message history with this client"
      />

      {communications.length === 0 ? (
        <EmptyState
          icon={MessageSquare}
          title="No communications"
          description="No messages or communications have been recorded for this client."
        />
      ) : (
        <div className="space-y-3">
          {communications.map((comm) => {
            const Icon = typeIcons[comm.type] ?? MessageSquare;
            const colorClass = typeColors[comm.type] ?? "bg-gray-100 text-gray-800";

            return (
              <Card key={comm.id}>
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-start gap-3">
                    <div
                      className={cn(
                        "flex h-9 w-9 shrink-0 items-center justify-center rounded-full",
                        colorClass
                      )}
                    >
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">
                            {comm.sender_name}
                          </span>
                          <Badge variant="outline" className="text-xs capitalize">
                            {comm.type}
                          </Badge>
                          <Badge
                            variant="secondary"
                            className="text-xs capitalize"
                          >
                            {comm.direction}
                          </Badge>
                        </div>
                        <span className="text-xs text-muted-foreground shrink-0">
                          {format(
                            new Date(comm.created_at),
                            "MMM d, yyyy h:mm a"
                          )}
                        </span>
                      </div>
                      {comm.subject && (
                        <p className="text-sm font-medium mt-1">
                          {comm.subject}
                        </p>
                      )}
                      <p className="text-sm text-muted-foreground mt-1 whitespace-pre-wrap line-clamp-3">
                        {comm.body}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
