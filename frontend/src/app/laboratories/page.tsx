"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { Laboratory } from "@/types";

const columns: Column<Laboratory>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "code", label: "Code", sortable: true },
  { key: "capacity", label: "Capacity", sortable: true },
  { key: "building", label: "Building" },
  { key: "floor", label: "Floor" },
  { key: "department_id", label: "Dept ID" },
];

const fields: Field[] = [
  { key: "college_id", label: "College ID", required: true },
  { key: "department_id", label: "Department ID" },
  { key: "name", label: "Name", required: true },
  { key: "code", label: "Code", required: true },
  { key: "capacity", label: "Capacity", type: "number", required: true, min: 1 },
  { key: "building", label: "Building" },
  { key: "floor", label: "Floor", type: "number" },
];

export default function LaboratoriesPage() {
  const crud = useCrud<Laboratory>({ endpoint: "/laboratories" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<Laboratory | null>(null);
  const [deleteItem, setDeleteItem] = useState<Laboratory | null>(null);

  return (
    <RequirePermission permission="manage:laboratories">
      <AppShell title="Laboratories">
        <div className="animate-fade-in">
          <DataTable title="All Laboratories" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onCreate={() => { setEditItem(null); setOpen(true); }} onEdit={(item) => { setEditItem(item); setOpen(true); }} onDelete={(item) => setDeleteItem(item)} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
        <FormDialog open={open} onClose={() => { setOpen(false); setEditItem(null); }} onSubmit={async (data) => { const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data); if (ok) { setOpen(false); setEditItem(null); } }} fields={fields} initialData={editItem} title="Laboratory" loading={crud.saving} />
        <ConfirmDialog open={!!deleteItem} onClose={() => setDeleteItem(null)} onConfirm={async () => { if (deleteItem) { await crud.remove(deleteItem.id); setDeleteItem(null); } }} title="Delete Laboratory" message={`Delete ${deleteItem?.name}?`} loading={crud.saving} />
      </AppShell>
    </RequirePermission>
  );
}
