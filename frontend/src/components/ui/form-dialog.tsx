"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { X, Loader2 } from "lucide-react";

export interface Field {
  key: string;
  label: string;
  type?: "text" | "email" | "number" | "select" | "textarea" | "checkbox";
  placeholder?: string;
  required?: boolean;
  options?: { value: string; label: string }[];
  min?: number;
  max?: number;
}

interface FormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: Record<string, unknown>) => void;
  fields: Field[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  initialData?: any;
  title: string;
  loading?: boolean;
}

export function FormDialog({ open, onClose, onSubmit, fields, initialData, title, loading }: FormDialogProps) {
  const [form, setForm] = useState<Record<string, unknown>>({});

  useEffect(() => {
    if (initialData) {
      setForm({ ...initialData });
    } else {
      const defaults: Record<string, unknown> = {};
      fields.forEach((f) => {
        defaults[f.key] = f.type === "checkbox" ? false : "";
      });
      setForm(defaults);
    }
  }, [initialData, fields, open]);

  if (!open) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = { ...form };
    fields.forEach((f) => {
      if (f.type === "number") {
        data[f.key] = Number(data[f.key]) || 0;
      }
    });
    onSubmit(data);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true" aria-label={title}>
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-card border border-border rounded-xl shadow-lg w-full max-w-lg mx-4 max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-lg font-semibold">{initialData ? `Edit ${title}` : `Add ${title}`}</h2>
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onClose} aria-label="Close dialog">
            <X size={16} />
          </Button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {fields.map((field) => (
            <div key={field.key} className="space-y-2">
              <label className="text-sm font-medium">
                {field.label}
                {field.required && <span className="text-destructive ml-0.5">*</span>}
              </label>
              {field.type === "select" ? (
                <select
                  className="w-full h-10 px-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  value={String(form[field.key] ?? "")}
                  onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                  required={field.required}
                >
                  <option value="">Select...</option>
                  {field.options?.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              ) : field.type === "textarea" ? (
                <textarea
                  className="w-full min-h-[80px] px-3 py-2 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-y"
                  value={String(form[field.key] ?? "")}
                  onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                  placeholder={field.placeholder}
                  required={field.required}
                />
              ) : field.type === "checkbox" ? (
                <input
                  type="checkbox"
                  className="rounded border-border bg-background"
                  checked={!!form[field.key]}
                  onChange={(e) => setForm({ ...form, [field.key]: e.target.checked })}
                />
              ) : (
                <Input
                  type={field.type || "text"}
                  value={String(form[field.key] ?? "")}
                  onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                  placeholder={field.placeholder}
                  required={field.required}
                  min={field.min}
                  max={field.max}
                />
              )}
            </div>
          ))}
          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 size={16} className="mr-2 animate-spin" />}
              {initialData ? "Save Changes" : "Create"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
