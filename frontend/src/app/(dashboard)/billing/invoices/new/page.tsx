"use client";

import { PageHeader } from "@/components/layout/page-header";
import { InvoiceForm } from "@/components/features/billing/invoice-form";

export default function NewInvoicePage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="New Invoice"
        description="Create a new invoice for a client"
      />
      <InvoiceForm />
    </div>
  );
}
