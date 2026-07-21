"use client";

import { Button } from "@/components/ui/button";
import { AlertTriangle, Loader2, X } from "lucide-react";

interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  loading?: boolean;
}

export function ConfirmDialog({ open, onClose, onConfirm, title, message, loading }: ConfirmDialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true" aria-label={title}>
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-card border border-border rounded-xl shadow-lg w-full max-w-sm mx-4 p-6">
        <div className="flex items-start gap-4">
          <div className="p-2 rounded-full bg-destructive/10 shrink-0">
            <AlertTriangle size={20} className="text-destructive" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-semibold">{title}</h3>
            <p className="text-sm text-muted-foreground mt-1">{message}</p>
          </div>
          <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0" onClick={onClose} aria-label="Close dialog">
            <X size={16} />
          </Button>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button variant="destructive" onClick={onConfirm} disabled={loading}>
            {loading && <Loader2 size={16} className="mr-2 animate-spin" />}
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
}
