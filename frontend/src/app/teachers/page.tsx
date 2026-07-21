"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Badge } from "@/components/ui/badge";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { Teacher } from "@/types";

const columns: Column<Teacher>[] = [
  { key: "full_name", label: "Name", sortable: true },
  { key: "employee_code", label: "Code", sortable: true },
  { key: "email", label: "Email" },
  { key: "specialization", label: "Specialization" },
  { key: "max_lectures_per_week", label: "Max/Week", sortable: true },
  { key: "is_shared", label: "Shared", render: (t) => t.is_shared ? <Badge variant="outline">Yes</Badge> : <Badge variant="secondary">No</Badge> },
];

const fields: Field[] = [
  { key: "department_id", label: "Department ID", required: true },
  { key: "employee_code", label: "Employee Code", required: true },
  { key: "full_name", label: "Full Name", required: true },
  { key: "email", label: "Email", type: "email", required: true },
  { key: "phone", label: "Phone" },
  { key: "qualification", label: "Qualification" },
  { key: "specialization", label: "Specialization" },
  { key: "max_lectures_per_day", label: "Max Lectures/Day", type: "number", min: 1, max: 8 },
  { key: "max_lectures_per_week", label: "Max Lectures/Week", type: "number", min: 1, max: 40 },
  { key: "is_shared", label: "Shared Teacher", type: "checkbox" },
];

export default function TeachersPage() {
  const crud = useCrud<Teacher>({ endpoint: "/teachers" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<Teacher | null>(null);
  const [deleteItem, setDeleteItem] = useState<Teacher | null>(null);

  return (
    <RequirePermission permission="manage:teachers">
      <AppShell title="Teachers">
        <div className="animate-fade-in">
          <DataTable title="All Teachers" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onCreate={() => { setEditItem(null); setOpen(true); }} onEdit={(item) => { setEditItem(item); setOpen(true); }} onDelete={(item) => setDeleteItem(item)} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
        <FormDialog open={open} onClose={() => { setOpen(false); setEditItem(null); }} onSubmit={async (data) => { const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data); if (ok) { setOpen(false); setEditItem(null); } }} fields={fields} initialData={editItem} title="Teacher" loading={crud.saving} />
        <ConfirmDialog open={!!deleteItem} onClose={() => setDeleteItem(null)} onConfirm={async () => { if (deleteItem) { await crud.remove(deleteItem.id); setDeleteItem(null); } }} title="Delete Teacher" message={`Delete ${deleteItem?.full_name}?`} loading={crud.saving} />
      </AppShell>
    </RequirePermission>
  );
}
