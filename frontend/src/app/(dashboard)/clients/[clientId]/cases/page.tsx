"use client";

import { useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useCases } from "@/hooks/queries/use-cases";
import { PageHeader } from "@/components/layout/page-header";
import { DataTable } from "@/components/shared/data-table/data-table";
import { DataTableColumnHeader } from "@/components/shared/data-table/data-table-column-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { CASE_STATUSES, PRIORITIES } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Briefcase } from "lucide-react";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { SearchInput } from "@/components/shared/search-input";
import { type ColumnDef } from "@tanstack/react-table";
import { type Case } from "@/types/case";
import { format } from "date-fns";

const caseColumns: ColumnDef<Case>[] = [
  {
    accessorKey: "case_number",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Case #" />
    ),
    cell: ({ row }) => {
      const c = row.original;
      return (
        <Link
          href={`/clients/${c.client_id}/cases/${c.id}`}
          className="font-medium hover:underline"
        >
          {c.case_number}
        </Link>
      );
    },
  },
  {
    accessorKey: "title",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Title" />
    ),
  },
  {
    accessorKey: "case_type",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Type" />
    ),
  },
  {
    accessorKey: "status",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Status" />
    ),
    cell: ({ row }) => (
      <StatusBadge
        status={row.getValue("status") as string}
        statusMap={CASE_STATUSES}
      />
    ),
  },
  {
    accessorKey: "priority",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Priority" />
    ),
    cell: ({ row }) => (
      <StatusBadge
        status={row.getValue("priority") as string}
        statusMap={PRIORITIES}
      />
    ),
  },
  {
    accessorKey: "assigned_to_name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Assigned To" />
    ),
    cell: ({ row }) => row.getValue("assigned_to_name") || "Unassigned",
  },
  {
    accessorKey: "opened_date",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Opened" />
    ),
    cell: ({ row }) => {
      const date = row.getValue("opened_date") as string;
      return date ? format(new Date(date), "MMM d, yyyy") : "-";
    },
  },
];

export default function ClientCasesPage() {
  const params = useParams();
  const clientId = params.clientId as string;
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const { data, isLoading } = useCases({ client_id: clientId, search });

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Cases" description="Client cases" />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  const allCases = data?.items ?? [];
  const cases =
    statusFilter === "all"
      ? allCases
      : allCases.filter((c) => c.status === statusFilter);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Cases"
        description="Manage cases for this client"
        actions={
          <Button asChild>
            <Link href={`/clients/${clientId}/cases/new`}>
              <Plus className="mr-2 h-4 w-4" />
              New Case
            </Link>
          </Button>
        }
      />

      {allCases.length === 0 && !search ? (
        <EmptyState
          icon={Briefcase}
          title="No cases yet"
          description="Get started by creating a new case for this client."
          actionLabel="Create Case"
          onAction={() => {}}
        />
      ) : (
        <DataTable
          columns={caseColumns}
          data={cases}
          toolbar={
            <div className="flex items-center gap-3">
              <SearchInput
                placeholder="Search cases..."
                className="max-w-sm"
                onSearch={handleSearch}
              />
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  {Object.entries(CASE_STATUSES).map(([key, val]) => (
                    <SelectItem key={key} value={key}>
                      {val.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          }
        />
      )}
    </div>
  );
}
