"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { useClients } from "@/hooks/queries/use-clients";
import { PageHeader } from "@/components/layout/page-header";
import { DataTable } from "@/components/shared/data-table/data-table";
import { clientColumns } from "@/components/features/clients/client-list-table";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { Users } from "lucide-react";
import { SearchInput } from "@/components/shared/search-input";

export default function ClientsPage() {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useClients({ search });

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Clients" description="Manage your client database" />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  const clients = data?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Clients"
        description="Manage your client database"
        actions={
          <Button asChild>
            <Link href="/clients/new">
              <Plus className="mr-2 h-4 w-4" />
              New Client
            </Link>
          </Button>
        }
      />

      {clients.length === 0 && !search ? (
        <EmptyState
          icon={Users}
          title="No clients yet"
          description="Get started by adding your first client to the system."
          actionLabel="Add Client"
          onAction={() => {}}
        />
      ) : (
        <DataTable
          columns={clientColumns}
          data={clients}
          toolbar={
            <SearchInput
              placeholder="Search clients by name or email..."
              className="max-w-sm"
              onSearch={handleSearch}
            />
          }
        />
      )}
    </div>
  );
}
