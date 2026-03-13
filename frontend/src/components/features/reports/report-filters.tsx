"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CalendarDays, RotateCcw } from "lucide-react";

interface ReportFiltersProps {
  onDateRangeChange: (dateFrom: string, dateTo: string) => void;
  additionalFilters?: {
    label: string;
    options: { value: string; label: string }[];
    onChange: (value: string) => void;
  }[];
}

export function ReportFilters({
  onDateRangeChange,
  additionalFilters,
}: ReportFiltersProps) {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const handleApply = () => {
    onDateRangeChange(dateFrom, dateTo);
  };

  const handleReset = () => {
    setDateFrom("");
    setDateTo("");
    onDateRangeChange("", "");
  };

  return (
    <div className="flex flex-wrap items-end gap-4 rounded-lg border p-4">
      <div className="space-y-1">
        <Label className="text-xs text-muted-foreground">From</Label>
        <div className="relative">
          <CalendarDays className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="date"
            className="pl-9 w-[160px]"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-1">
        <Label className="text-xs text-muted-foreground">To</Label>
        <div className="relative">
          <CalendarDays className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="date"
            className="pl-9 w-[160px]"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
          />
        </div>
      </div>

      {additionalFilters?.map((filter) => (
        <div key={filter.label} className="space-y-1">
          <Label className="text-xs text-muted-foreground">
            {filter.label}
          </Label>
          <Select onValueChange={filter.onChange}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder={`All ${filter.label}`} />
            </SelectTrigger>
            <SelectContent>
              {filter.options.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      ))}

      <Button onClick={handleApply} size="sm">
        Apply
      </Button>
      <Button onClick={handleReset} variant="ghost" size="sm">
        <RotateCcw className="mr-1 h-3 w-3" />
        Reset
      </Button>
    </div>
  );
}
