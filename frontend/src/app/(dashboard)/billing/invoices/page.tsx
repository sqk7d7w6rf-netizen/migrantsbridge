"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { useInvoices } from "@/hooks/queries/use-invoices";
import { PageHeader } from "@/components/layout/page-header";
import { DataTable } from "@/components/shared/data-table/data-table";
import { invoiceColumns } from "@/components/features/billing/invoice-table";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, FileText } from "lucide-react";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { SearchInput } from "@/components/shared/search-input";

export default function InvoicesPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  const { data, isLoading } = useInvoices({
    search,
    status: statusFilter || undefined,
  });

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Invoices" description="Manage your invoices" />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  const invoices = data?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Invoices"
        description="Manage your invoices"
        actions={
          <Button asChild>
            <Link href="/billing/invoices/new">
              <Plus className="mr-2 h-4 w-4" />
              Create Invoice
            </Link>
          </Button>
        }
      />

      {invoices.length === 0 && !search && !statusFilter ? (
        <EmptyState
          icon={FileText}
          title="No invoices yet"
          description="Create your first invoice to start tracking billing."
          actionLabel="Create Invoice"
          onAction={() => {}}
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
              <Select
                value={statusFilter}
                onValueChange={setStatusFilter}
              >
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Statuses</SelectItem>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="sent">Sent</SelectItem>
                  <SelectItem value="paid">Paid</SelectItem>
                  <SelectItem value="overdue">Overdue</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          }
        />
      )}
    </div>
  );
}
