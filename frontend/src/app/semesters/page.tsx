"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Badge } from "@/components/ui/badge";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { Semester } from "@/types";

const columns: Column<Semester>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "code", label: "Code", sortable: true },
  { key: "year", label: "Year", sortable: true },
  { key: "order", label: "Order", sortable: true },
  { key: "department_id", label: "Department ID" },
  { key: "is_active", label: "Status", render: (s) => <Badge variant={s.is_active ? "outline" : "secondary"}>{s.is_active ? "Active" : "Inactive"}</Badge> },
];

const fields: Field[] = [
  { key: "department_id", label: "Department ID", required: true },
  { key: "name", label: "Name", required: true },
  { key: "code", label: "Code", required: true },
  { key: "year", label: "Year", type: "number", required: true, min: 1, max: 8 },
  { key: "order", label: "Order", type: "number", required: true, min: 1, max: 8 },
];

export default function SemestersPage() {
  const crud = useCrud<Semester>({ endpoint: "/semesters" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<Semester | null>(null);
  const [deleteItem, setDeleteItem] = useState<Semester | null>(null);

  const handleSubmit = async (data: Record<string, unknown>) => {
    const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data);
    if (ok) { setOpen(false); setEditItem(null); }
  };

  return (
    <RequirePermission permission="manage:departments">
      <AppShell title="Semesters">
        <div className="animate-fade-in">
          <DataTable title="All Semesters" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onCreate={() => { setEditItem(null); setOpen(true); }} onEdit={(item) => { setEditItem(item); setOpen(true); }} onDelete={(item) => setDeleteItem(item)} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
        <FormDialog open={open} onClose={() => { setOpen(false); setEditItem(null); }} onSubmit={handleSubmit} fields={fields} initialData={editItem} title="Semester" loading={crud.saving} />
        <ConfirmDialog open={!!deleteItem} onClose={() => setDeleteItem(null)} onConfirm={async () => { if (deleteItem) { await crud.remove(deleteItem.id); setDeleteItem(null); } }} title="Delete Semester" message={`Delete ${deleteItem?.name}?`} loading={crud.saving} />
      </AppShell>
    </RequirePermission>
  );
}
