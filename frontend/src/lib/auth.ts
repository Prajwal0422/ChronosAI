import { api } from "./api-client";
import { useAuthStore } from "@/stores/auth-store";

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  role: string;
  college_id: string | null;
  department_id: string | null;
  is_active: boolean;
}

interface ForgotPasswordResponse {
  message: string;
}

export async function login(
  email: string,
  password: string,
  remember: boolean = false
): Promise<void> {
  const response = await api.post<LoginResponse>("/auth/login", { email, password });
  api.setTokens(response.access_token, response.refresh_token, remember);
  const user = await getCurrentUser();
  useAuthStore.getState().setUser({
    id: user.id,
    email: user.email,
    full_name: user.full_name,
    role: user.role,
    college_id: user.college_id,
    department_id: user.department_id,
    is_active: user.is_active,
  });
}

export async function getCurrentUser(): Promise<UserResponse> {
  return api.get<UserResponse>("/auth/me");
}

export async function updateProfile(data: {
  college_id?: string | null;
  department_id?: string | null;
  full_name?: string;
}): Promise<UserResponse> {
  return api.patch<UserResponse>("/auth/me", data);
}

export function logout() {
  api.clearTokens();
  useAuthStore.getState().clear();
  window.location.href = "/login";
}

export function isAuthenticated(): boolean {
  return !!api.getToken();
}

export function needsWorkspace(): boolean {
  return !useAuthStore.getState().user?.college_id;
}

export async function initAuth(): Promise<void> {
  api.loadTokens();
  const token = api.getToken();
  if (!token) {
    useAuthStore.getState().setLoading(false);
    return;
  }
  try {
    const user = await getCurrentUser();
    useAuthStore.getState().setUser({
      id: user.id,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      college_id: user.college_id,
      department_id: user.department_id,
      is_active: user.is_active,
    });
  } catch {
    const refreshed = api.getRefreshToken() ? await api.tryRefreshAccessToken() : false;
    if (refreshed) {
      try {
        const user = await getCurrentUser();
        useAuthStore.getState().setUser({
          id: user.id,
          email: user.email,
          full_name: user.full_name,
          role: user.role,
          college_id: user.college_id,
          department_id: user.department_id,
          is_active: user.is_active,
        });
        return;
      } catch {}
    }
    api.clearTokens();
    useAuthStore.getState().clear();
  }
}

export async function forgotPassword(email: string): Promise<string> {
  try {
    const response = await api.post<ForgotPasswordResponse>("/auth/forgot-password", { email });
    return response.message;
  } catch {
    return "If the email exists, a reset link will be sent.";
  }
}
