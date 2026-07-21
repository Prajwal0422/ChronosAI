import { create } from "zustand";

interface TimetableEntry {
  id: string;
  time_slot_id: string;
  teacher_id: string;
  subject_id: string;
  classroom_id: string | null;
  laboratory_id: string | null;
  is_lab_session: boolean;
}

interface TimetableState {
  entries: TimetableEntry[];
  selectedSlot: string | null;
  qualityScore: number | null;
  conflicts: number;
  setEntries: (entries: TimetableEntry[]) => void;
  setSelectedSlot: (slot: string | null) => void;
  setQualityScore: (score: number | null) => void;
  setConflicts: (count: number) => void;
  addEntry: (entry: TimetableEntry) => void;
  removeEntry: (id: string) => void;
  clear: () => void;
}

export const useTimetableStore = create<TimetableState>((set) => ({
  entries: [],
  selectedSlot: null,
  qualityScore: null,
  conflicts: 0,
  setEntries: (entries) => set({ entries }),
  setSelectedSlot: (selectedSlot) => set({ selectedSlot }),
  setQualityScore: (qualityScore) => set({ qualityScore }),
  setConflicts: (conflicts) => set({ conflicts }),
  addEntry: (entry) => set((state) => ({ entries: [...state.entries, entry] })),
  removeEntry: (id) =>
    set((state) => ({ entries: state.entries.filter((e) => e.id !== id) })),
  clear: () => set({ entries: [], selectedSlot: null, qualityScore: null, conflicts: 0 }),
}));
