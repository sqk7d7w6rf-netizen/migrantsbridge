"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Plus, Trash2 } from "lucide-react";
import { useCreateInvoice } from "@/hooks/queries/use-invoices";
import { useClients } from "@/hooks/queries/use-clients";
import { useServiceFees } from "@/hooks/queries/use-invoices";

interface LineItemInput {
  description: string;
  quantity: number;
  unit_price: number;
}

export function InvoiceForm() {
  const router = useRouter();
  const createInvoice = useCreateInvoice();
  const { data: clientsData } = useClients();
  const { data: serviceFees } = useServiceFees();

  const [clientId, setClientId] = useState("");
  const [caseId, setCaseId] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [notes, setNotes] = useState("");
  const [taxRate, setTaxRate] = useState("0");
  const [isProBono, setIsProBono] = useState(false);
  const [lineItems, setLineItems] = useState<LineItemInput[]>([
    { description: "", quantity: 1, unit_price: 0 },
  ]);

  const clients = clientsData?.items ?? [];

  const addLineItem = () => {
    setLineItems([
      ...lineItems,
      { description: "", quantity: 1, unit_price: 0 },
    ]);
  };

  const removeLineItem = (index: number) => {
    if (lineItems.length === 1) return;
    setLineItems(lineItems.filter((_, i) => i !== index));
  };

  const updateLineItem = (
    index: number,
    field: keyof LineItemInput,
    value: string | number
  ) => {
    const updated = [...lineItems];
    updated[index] = { ...updated[index], [field]: value };
    setLineItems(updated);
  };

  const applyServiceFee = (feeId: string) => {
    const fee = serviceFees?.find((f) => f.id === feeId);
    if (fee) {
      setLineItems([
        ...lineItems,
        {
          description: fee.name,
          quantity: 1,
          unit_price: fee.amount,
        },
      ]);
    }
  };

  const subtotal = lineItems.reduce(
    (sum, item) => sum + item.quantity * item.unit_price,
    0
  );
  const taxAmount = subtotal * (parseFloat(taxRate) / 100);
  const total = isProBono ? 0 : subtotal + taxAmount;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await createInvoice.mutateAsync({
      client_id: clientId,
      case_id: caseId || undefined,
      due_date: dueDate,
      line_items: lineItems.map((item) => ({
        description: item.description,
        quantity: item.quantity,
        unit_price: item.unit_price,
      })),
      notes: notes || undefined,
      tax_rate: parseFloat(taxRate),
      is_pro_bono: isProBono,
    });

    router.push("/billing/invoices");
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Invoice Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="client">Client</Label>
                <Select value={clientId} onValueChange={setClientId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a client" />
                  </SelectTrigger>
                  <SelectContent>
                    {clients.map((client) => (
                      <SelectItem key={client.id} value={client.id}>
                        {client.first_name} {client.last_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="case">Case (Optional)</Label>
                <Input
                  id="case"
                  placeholder="Enter case ID"
                  value={caseId}
                  onChange={(e) => setCaseId(e.target.value)}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="due_date">Due Date</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tax_rate">Tax Rate (%)</Label>
                <Input
                  id="tax_rate"
                  type="number"
                  step="0.01"
                  min="0"
                  value={taxRate}
                  onChange={(e) => setTaxRate(e.target.value)}
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="pro_bono"
                checked={isProBono}
                onChange={(e) => setIsProBono(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <Label htmlFor="pro_bono">Pro Bono (no charge)</Label>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Line Items</CardTitle>
              <div className="flex gap-2">
                {serviceFees && serviceFees.length > 0 && (
                  <Select onValueChange={applyServiceFee}>
                    <SelectTrigger className="w-[200px]">
                      <SelectValue placeholder="Add service fee" />
                    </SelectTrigger>
                    <SelectContent>
                      {serviceFees
                        .filter((f) => f.is_active)
                        .map((fee) => (
                          <SelectItem key={fee.id} value={fee.id}>
                            {fee.name} - ${fee.amount}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                )}
                <Button type="button" variant="outline" onClick={addLineItem}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Item
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="grid grid-cols-12 gap-3 text-sm font-medium text-muted-foreground">
                <div className="col-span-6">Description</div>
                <div className="col-span-2">Quantity</div>
                <div className="col-span-2">Unit Price</div>
                <div className="col-span-1 text-right">Total</div>
                <div className="col-span-1" />
              </div>
              {lineItems.map((item, index) => (
                <div key={index} className="grid grid-cols-12 gap-3 items-center">
                  <div className="col-span-6">
                    <Input
                      placeholder="Description"
                      value={item.description}
                      onChange={(e) =>
                        updateLineItem(index, "description", e.target.value)
                      }
                      required
                    />
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) =>
                        updateLineItem(
                          index,
                          "quantity",
                          parseInt(e.target.value) || 0
                        )
                      }
                      required
                    />
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      value={item.unit_price}
                      onChange={(e) =>
                        updateLineItem(
                          index,
                          "unit_price",
                          parseFloat(e.target.value) || 0
                        )
                      }
                      required
                    />
                  </div>
                  <div className="col-span-1 text-right text-sm font-medium">
                    ${(item.quantity * item.unit_price).toFixed(2)}
                  </div>
                  <div className="col-span-1 text-right">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeLineItem(index)}
                      disabled={lineItems.length === 1}
                    >
                      <Trash2 className="h-4 w-4 text-muted-foreground" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
          <CardFooter className="flex-col items-end space-y-1 border-t pt-4">
            <div className="text-sm text-muted-foreground">
              Subtotal: ${subtotal.toFixed(2)}
            </div>
            {parseFloat(taxRate) > 0 && (
              <div className="text-sm text-muted-foreground">
                Tax ({taxRate}%): ${taxAmount.toFixed(2)}
              </div>
            )}
            <div className="text-lg font-bold">
              Total: ${total.toFixed(2)}
              {isProBono && (
                <span className="ml-2 text-sm font-normal text-green-600">
                  (Pro Bono)
                </span>
              )}
            </div>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="Additional notes or terms..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={createInvoice.isPending}>
            {createInvoice.isPending ? "Creating..." : "Create Invoice"}
          </Button>
        </div>
      </div>
    </form>
  );
}
