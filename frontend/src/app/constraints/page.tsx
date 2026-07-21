"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Badge } from "@/components/ui/badge";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { Constraint } from "@/types";

const columns: Column<Constraint>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "constraint_type", label: "Type", sortable: true, render: (c) => <Badge variant={c.constraint_type === "hard" ? "destructive" : "warning"}>{c.constraint_type}</Badge> },
  { key: "category", label: "Category", sortable: true, render: (c) => <Badge variant="outline">{c.category}</Badge> },
  { key: "priority", label: "Priority", sortable: true },
  { key: "department_id", label: "Dept ID" },
];

const fields: Field[] = [
  { key: "college_id", label: "College ID", required: true },
  { key: "department_id", label: "Department ID" },
  { key: "name", label: "Name", required: true },
  { key: "constraint_type", label: "Type", type: "select", required: true,
    options: [{ value: "hard", label: "Hard (Must Satisfy)" }, { value: "soft", label: "Soft (Preference)" }] },
  { key: "category", label: "Category", type: "select", required: true,
    options: [{ value: "teacher_time", label: "Teacher Time" }, { value: "room_capacity", label: "Room Capacity" },
      { value: "lab_availability", label: "Lab Availability" }, { value: "subject_spacing", label: "Subject Spacing" },
      { value: "teacher_load", label: "Teacher Load" }, { value: "section_balance", label: "Section Balance" },
      { value: "other", label: "Other" }] },
  { key: "priority", label: "Priority (1-10)", type: "number", required: true, min: 1, max: 10 },
];

export default function ConstraintsPage() {
  const crud = useCrud<Constraint>({ endpoint: "/constraints" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<Constraint | null>(null);
  const [deleteItem, setDeleteItem] = useState<Constraint | null>(null);

  return (
    <RequirePermission permission="manage:timetables">
      <AppShell title="Constraints">
        <div className="animate-fade-in">
          <DataTable title="All Constraints" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onCreate={() => { setEditItem(null); setOpen(true); }} onEdit={(item) => { setEditItem(item); setOpen(true); }} onDelete={(item) => setDeleteItem(item)} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
        <FormDialog open={open} onClose={() => { setOpen(false); setEditItem(null); }} onSubmit={async (data) => { const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data); if (ok) { setOpen(false); setEditItem(null); } }} fields={fields} initialData={editItem} title="Constraint" loading={crud.saving} />
        <ConfirmDialog open={!!deleteItem} onClose={() => setDeleteItem(null)} onConfirm={async () => { if (deleteItem) { await crud.remove(deleteItem.id); setDeleteItem(null); } }} title="Delete Constraint" message={`Delete ${deleteItem?.name}?`} loading={crud.saving} />
      </AppShell>
    </RequirePermission>
  );
}
