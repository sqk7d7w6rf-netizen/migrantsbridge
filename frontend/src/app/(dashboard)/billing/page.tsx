"use client";

import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { FinancialSummaryCards } from "@/components/features/billing/financial-summary-cards";
import { DataTable } from "@/components/shared/data-table/data-table";
import { invoiceColumns } from "@/components/features/billing/invoice-table";
import { useInvoices, usePayments } from "@/hooks/queries/use-invoices";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Plus, ArrowRight } from "lucide-react";
import { format } from "date-fns";

export default function BillingPage() {
  const { data: invoicesData, isLoading: invoicesLoading } = useInvoices({
    page_size: 5,
  });
  const { data: paymentsData, isLoading: paymentsLoading } = usePayments({
    page_size: 5,
  });

  const invoices = invoicesData?.items ?? [];
  const payments = paymentsData?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Billing"
        description="Financial overview and billing management"
        actions={
          <Button asChild>
            <Link href="/billing/invoices/new">
              <Plus className="mr-2 h-4 w-4" />
              New Invoice
            </Link>
          </Button>
        }
      />

      <FinancialSummaryCards />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-base">Recent Invoices</CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/billing/invoices">
                View All
                <ArrowRight className="ml-1 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {invoicesLoading ? (
              <LoadingSkeleton variant="table" />
            ) : (
              <DataTable columns={invoiceColumns} data={invoices} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-base">Recent Payments</CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/billing/payments">
                View All
                <ArrowRight className="ml-1 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {paymentsLoading ? (
              <LoadingSkeleton variant="table" />
            ) : payments.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                No recent payments
              </p>
            ) : (
              <div className="space-y-3">
                {payments.map((payment) => (
                  <div
                    key={payment.id}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div>
                      <p className="text-sm font-medium">
                        {new Intl.NumberFormat("en-US", {
                          style: "currency",
                          currency: "USD",
                        }).format(payment.amount)}
                      </p>
                      <p className="text-xs text-muted-foreground capitalize">
                        {payment.payment_method.replace("_", " ")}
                        {payment.reference_number &&
                          ` - ${payment.reference_number}`}
                      </p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(payment.payment_date), "MMM d, yyyy")}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
