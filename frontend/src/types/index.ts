export interface College {
  id: string;
  name: string;
  code: string;
  college_type: string;
  address: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  academic_year: string;
  is_active: boolean;
  [key: string]: unknown;
}

export interface Department {
  id: string;
  college_id: string;
  name: string;
  code: string;
  hod_id: string | null;
  description: string | null;
  is_active: boolean;
}

export interface Semester {
  id: string;
  department_id: string;
  name: string;
  code: string;
  year: number;
  order: number;
  is_active: boolean;
}

export interface Section {
  id: string;
  semester_id: string;
  name: string;
  code: string;
  strength: number;
  is_active: boolean;
}

export interface Teacher {
  id: string;
  department_id: string;
  employee_code: string;
  full_name: string;
  email: string;
  phone: string | null;
  qualification: string | null;
  specialization: string | null;
  max_lectures_per_day: number;
  max_lectures_per_week: number;
  is_shared: boolean;
  is_active: boolean;
}

export interface Subject {
  id: string;
  department_id: string;
  name: string;
  code: string;
  subject_type: string;
  lectures_per_week: number;
  is_elective: boolean;
  is_lab: boolean;
  is_active: boolean;
}

export interface Classroom {
  id: string;
  college_id: string;
  name: string;
  code: string;
  capacity: number;
  building: string;
  floor: number;
  room_type: string;
  facilities: Record<string, unknown>;
  is_active: boolean;
}

export interface Laboratory {
  id: string;
  college_id: string;
  department_id: string;
  name: string;
  code: string;
  capacity: number;
  building: string;
  floor: number;
  equipment: Record<string, unknown>;
  is_active: boolean;
}

export interface TimeSlot {
  id: string;
  college_id: string;
  name: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  slot_type: string;
  slot_group: string | null;
  is_active: boolean;
}

export type TimetableStatus = "draft" | "generated" | "under_review" | "approved" | "published" | "archived";

export interface Timetable {
  id: string;
  section_id: string;
  academic_calendar_id: string;
  name: string;
  version: number;
  status: TimetableStatus;
  quality_score: number | null;
  is_active: boolean;
}

export interface TimetableEntry {
  id: string;
  timetable_id: string;
  time_slot_id: string;
  section_id: string;
  teacher_id: string;
  subject_id: string;
  classroom_id: string | null;
  laboratory_id: string | null;
  is_lab_session: boolean;
  notes: string | null;
}

export interface Constraint {
  id: string;
  college_id: string;
  department_id: string | null;
  name: string;
  constraint_type: "hard" | "soft";
  category: string;
  priority: number;
  config: Record<string, unknown>;
  is_active: boolean;
}

export interface ConflictRecord {
  id: string;
  timetable_id: string;
  conflict_type: string;
  severity: string;
  description: string;
  involved_entries: unknown[];
  resolved: boolean;
}

export interface Notification {
  id: string;
  user_id: string;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  reference_type: string | null;
  reference_id: string | null;
  read_at: string | null;
  created_at: string;
}

export interface Simulation {
  id: string;
  timetable_id: string;
  simulation_type: string;
  name: string;
  description: string | null;
  parameters: Record<string, unknown>;
  original_score: number | null;
  simulated_score: number | null;
  impact_summary: string | null;
  applied: boolean;
  applied_at: string | null;
  created_by: string | null;
  created_at: string;
}

export interface VersionSnapshot {
  id: string;
  timetable_id: string;
  version_number: number;
  label: string | null;
  quality_score: number | null;
  entry_count: number;
  change_summary: string | null;
  is_restored: boolean;
  restored_at: string | null;
  created_by: string | null;
  created_at: string;
}

export interface Approval {
  id: string;
  timetable_id: string;
  status: string;
  requested_by: string | null;
  requested_at: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  review_notes: string | null;
  approved_by: string | null;
  approved_at: string | null;
  published_by: string | null;
  published_at: string | null;
  archived_by: string | null;
  archived_at: string | null;
  created_at: string | null;
}

export interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  changes: Record<string, unknown> | null;
  ip_address: string | null;
  timestamp: string;
}

export interface Insight {
  type: string;
  severity: string;
  title: string;
  description: string;
  suggestion: string;
}

export interface HealthScore {
  timetable_id: string;
  timetable_name: string;
  overall_score: number;
  grade: string;
  entry_count: number;
  metrics: Record<string, number>;
  improvement_suggestions: string[];
}

export interface SearchResult {
  type: string;
  id: string;
  label: string;
  subtitle: string;
  url: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}
