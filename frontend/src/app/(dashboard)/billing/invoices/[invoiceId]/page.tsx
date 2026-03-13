"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { PageHeader } from "@/components/layout/page-header";
import { InvoicePreview } from "@/components/features/billing/invoice-preview";
import { PaymentForm } from "@/components/features/billing/payment-form";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import {
  useInvoice,
  useInvoicePayments,
  useSendInvoice,
  useCancelInvoice,
} from "@/hooks/queries/use-invoices";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { Button } from "@/components/ui/button";
import { Send, CreditCard, XCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function InvoiceDetailPage() {
  const params = useParams();
  const invoiceId = params.invoiceId as string;

  const { data: invoice, isLoading } = useInvoice(invoiceId);
  const { data: payments } = useInvoicePayments(invoiceId);
  const sendInvoice = useSendInvoice();
  const cancelInvoice = useCancelInvoice();

  const [paymentOpen, setPaymentOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);

  if (isLoading || !invoice) {
    return (
      <div className="space-y-6">
        <PageHeader title="Invoice" description="Loading invoice details..." />
        <LoadingSkeleton variant="card" />
      </div>
    );
  }

  const handleSend = async () => {
    await sendInvoice.mutateAsync(invoiceId);
  };

  const handleCancel = async () => {
    await cancelInvoice.mutateAsync(invoiceId);
    setCancelOpen(false);
  };

  const canSend = invoice.status === "draft";
  const canRecordPayment =
    invoice.status === "sent" || invoice.status === "overdue";
  const canCancel =
    invoice.status !== "cancelled" && invoice.status !== "paid";

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Invoice ${invoice.invoice_number}`}
        description={`Invoice for ${invoice.client_name || "client"}`}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/billing/invoices">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Link>
            </Button>
            {canSend && (
              <Button
                onClick={handleSend}
                disabled={sendInvoice.isPending}
              >
                <Send className="mr-2 h-4 w-4" />
                {sendInvoice.isPending ? "Sending..." : "Send Invoice"}
              </Button>
            )}
            {canRecordPayment && (
              <Button onClick={() => setPaymentOpen(true)}>
                <CreditCard className="mr-2 h-4 w-4" />
                Record Payment
              </Button>
            )}
            {canCancel && (
              <Button
                variant="destructive"
                onClick={() => setCancelOpen(true)}
              >
                <XCircle className="mr-2 h-4 w-4" />
                Cancel Invoice
              </Button>
            )}
          </div>
        }
      />

      <InvoicePreview invoice={invoice} payments={payments ?? []} />

      <PaymentForm
        open={paymentOpen}
        onOpenChange={setPaymentOpen}
        invoiceId={invoiceId}
        balanceDue={invoice.balance_due}
      />

      <ConfirmDialog
        open={cancelOpen}
        onOpenChange={setCancelOpen}
        title="Cancel Invoice"
        description="Are you sure you want to cancel this invoice? This action cannot be undone."
        confirmLabel="Cancel Invoice"
        variant="destructive"
        onConfirm={handleCancel}
        loading={cancelInvoice.isPending}
      />
    </div>
  );
}
