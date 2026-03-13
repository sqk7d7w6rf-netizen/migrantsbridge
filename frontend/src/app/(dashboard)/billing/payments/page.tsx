"use client";

import { useState, useCallback } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { DataTable } from "@/components/shared/data-table/data-table";
import { usePayments } from "@/hooks/queries/use-invoices";
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
import { type ColumnDef } from "@tanstack/react-table";
import { type Payment } from "@/types/invoice";
import { DataTableColumnHeader } from "@/components/shared/data-table/data-table-column-header";
import { format } from "date-fns";
import { CreditCard } from "lucide-react";
import Link from "next/link";

const paymentColumns: ColumnDef<Payment>[] = [
  {
    accessorKey: "payment_date",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Date" />
    ),
    cell: ({ row }) => {
      const date = row.getValue("payment_date") as string;
      return date ? format(new Date(date), "MMM d, yyyy") : "-";
    },
  },
  {
    accessorKey: "invoice_id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Invoice" />
    ),
    cell: ({ row }) => {
      const invoiceId = row.getValue("invoice_id") as string;
      return (
        <Link
          href={`/billing/invoices/${invoiceId}`}
          className="font-medium hover:underline"
        >
          {invoiceId.slice(0, 8)}...
        </Link>
      );
    },
  },
  {
    accessorKey: "amount",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Amount" />
    ),
    cell: ({ row }) => {
      const amount = row.getValue("amount") as number;
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount);
    },
  },
  {
    accessorKey: "payment_method",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Method" />
    ),
    cell: ({ row }) => {
      const method = row.getValue("payment_method") as string;
      return (
        <span className="capitalize">{method.replace("_", " ")}</span>
      );
    },
  },
  {
    accessorKey: "reference_number",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Reference" />
    ),
    cell: ({ row }) => row.getValue("reference_number") || "-",
  },
  {
    accessorKey: "notes",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Notes" />
    ),
    cell: ({ row }) => {
      const notes = row.getValue("notes") as string;
      return notes ? (
        <span className="truncate max-w-[200px] block">{notes}</span>
      ) : (
        "-"
      );
    },
  },
];

export default function PaymentsPage() {
  const [search, setSearch] = useState("");
  const [methodFilter, setMethodFilter] = useState<string>("");

  const { data, isLoading } = usePayments({
    search,
    payment_method: methodFilter || undefined,
  });

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Payments"
          description="Payment history and records"
        />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  const payments = data?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Payments"
        description="Payment history and records"
      />

      {payments.length === 0 && !search && !methodFilter ? (
        <EmptyState
          icon={CreditCard}
          title="No payments recorded"
          description="Payments will appear here when they are recorded against invoices."
        />
      ) : (
        <DataTable
          columns={paymentColumns}
          data={payments}
          toolbar={
            <div className="flex items-center gap-3">
              <SearchInput
                placeholder="Search payments..."
                className="max-w-sm"
                onSearch={handleSearch}
              />
              <Select
                value={methodFilter}
                onValueChange={setMethodFilter}
              >
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="All Methods" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Methods</SelectItem>
                  <SelectItem value="cash">Cash</SelectItem>
                  <SelectItem value="check">Check</SelectItem>
                  <SelectItem value="credit_card">Credit Card</SelectItem>
                  <SelectItem value="bank_transfer">Bank Transfer</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          }
        />
      )}
    </div>
  );
}
