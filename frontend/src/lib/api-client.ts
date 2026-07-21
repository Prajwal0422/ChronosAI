const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  params?: Record<string, string | number | boolean | undefined | null>;
}

type TokenRefreshCallback = () => Promise<string | null>;

class ApiClient {
  private baseUrl: string;
  private accessToken: string | null = null;
  private refreshTokenValue: string | null = null;
  private refreshPromise: Promise<string | null> | null = null;
  private onLogout: (() => void) | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setLogoutHandler(handler: () => void) {
    this.onLogout = handler;
  }

  setTokens(access: string | null, refresh: string | null, remember: boolean) {
    this.accessToken = access;
    this.refreshTokenValue = refresh;
    if (typeof window !== "undefined") {
      const storage = remember ? localStorage : sessionStorage;
      if (access) storage.setItem("access_token", access); else storage.removeItem("access_token");
      if (refresh) storage.setItem("refresh_token", refresh); else storage.removeItem("refresh_token");
      if (remember) localStorage.setItem("remember_me", "true"); else localStorage.removeItem("remember_me");
    }
  }

  loadTokens() {
    if (typeof window === "undefined") return;
    const remember = localStorage.getItem("remember_me") === "true";
    const storage = remember ? localStorage : sessionStorage;
    this.accessToken = storage.getItem("access_token");
    this.refreshTokenValue = storage.getItem("refresh_token");
  }

  getToken(): string | null {
    if (!this.accessToken) this.loadTokens();
    return this.accessToken;
  }

  getRefreshToken(): string | null {
    if (!this.refreshTokenValue) this.loadTokens();
    return this.refreshTokenValue;
  }

  clearTokens() {
    this.accessToken = null;
    this.refreshTokenValue = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("remember_me");
      sessionStorage.removeItem("access_token");
      sessionStorage.removeItem("refresh_token");
    }
  }

  async tryRefreshAccessToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    if (this.refreshPromise) return !!(await this.refreshPromise);

    this.refreshPromise = (async () => {
      try {
        const res = await fetch(`${this.baseUrl}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!res.ok) return null;
        const data = await res.json();
        const remember = localStorage.getItem("remember_me") === "true";
        this.setTokens(data.access_token, data.refresh_token || refreshToken, remember);
        return data.access_token;
      } catch {
        return null;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return !!(await this.refreshPromise);
  }

  private buildUrl(path: string, params?: Record<string, string | number | boolean | undefined | null>): string {
    const url = new URL(`${this.baseUrl}${path}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) url.searchParams.set(key, String(value));
      });
    }
    return url.toString();
  }

  private async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { method = "GET", body, headers = {}, params } = options;

    let token = this.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const config: RequestInit = {
      method,
      headers: { "Content-Type": "application/json", ...headers },
    };
    if (body) config.body = JSON.stringify(body);

    let res = await fetch(this.buildUrl(path, params), config);

    if (res.status === 401 && this.getRefreshToken()) {
      const refreshed = await this.tryRefreshAccessToken();
      if (refreshed) {
        headers["Authorization"] = `Bearer ${this.accessToken}`;
        config.headers = { "Content-Type": "application/json", ...headers };
        res = await fetch(this.buildUrl(path, params), config);
      } else {
        this.clearTokens();
        if (this.onLogout) this.onLogout();
        throw new Error("Session expired. Please sign in again.");
      }
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      const msg = error.detail || error.message || `Request failed (${res.status})`;
      if (res.status === 429) throw new Error("Too many requests. Please wait a moment.");
      throw new Error(msg);
    }

    return res.json();
  }

  get<T>(path: string, params?: Record<string, string | number | boolean | undefined | null>) {
    return this.request<T>(path, { params });
  }

  post<T>(path: string, body?: unknown, params?: Record<string, string | number | boolean | undefined | null>) {
    return this.request<T>(path, { method: "POST", body, params });
  }

  put<T>(path: string, body?: unknown, params?: Record<string, string | number | boolean | undefined | null>) {
    return this.request<T>(path, { method: "PUT", body, params });
  }

  patch<T>(path: string, body?: unknown, params?: Record<string, string | number | boolean | undefined | null>) {
    return this.request<T>(path, { method: "PATCH", body, params });
  }

  delete<T>(path: string, params?: Record<string, string | number | boolean | undefined | null>) {
    return this.request<T>(path, { method: "DELETE", params });
  }
}

export const api = new ApiClient(API_BASE);
