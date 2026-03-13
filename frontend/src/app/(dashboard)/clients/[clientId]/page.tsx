"use client";

import { useParams } from "next/navigation";
import { useClient } from "@/hooks/queries/use-clients";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { StatusBadge } from "@/components/shared/status-badge";
import { IMMIGRATION_STATUSES } from "@/lib/constants";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Pencil, Mail, Phone } from "lucide-react";
import { format } from "date-fns";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";

export default function ClientDetailPage() {
  const params = useParams();
  const clientId = params.clientId as string;
  const { data: client, isLoading } = useClient(clientId);

  if (isLoading) {
    return <LoadingSkeleton variant="detail" />;
  }

  if (!client) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Client not found</p>
      </div>
    );
  }

  const initials = `${client.first_name[0]}${client.last_name[0]}`.toUpperCase();

  return (
    <div className="space-y-6">
      <PageHeader
        title={`${client.first_name} ${client.last_name}`}
        description={`Client since ${format(new Date(client.created_at), "MMMM yyyy")}`}
        actions={
          <Button variant="outline">
            <Pencil className="mr-2 h-4 w-4" />
            Edit
          </Button>
        }
      />

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-1">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center text-center">
              <Avatar className="h-20 w-20">
                <AvatarFallback className="text-xl">{initials}</AvatarFallback>
              </Avatar>
              <h3 className="mt-4 text-lg font-semibold">
                {client.first_name} {client.last_name}
              </h3>
              {client.immigration_status && (
                <div className="mt-2">
                  <StatusBadge
                    status={client.immigration_status}
                    statusMap={IMMIGRATION_STATUSES}
                  />
                </div>
              )}
              <Separator className="my-4" />
              <div className="w-full space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span>{client.email}</span>
                </div>
                {client.phone_numbers?.[0] && (
                  <div className="flex items-center gap-2">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span>{client.phone_numbers[0].number}</span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-muted-foreground">Nationality</dt>
                <dd className="font-medium">
                  {client.nationality || "Not specified"}
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Date of Birth</dt>
                <dd className="font-medium">
                  {client.date_of_birth
                    ? format(new Date(client.date_of_birth), "MMM d, yyyy")
                    : "Not specified"}
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Active Cases</dt>
                <dd className="font-medium">{client.case_count ?? 0}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Assigned To</dt>
                <dd className="font-medium">
                  {client.assigned_to_name || "Unassigned"}
                </dd>
              </div>
              {client.address && (
                <div className="col-span-2">
                  <dt className="text-muted-foreground">Address</dt>
                  <dd className="font-medium">
                    {client.address.street}, {client.address.city},{" "}
                    {client.address.state} {client.address.zip_code},{" "}
                    {client.address.country}
                  </dd>
                </div>
              )}
              {client.languages && client.languages.length > 0 && (
                <div className="col-span-2">
                  <dt className="text-muted-foreground mb-1">Languages</dt>
                  <dd className="flex flex-wrap gap-1">
                    {client.languages.map((lang) => (
                      <Badge key={lang.language} variant="secondary">
                        {lang.language} ({lang.proficiency})
                      </Badge>
                    ))}
                  </dd>
                </div>
              )}
              {client.tags && client.tags.length > 0 && (
                <div className="col-span-2">
                  <dt className="text-muted-foreground mb-1">Tags</dt>
                  <dd className="flex flex-wrap gap-1">
                    {client.tags.map((tag) => (
                      <Badge key={tag} variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </dd>
                </div>
              )}
              {client.notes && (
                <div className="col-span-2">
                  <dt className="text-muted-foreground">Notes</dt>
                  <dd className="font-medium whitespace-pre-wrap">
                    {client.notes}
                  </dd>
                </div>
              )}
            </dl>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
