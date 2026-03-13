"use client";

import { type Table } from "@tanstack/react-table";
import { SearchInput } from "@/components/shared/search-input";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { type ReactNode } from "react";

interface DataTableToolbarProps<TData> {
  table: Table<TData>;
  searchKey?: string;
  searchPlaceholder?: string;
  filters?: ReactNode;
  actions?: ReactNode;
}

export function DataTableToolbar<TData>({
  table,
  searchKey,
  searchPlaceholder = "Search...",
  filters,
  actions,
}: DataTableToolbarProps<TData>) {
  const isFiltered = table.getState().columnFilters.length > 0;

  return (
    <div className="flex items-center justify-between">
      <div className="flex flex-1 items-center space-x-2">
        {searchKey && (
          <SearchInput
            placeholder={searchPlaceholder}
            className="w-[250px] lg:w-[350px]"
            defaultValue={
              (table.getColumn(searchKey)?.getFilterValue() as string) ?? ""
            }
            onSearch={(value) =>
              table.getColumn(searchKey)?.setFilterValue(value)
            }
          />
        )}
        {filters}
        {isFiltered && (
          <Button
            variant="ghost"
            onClick={() => table.resetColumnFilters()}
            className="h-8 px-2 lg:px-3"
          >
            Reset
            <X className="ml-2 h-4 w-4" />
          </Button>
        )}
      </div>
      {actions}
    </div>
  );
}
