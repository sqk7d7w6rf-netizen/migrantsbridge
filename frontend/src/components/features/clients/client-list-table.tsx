"use client";

import { type ColumnDef } from "@tanstack/react-table";
import { type Client } from "@/types/client";
import { DataTableColumnHeader } from "@/components/shared/data-table/data-table-column-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { IMMIGRATION_STATUSES } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal, Eye, Pencil, Trash2 } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";

export const clientColumns: ColumnDef<Client>[] = [
  {
    accessorKey: "first_name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Name" />
    ),
    cell: ({ row }) => {
      const client = row.original;
      return (
        <Link
          href={`/clients/${client.id}`}
          className="font-medium hover:underline"
        >
          {client.first_name} {client.last_name}
        </Link>
      );
    },
  },
  {
    accessorKey: "email",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Email" />
    ),
  },
  {
    accessorKey: "immigration_status",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Immigration Status" />
    ),
    cell: ({ row }) => {
      const status = row.getValue("immigration_status") as string;
      if (!status) return <span className="text-muted-foreground">-</span>;
      return <StatusBadge status={status} statusMap={IMMIGRATION_STATUSES} />;
    },
  },
  {
    accessorKey: "case_count",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Cases" />
    ),
    cell: ({ row }) => row.getValue("case_count") ?? 0,
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
  {
    id: "actions",
    cell: ({ row }) => {
      const client = row.original;
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link href={`/clients/${client.id}`}>
                <Eye className="mr-2 h-4 w-4" />
                View
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link href={`/clients/${client.id}`}>
                <Pencil className="mr-2 h-4 w-4" />
                Edit
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem className="text-destructive">
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];
