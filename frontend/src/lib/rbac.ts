export type UserRole =
  | "admin"
  | "principal"
  | "hod"
  | "coordinator"
  | "faculty"
  | "viewer";

const ROLE_HIERARCHY: Record<UserRole, number> = {
  admin: 100,
  principal: 80,
  hod: 60,
  coordinator: 40,
  faculty: 20,
  viewer: 10,
};

export function roleWeight(role: string): number {
  return ROLE_HIERARCHY[role as UserRole] ?? 0;
}

export function hasMinRole(userRole: string, minRole: UserRole): boolean {
  return roleWeight(userRole) >= roleWeight(minRole);
}

export type Permission =
  | "manage:all"
  | "manage:users"
  | "manage:colleges"
  | "manage:departments"
  | "manage:teachers"
  | "manage:subjects"
  | "manage:classrooms"
  | "manage:laboratories"
  | "manage:timetables"
  | "manage:settings"
  | "manage:approvals"
  | "manage:notifications"
  | "view:analytics"
  | "view:audit_logs"
  | "view:search"
  | "view:all";

const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  admin: [
    "manage:all", "manage:users", "manage:colleges", "manage:departments",
    "manage:teachers", "manage:subjects", "manage:classrooms", "manage:laboratories",
    "manage:timetables", "manage:settings", "manage:approvals", "manage:notifications",
    "view:analytics", "view:audit_logs", "view:search", "view:all",
  ],
  principal: [
    "manage:colleges", "manage:departments", "manage:teachers", "manage:subjects",
    "manage:timetables", "manage:approvals", "view:analytics", "view:audit_logs", "view:all",
  ],
  hod: [
    "manage:departments", "manage:teachers", "manage:subjects", "manage:timetables",
    "manage:approvals", "view:analytics", "view:audit_logs",
  ],
  coordinator: [
    "manage:timetables", "manage:teachers", "manage:subjects",
    "view:analytics", "view:audit_logs",
  ],
  faculty: ["view:analytics"],
  viewer: [],
};

export function can(role: string, permission: Permission): boolean {
  const perms = ROLE_PERMISSIONS[role as UserRole] ?? [];
  if (perms.includes("manage:all")) return true;
  return perms.includes(permission);
}

export function canAny(role: string, permissions: Permission[]): boolean {
  return permissions.some((p) => can(role, p));
}
