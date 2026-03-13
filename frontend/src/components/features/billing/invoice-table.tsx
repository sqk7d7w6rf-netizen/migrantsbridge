"use client";

import { type ColumnDef } from "@tanstack/react-table";
import { type Invoice } from "@/types/invoice";
import { DataTableColumnHeader } from "@/components/shared/data-table/data-table-column-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { INVOICE_STATUSES } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  MoreHorizontal,
  Eye,
  Send,
  CreditCard,
  XCircle,
} from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";

export const invoiceColumns: ColumnDef<Invoice>[] = [
  {
    accessorKey: "invoice_number",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Invoice #" />
    ),
    cell: ({ row }) => {
      const invoice = row.original;
      return (
        <Link
          href={`/billing/invoices/${invoice.id}`}
          className="font-medium hover:underline"
        >
          {invoice.invoice_number}
        </Link>
      );
    },
  },
  {
    accessorKey: "client_name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Client" />
    ),
    cell: ({ row }) => {
      return row.getValue("client_name") || "-";
    },
  },
  {
    accessorKey: "total",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Amount" />
    ),
    cell: ({ row }) => {
      const amount = row.getValue("total") as number;
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount);
    },
  },
  {
    accessorKey: "balance_due",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Balance Due" />
    ),
    cell: ({ row }) => {
      const balance = row.getValue("balance_due") as number;
      return (
        <span className={balance > 0 ? "text-orange-600 font-medium" : ""}>
          {new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
          }).format(balance)}
        </span>
      );
    },
  },
  {
    accessorKey: "status",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Status" />
    ),
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return <StatusBadge status={status} statusMap={INVOICE_STATUSES} />;
    },
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
    id: "actions",
    cell: ({ row }) => {
      const invoice = row.original;
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link href={`/billing/invoices/${invoice.id}`}>
                <Eye className="mr-2 h-4 w-4" />
                View
              </Link>
            </DropdownMenuItem>
            {invoice.status === "draft" && (
              <DropdownMenuItem asChild>
                <Link href={`/billing/invoices/${invoice.id}?action=send`}>
                  <Send className="mr-2 h-4 w-4" />
                  Send
                </Link>
              </DropdownMenuItem>
            )}
            {(invoice.status === "sent" || invoice.status === "overdue") && (
              <DropdownMenuItem asChild>
                <Link href={`/billing/invoices/${invoice.id}?action=payment`}>
                  <CreditCard className="mr-2 h-4 w-4" />
                  Record Payment
                </Link>
              </DropdownMenuItem>
            )}
            <DropdownMenuSeparator />
            {invoice.status !== "cancelled" && invoice.status !== "paid" && (
              <DropdownMenuItem className="text-destructive">
                <XCircle className="mr-2 h-4 w-4" />
                Cancel
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];
