"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { Search, Plus, ChevronLeft, ChevronRight, Pencil, Trash2, Loader2 } from "lucide-react";

export interface Column<T> {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (item: T) => React.ReactNode;
}

interface DataTableProps<T> {
  title: string;
  columns: Column<T>[];
  data: T[] | undefined;
  loading?: boolean;
  total?: number;
  searchable?: boolean;
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  onCreate?: () => void;
  onEdit?: (item: T) => void;
  onDelete?: (item: T) => void;
  onPageChange?: (page: number) => void;
  page?: number;
  pageSize?: number;
}

export function DataTable<T extends { id: string }>({
  title,
  columns,
  data,
  loading,
  total = 0,
  searchable = true,
  searchPlaceholder = "Search...",
  onSearch,
  onCreate,
  onEdit,
  onDelete,
  onPageChange,
  page = 1,
  pageSize = 10,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const sortedData = data && sortKey
    ? [...data].sort((a, b) => {
        const aVal = String((a as Record<string, unknown>)[sortKey] ?? "");
        const bVal = String((b as Record<string, unknown>)[sortKey] ?? "");
        const cmp = aVal.localeCompare(bVal, undefined, { numeric: true });
        return sortDir === "asc" ? cmp : -cmp;
      })
    : data;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-base">{title}</CardTitle>
        {onCreate && (
          <Button size="sm" onClick={onCreate}>
            <Plus size={16} className="mr-1" /> Add
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {searchable && onSearch && (
          <div className="relative mb-4">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder={searchPlaceholder}
              className="pl-9 h-9"
              onChange={(e) => onSearch(e.target.value)}
            />
          </div>
        )}

        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  {columns.map((col) => (
                    <th
                      key={col.key}
                      className={cn(
                        "text-left text-xs font-medium text-muted-foreground pb-3 pr-4 last:pr-0",
                        col.sortable && "cursor-pointer hover:text-foreground select-none"
                      )}
                      onClick={() => col.sortable && handleSort(col.key)}
                    >
                      <span className="inline-flex items-center gap-1">
                        {col.label}
                        {col.sortable && sortKey === col.key && (
                          <span className="text-[10px]">{sortDir === "asc" ? "▲" : "▼"}</span>
                        )}
                      </span>
                    </th>
                  ))}
                  {(onEdit || onDelete) && <th className="text-right text-xs font-medium text-muted-foreground pb-3 w-20">Actions</th>}
                </tr>
              </thead>
              <tbody>
                {sortedData && sortedData.length > 0 ? (
                  sortedData.map((item, idx) => (
                    <tr key={(item.id as string) || idx} className="border-b border-border/50 last:border-0">
                      {columns.map((col) => (
                        <td key={col.key} className="py-3 pr-4 last:pr-0 text-sm">
                          {col.render ? col.render(item) : String((item as Record<string, unknown>)[col.key] ?? "")}
                        </td>
                      ))}
                      {(onEdit || onDelete) && (
                        <td className="py-3 text-right">
                          <div className="inline-flex gap-1">
                            {onEdit && (
                              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => onEdit(item)} aria-label="Edit">
                                <Pencil size={14} />
                              </Button>
                            )}
                            {onDelete && (
                              <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive hover:text-destructive" onClick={() => onDelete(item)} aria-label="Delete">
                                <Trash2 size={14} />
                              </Button>
                            )}
                          </div>
                        </td>
                      )}
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={columns.length + ((onEdit || onDelete) ? 1 : 0)} className="py-8 text-center text-sm text-muted-foreground">
                      {data === undefined ? "Loading..." : "No records found"}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {onPageChange && totalPages > 1 && (
          <div className="flex items-center justify-between pt-4">
            <p className="text-xs text-muted-foreground">
              {total > 0
                ? `Showing ${(page - 1) * pageSize + 1}-${Math.min(page * pageSize, total)} of ${total}`
                : "No results"}
            </p>
            <div className="flex gap-1">
              <Button variant="outline" size="icon" className="h-8 w-8" disabled={page <= 1} onClick={() => onPageChange(page - 1)} aria-label="Previous page">
                <ChevronLeft size={14} />
              </Button>
              <Button variant="outline" size="icon" className="h-8 w-8" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)} aria-label="Next page">
                <ChevronRight size={14} />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
