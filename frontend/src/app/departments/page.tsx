"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { Department } from "@/types";

const columns: Column<Department>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "code", label: "Code", sortable: true },
  { key: "college_id", label: "College ID" },
  { key: "description", label: "Description" },
];

const fields: Field[] = [
  { key: "college_id", label: "College ID", required: true },
  { key: "name", label: "Name", required: true },
  { key: "code", label: "Code", required: true },
  { key: "description", label: "Description", type: "textarea" },
];

export default function DepartmentsPage() {
  const crud = useCrud<Department>({ endpoint: "/departments" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<Department | null>(null);
  const [deleteItem, setDeleteItem] = useState<Department | null>(null);

  const handleSubmit = async (data: Record<string, unknown>) => {
    const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data);
    if (ok) { setOpen(false); setEditItem(null); }
  };

  return (
    <RequirePermission permission="manage:departments">
      <AppShell title="Departments">
        <div className="animate-fade-in">
          <DataTable
            title="All Departments"
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
        <FormDialog open={open} onClose={() => { setOpen(false); setEditItem(null); }} onSubmit={handleSubmit} fields={fields} initialData={editItem} title="Department" loading={crud.saving} />
        <ConfirmDialog open={!!deleteItem} onClose={() => setDeleteItem(null)} onConfirm={async () => { if (deleteItem) { await crud.remove(deleteItem.id); setDeleteItem(null); } }} title="Delete Department" message={`Are you sure you want to delete ${deleteItem?.name}?`} loading={crud.saving} />
      </AppShell>
    </RequirePermission>
  );
}
