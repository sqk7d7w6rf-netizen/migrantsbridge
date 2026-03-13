"use client";

import Link from "next/link";
import { Case } from "@/types/case";
import { StatusBadge } from "@/components/shared/status-badge";
import { CASE_STATUSES, PRIORITIES } from "@/lib/constants";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Calendar, User } from "lucide-react";
import { format } from "date-fns";

interface CaseCardProps {
  caseItem: Case;
  clientId: string;
}

export function CaseCard({ caseItem, clientId }: CaseCardProps) {
  return (
    <Link href={`/clients/${clientId}/cases/${caseItem.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-muted-foreground">
                {caseItem.case_number}
              </p>
              <CardTitle className="text-base mt-1">{caseItem.title}</CardTitle>
            </div>
            <StatusBadge
              status={caseItem.status}
              statusMap={CASE_STATUSES}
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">{caseItem.case_type}</span>
              <StatusBadge
                status={caseItem.priority}
                statusMap={PRIORITIES}
              />
            </div>
            <div className="flex items-center gap-4 text-muted-foreground text-xs mt-1">
              {caseItem.assigned_to_name && (
                <div className="flex items-center gap-1">
                  <User className="h-3 w-3" />
                  <span>{caseItem.assigned_to_name}</span>
                </div>
              )}
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                <span>
                  {format(new Date(caseItem.opened_date), "MMM d, yyyy")}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
