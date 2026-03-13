"use client";

import { type Invoice, type Payment } from "@/types/invoice";
import { StatusBadge } from "@/components/shared/status-badge";
import { INVOICE_STATUSES } from "@/lib/constants";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { format } from "date-fns";

interface InvoicePreviewProps {
  invoice: Invoice;
  payments?: Payment[];
}

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);

export function InvoicePreview({ invoice, payments = [] }: InvoicePreviewProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <div className="text-2xl font-bold text-primary">
              MigrantsBridge
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Immigration Services & Community Support
            </p>
          </div>
          <div className="text-right">
            <h2 className="text-2xl font-bold">INVOICE</h2>
            <p className="text-sm font-medium mt-1">
              {invoice.invoice_number}
            </p>
            <StatusBadge
              status={invoice.status}
              statusMap={INVOICE_STATUSES}
              className="mt-2"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-muted-foreground mb-1">
              Bill To
            </h4>
            <p className="font-medium">{invoice.client_name || "—"}</p>
          </div>
          <div className="text-right">
            <div className="space-y-1 text-sm">
              <div>
                <span className="text-muted-foreground">Issue Date: </span>
                {format(new Date(invoice.issue_date), "MMM d, yyyy")}
              </div>
              <div>
                <span className="text-muted-foreground">Due Date: </span>
                {format(new Date(invoice.due_date), "MMM d, yyyy")}
              </div>
              {invoice.paid_date && (
                <div>
                  <span className="text-muted-foreground">Paid Date: </span>
                  {format(new Date(invoice.paid_date), "MMM d, yyyy")}
                </div>
              )}
            </div>
          </div>
        </div>

        <Separator />

        <div>
          <div className="grid grid-cols-12 gap-2 py-2 text-sm font-medium text-muted-foreground border-b">
            <div className="col-span-6">Description</div>
            <div className="col-span-2 text-right">Qty</div>
            <div className="col-span-2 text-right">Unit Price</div>
            <div className="col-span-2 text-right">Total</div>
          </div>
          {invoice.line_items.map((item) => (
            <div
              key={item.id}
              className="grid grid-cols-12 gap-2 py-3 text-sm border-b last:border-0"
            >
              <div className="col-span-6">{item.description}</div>
              <div className="col-span-2 text-right">{item.quantity}</div>
              <div className="col-span-2 text-right">
                {formatCurrency(item.unit_price)}
              </div>
              <div className="col-span-2 text-right font-medium">
                {formatCurrency(item.total)}
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-end">
          <div className="w-64 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Subtotal</span>
              <span>{formatCurrency(invoice.subtotal)}</span>
            </div>
            {invoice.tax_rate > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">
                  Tax ({invoice.tax_rate}%)
                </span>
                <span>{formatCurrency(invoice.tax_amount)}</span>
              </div>
            )}
            <Separator />
            <div className="flex justify-between font-bold">
              <span>Total</span>
              <span>{formatCurrency(invoice.total)}</span>
            </div>
            {invoice.amount_paid > 0 && (
              <div className="flex justify-between text-sm text-green-600">
                <span>Amount Paid</span>
                <span>-{formatCurrency(invoice.amount_paid)}</span>
              </div>
            )}
            {invoice.balance_due > 0 && (
              <div className="flex justify-between font-bold text-orange-600">
                <span>Balance Due</span>
                <span>{formatCurrency(invoice.balance_due)}</span>
              </div>
            )}
          </div>
        </div>

        {invoice.notes && (
          <>
            <Separator />
            <div>
              <h4 className="text-sm font-medium text-muted-foreground mb-1">
                Notes
              </h4>
              <p className="text-sm">{invoice.notes}</p>
            </div>
          </>
        )}

        {payments.length > 0 && (
          <>
            <Separator />
            <div>
              <CardTitle className="text-base mb-3">Payment History</CardTitle>
              <div className="space-y-2">
                {payments.map((payment) => (
                  <div
                    key={payment.id}
                    className="flex items-center justify-between rounded-lg border p-3 text-sm"
                  >
                    <div className="flex items-center gap-4">
                      <span className="font-medium">
                        {formatCurrency(payment.amount)}
                      </span>
                      <span className="text-muted-foreground capitalize">
                        {payment.payment_method.replace("_", " ")}
                      </span>
                      {payment.reference_number && (
                        <span className="text-muted-foreground">
                          Ref: {payment.reference_number}
                        </span>
                      )}
                    </div>
                    <span className="text-muted-foreground">
                      {format(new Date(payment.payment_date), "MMM d, yyyy")}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
