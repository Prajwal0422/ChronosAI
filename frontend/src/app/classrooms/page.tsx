"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Badge } from "@/components/ui/badge";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { Classroom } from "@/types";

const columns: Column<Classroom>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "code", label: "Code", sortable: true },
  { key: "capacity", label: "Capacity", sortable: true },
  { key: "building", label: "Building" },
  { key: "floor", label: "Floor" },
  { key: "room_type", label: "Type", render: (c) => <Badge variant="outline">{c.room_type}</Badge> },
];

const fields: Field[] = [
  { key: "college_id", label: "College ID", required: true },
  { key: "name", label: "Name", required: true },
  { key: "code", label: "Code", required: true },
  { key: "capacity", label: "Capacity", type: "number", required: true, min: 1 },
  { key: "building", label: "Building" },
  { key: "floor", label: "Floor", type: "number" },
  { key: "room_type", label: "Room Type", type: "select",
    options: [{ value: "lecture", label: "Lecture Hall" }, { value: "seminar", label: "Seminar Hall" },
      { value: "tutorial", label: "Tutorial Room" }, { value: "conference", label: "Conference Room" },
      { value: "other", label: "Other" }] },
];

export default function ClassroomsPage() {
  const crud = useCrud<Classroom>({ endpoint: "/classrooms" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<Classroom | null>(null);
  const [deleteItem, setDeleteItem] = useState<Classroom | null>(null);

  return (
    <RequirePermission permission="manage:classrooms">
      <AppShell title="Classrooms">
        <div className="animate-fade-in">
          <DataTable title="All Classrooms" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onCreate={() => { setEditItem(null); setOpen(true); }} onEdit={(item) => { setEditItem(item); setOpen(true); }} onDelete={(item) => setDeleteItem(item)} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
        <FormDialog open={open} onClose={() => { setOpen(false); setEditItem(null); }} onSubmit={async (data) => { const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data); if (ok) { setOpen(false); setEditItem(null); } }} fields={fields} initialData={editItem} title="Classroom" loading={crud.saving} />
        <ConfirmDialog open={!!deleteItem} onClose={() => setDeleteItem(null)} onConfirm={async () => { if (deleteItem) { await crud.remove(deleteItem.id); setDeleteItem(null); } }} title="Delete Classroom" message={`Delete ${deleteItem?.name}?`} loading={crud.saving} />
      </AppShell>
    </RequirePermission>
  );
}
