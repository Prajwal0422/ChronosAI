"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { Section } from "@/types";

const columns: Column<Section>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "code", label: "Code", sortable: true },
  { key: "strength", label: "Strength", sortable: true },
  { key: "semester_id", label: "Semester ID" },
];

const fields: Field[] = [
  { key: "semester_id", label: "Semester ID", required: true },
  { key: "name", label: "Name", required: true },
  { key: "code", label: "Code", required: true },
  { key: "strength", label: "Strength", type: "number", required: true, min: 1 },
];

export default function SectionsPage() {
  const crud = useCrud<Section>({ endpoint: "/sections" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<Section | null>(null);
  const [deleteItem, setDeleteItem] = useState<Section | null>(null);

  return (
    <RequirePermission permission="manage:classrooms">
      <AppShell title="Sections">
        <div className="animate-fade-in">
          <DataTable title="All Sections" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onCreate={() => { setEditItem(null); setOpen(true); }} onEdit={(item) => { setEditItem(item); setOpen(true); }} onDelete={(item) => setDeleteItem(item)} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
        <FormDialog open={open} onClose={() => { setOpen(false); setEditItem(null); }} onSubmit={async (data) => { const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data); if (ok) { setOpen(false); setEditItem(null); } }} fields={fields} initialData={editItem} title="Section" loading={crud.saving} />
        <ConfirmDialog open={!!deleteItem} onClose={() => setDeleteItem(null)} onConfirm={async () => { if (deleteItem) { await crud.remove(deleteItem.id); setDeleteItem(null); } }} title="Delete Section" message={`Delete ${deleteItem?.name}?`} loading={crud.saving} />
      </AppShell>
    </RequirePermission>
  );
}
