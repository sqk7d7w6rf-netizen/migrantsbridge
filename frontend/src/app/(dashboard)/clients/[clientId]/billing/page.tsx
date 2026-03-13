"use client";

import { useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import apiClient from "@/lib/api-client";
import { PageHeader } from "@/components/layout/page-header";
import { DataTable } from "@/components/shared/data-table/data-table";
import { DataTableColumnHeader } from "@/components/shared/data-table/data-table-column-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { INVOICE_STATUSES } from "@/lib/constants";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { SearchInput } from "@/components/shared/search-input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Receipt } from "lucide-react";
import { type ColumnDef } from "@tanstack/react-table";
import { format } from "date-fns";

interface Invoice {
  id: string;
  invoice_number: string;
  client_id: string;
  case_id?: string;
  description: string;
  amount: number;
  status: string;
  due_date: string;
  paid_date?: string;
  created_at: string;
}

const invoiceColumns: ColumnDef<Invoice>[] = [
  {
    accessorKey: "invoice_number",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Invoice #" />
    ),
    cell: ({ row }) => (
      <span className="font-medium">{row.getValue("invoice_number")}</span>
    ),
  },
  {
    accessorKey: "description",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Description" />
    ),
  },
  {
    accessorKey: "amount",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Amount" />
    ),
    cell: ({ row }) => {
      const amount = row.getValue("amount") as number;
      return `$${amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
    },
  },
  {
    accessorKey: "status",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Status" />
    ),
    cell: ({ row }) => (
      <StatusBadge
        status={row.getValue("status") as string}
        statusMap={INVOICE_STATUSES}
      />
    ),
  },
  {
    accessorKey: "due_date",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Due Date" />
    ),
    cell: ({ row }) => {
      const date = row.getValue("due_date") as string;
      return date ? format(new Date(date), "MMM d, yyyy") : "-";
    },
  },
  {
    accessorKey: "paid_date",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Paid Date" />
    ),
    cell: ({ row }) => {
      const date = row.getValue("paid_date") as string;
      return date ? format(new Date(date), "MMM d, yyyy") : "-";
    },
  },
  {
    accessorKey: "created_at",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Created" />
    ),
    cell: ({ row }) => {
      const date = row.getValue("created_at") as string;
      return date ? format(new Date(date), "MMM d, yyyy") : "-";
    },
  },
];

export default function ClientBillingPage() {
  const params = useParams();
  const clientId = params.clientId as string;
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.invoices.list({ client_id: clientId, search }),
    queryFn: async () => {
      const { data } = await apiClient.get("/invoices", {
        params: { client_id: clientId, search },
      });
      return data;
    },
  });

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Billing" description="Client invoices and payments" />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  const allInvoices: Invoice[] = data?.items ?? [];
  const invoices =
    statusFilter === "all"
      ? allInvoices
      : allInvoices.filter((inv) => inv.status === statusFilter);

  const totalAmount = allInvoices.reduce((sum, inv) => sum + inv.amount, 0);
  const paidAmount = allInvoices
    .filter((inv) => inv.status === "paid")
    .reduce((sum, inv) => sum + inv.amount, 0);
  const outstandingAmount = totalAmount - paidAmount;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Billing"
        description="Invoices and payment history"
      />

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">Total Invoiced</p>
          <p className="text-2xl font-bold mt-1">
            ${totalAmount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">Paid</p>
          <p className="text-2xl font-bold mt-1 text-green-600">
            ${paidAmount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </p>
        </div>
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">Outstanding</p>
          <p className="text-2xl font-bold mt-1 text-orange-600">
            ${outstandingAmount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      {allInvoices.length === 0 && !search ? (
        <EmptyState
          icon={Receipt}
          title="No invoices yet"
          description="No invoices have been created for this client."
        />
      ) : (
        <DataTable
          columns={invoiceColumns}
          data={invoices}
          toolbar={
            <div className="flex items-center gap-3">
              <SearchInput
                placeholder="Search invoices..."
                className="max-w-sm"
                onSearch={handleSearch}
              />
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="Payment status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  {Object.entries(INVOICE_STATUSES).map(([key, val]) => (
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
