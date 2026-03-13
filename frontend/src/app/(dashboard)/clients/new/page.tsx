"use client";

import { useRouter } from "next/navigation";
import { PageHeader } from "@/components/layout/page-header";
import { ClientForm } from "@/components/features/clients/client-form";
import { useCreateClient } from "@/hooks/queries/use-clients";
import { type ClientFormInput } from "@/lib/validations/client";

export default function NewClientPage() {
  const router = useRouter();
  const createClient = useCreateClient();

  const handleSubmit = async (data: ClientFormInput) => {
    await createClient.mutateAsync(data as unknown as Parameters<typeof createClient.mutateAsync>[0]);
    router.push("/clients");
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <PageHeader
        title="New Client"
        description="Add a new client to the system"
      />
      <ClientForm
        onSubmit={handleSubmit}
        isLoading={createClient.isPending}
        submitLabel="Create Client"
      />
    </div>
  );
}
