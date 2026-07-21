"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { FormDialog, Field } from "@/components/ui/form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Badge } from "@/components/ui/badge";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { TimeSlot } from "@/types";
import { formatTime } from "@/lib/utils";

const columns: Column<TimeSlot>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "day_of_week", label: "Day", sortable: true, render: (t) => <Badge variant="outline">{t.day_of_week}</Badge> },
  { key: "start_time", label: "Start", render: (t) => formatTime(t.start_time) },
  { key: "end_time", label: "End", render: (t) => formatTime(t.end_time) },
  { key: "slot_type", label: "Type", render: (t) => <Badge variant="outline">{t.slot_type}</Badge> },
  { key: "slot_group", label: "Group" },
];

const fields: Field[] = [
  { key: "college_id", label: "College ID", required: true },
  { key: "name", label: "Name", required: true },
  { key: "day_of_week", label: "Day of Week", type: "select", required: true,
    options: [{ value: "Monday", label: "Monday" }, { value: "Tuesday", label: "Tuesday" },
      { value: "Wednesday", label: "Wednesday" }, { value: "Thursday", label: "Thursday" },
      { value: "Friday", label: "Friday" }, { value: "Saturday", label: "Saturday" },
      { value: "Sunday", label: "Sunday" }] },
  { key: "start_time", label: "Start Time (HH:mm)", required: true },
  { key: "end_time", label: "End Time (HH:mm)", required: true },
  { key: "slot_type", label: "Slot Type", type: "select",
    options: [{ value: "lecture", label: "Lecture" }, { value: "lab", label: "Lab" },
      { value: "break", label: "Break" }, { value: "other", label: "Other" }] },
  { key: "slot_group", label: "Slot Group" },
];

export default function TimeSlotsPage() {
  const crud = useCrud<TimeSlot>({ endpoint: "/time-slots" });
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<TimeSlot | null>(null);
  const [deleteItem, setDeleteItem] = useState<TimeSlot | null>(null);

  return (
    <RequirePermission permission="manage:timetables">
      <AppShell title="Time Slots">
        <div className="animate-fade-in">
          <DataTable title="All Time Slots" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onCreate={() => { setEditItem(null); setOpen(true); }} onEdit={(item) => { setEditItem(item); setOpen(true); }} onDelete={(item) => setDeleteItem(item)} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
        <FormDialog open={open} onClose={() => { setOpen(false); setEditItem(null); }} onSubmit={async (data) => { const ok = editItem ? await crud.update(editItem.id, data) : await crud.create(data); if (ok) { setOpen(false); setEditItem(null); } }} fields={fields} initialData={editItem} title="Time Slot" loading={crud.saving} />
        <ConfirmDialog open={!!deleteItem} onClose={() => setDeleteItem(null)} onConfirm={async () => { if (deleteItem) { await crud.remove(deleteItem.id); setDeleteItem(null); } }} title="Delete Time Slot" message={`Delete ${deleteItem?.name}?`} loading={crud.saving} />
      </AppShell>
    </RequirePermission>
  );
}
