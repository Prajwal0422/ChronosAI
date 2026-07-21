"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Badge } from "@/components/ui/badge";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { Subject } from "@/types";

const columns: Column<Subject>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "code", label: "Code", sortable: true },
  { key: "subject_type", label: "Type", sortable: true, render: (s) => <Badge variant="outline">{s.subject_type}</Badge> },
  { key: "lectures_per_week", label: "Lect/Week", sortable: true },
  { key: "is_lab", label: "Lab", render: (s) => s.is_lab ? <Badge variant="outline">Yes</Badge> : <Badge variant="secondary">No</Badge> },
  { key: "is_elective", label: "Elective", render: (s) => s.is_elective ? <Badge variant="outline">Yes</Badge> : <Badge variant="secondary">No</Badge> },
];

const fields: Field[] = [
  { key: "department_id", label: "Department ID", required: true },
  { key: "name", label: "Name", required: true },
  { key: "code", label: "Code", required: true },
  { key: "subject_type", label: "Subject Type", type: "select", required: true,
    options: [{ value: "theory", label: "Theory" }, { value: "lab", label: "Lab" },
      { value: "project", label: "Project" }, { value: "tutorial", label: "Tutorial" }] },
  { key: "lectures_per_week", label: "Lectures/Week", type: "number", required: true, min: 1, max: 10 },
  { key: "is_elective", label: "Is Elective", type: "checkbox" },
  { key: "is_lab", label: "Is Lab", type: "checkbox" },
];

export default function SubjectsPage() {
  const crud = useCrud<Subject>({ endpoint: "/subjects" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<Subject | null>(null);
  const [deleteItem, setDeleteItem] = useState<Subject | null>(null);

  return (
    <RequirePermission permission="manage:subjects">
      <AppShell title="Subjects">
        <div className="animate-fade-in">
          <DataTable title="All Subjects" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onCreate={() => { setEditItem(null); setOpen(true); }} onEdit={(item) => { setEditItem(item); setOpen(true); }} onDelete={(item) => setDeleteItem(item)} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
        <FormDialog open={open} onClose={() => { setOpen(false); setEditItem(null); }} onSubmit={async (data) => { const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data); if (ok) { setOpen(false); setEditItem(null); } }} fields={fields} initialData={editItem} title="Subject" loading={crud.saving} />
        <ConfirmDialog open={!!deleteItem} onClose={() => setDeleteItem(null)} onConfirm={async () => { if (deleteItem) { await crud.remove(deleteItem.id); setDeleteItem(null); } }} title="Delete Subject" message={`Delete ${deleteItem?.name}?`} loading={crud.saving} />
      </AppShell>
    </RequirePermission>
  );
}
