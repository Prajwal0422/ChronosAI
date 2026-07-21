"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Badge } from "@/components/ui/badge";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { College } from "@/types";

const columns: Column<College>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "code", label: "Code", sortable: true },
  {
    key: "college_type", label: "Type", sortable: true,
    render: (c) => <Badge variant="outline">{c.college_type}</Badge>,
  },
  { key: "academic_year", label: "Academic Year", sortable: true },
  { key: "email", label: "Email" },
  { key: "phone", label: "Phone" },
];

const fields: Field[] = [
  { key: "name", label: "Name", required: true },
  { key: "code", label: "Code", required: true },
  { key: "college_type", label: "College Type", type: "select", required: true,
    options: [{ value: "engineering", label: "Engineering" }, { value: "medical", label: "Medical" },
      { value: "arts", label: "Arts & Science" }, { value: "management", label: "Management" },
      { value: "pharmacy", label: "Pharmacy" }, { value: "law", label: "Law" },
      { value: "other", label: "Other" }] },
  { key: "academic_year", label: "Academic Year", placeholder: "e.g. 2025-2026", required: true },
  { key: "address", label: "Address", type: "textarea" },
  { key: "email", label: "Email", type: "email" },
  { key: "phone", label: "Phone" },
  { key: "website", label: "Website" },
];

export default function CollegesPage() {
  const crud = useCrud<College>({ endpoint: "/colleges" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<College | null>(null);
  const [deleteItem, setDeleteItem] = useState<College | null>(null);

  const handleSubmit = async (data: Record<string, unknown>) => {
    const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data);
    if (ok) { setOpen(false); setEditItem(null); }
  };

  const handleDelete = async () => {
    if (!deleteItem) return;
    const ok = await crud.remove(deleteItem.id);
    if (ok) setDeleteItem(null);
  };

  return (
    <RequirePermission permission="manage:colleges">
      <AppShell title="Colleges">
        <div className="animate-fade-in">
          <DataTable
            title="All Colleges"
            columns={columns}
            data={crud.data}
            loading={crud.loading}
            total={crud.total}
            onSearch={crud.handleSearch}
            onCreate={() => { setEditItem(null); setOpen(true); }}
            onEdit={(item) => { setEditItem(item); setOpen(true); }}
            onDelete={(item) => setDeleteItem(item)}
            onPageChange={crud.handlePageChange}
            page={crud.page}
          />
        </div>
        <FormDialog
          open={open}
          onClose={() => { setOpen(false); setEditItem(null); }}
          onSubmit={handleSubmit}
          fields={fields}
          initialData={editItem}
          title="College"
          loading={crud.saving}
        />
        <ConfirmDialog
          open={!!deleteItem}
          onClose={() => setDeleteItem(null)}
          onConfirm={handleDelete}
          title="Delete College"
          message={`Are you sure you want to delete ${deleteItem?.name}? This action cannot be undone.`}
          loading={crud.saving}
        />
      </AppShell>
    </RequirePermission>
  );
}
