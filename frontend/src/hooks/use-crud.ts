import { useState, useCallback, useEffect } from "react";
import toast from "react-hot-toast";
import { api } from "@/lib/api-client";
import { PaginatedResponse } from "@/types";

interface UseCrudOptions {
  endpoint: string;
  fetchOnMount?: boolean;
  pageSize?: number;
}

export function useCrud<T extends { id: string }>({ endpoint, fetchOnMount = true, pageSize = 10 }: UseCrudOptions) {
  const [data, setData] = useState<T[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  const fetch = useCallback(async (p?: number, q?: string) => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { limit: pageSize, offset: ((p ?? page) - 1) * pageSize };
      if (q ?? search) params.search = q ?? search;
      const res = await api.get<PaginatedResponse<T>>(endpoint, params);
      setData(res.items);
      setTotal(res.total);
    } catch {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [endpoint, page, search, pageSize]);

  useEffect(() => {
    if (fetchOnMount) fetch();
  }, [fetchOnMount]);

  const create = async (body: Record<string, unknown>): Promise<boolean> => {
    setSaving(true);
    try {
      await api.post<T>(endpoint, body);
      toast.success("Created successfully");
      await fetch(1, search);
      setPage(1);
      return true;
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create");
      return false;
    } finally {
      setSaving(false);
    }
  };

  const update = async (id: string, body: Record<string, unknown>): Promise<boolean> => {
    setSaving(true);
    try {
      await api.put<T>(`${endpoint}/${id}`, body);
      toast.success("Updated successfully");
      await fetch(page, search);
      return true;
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to update");
      return false;
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id: string): Promise<boolean> => {
    setSaving(true);
    try {
      await api.delete(`${endpoint}/${id}`);
      toast.success("Deleted successfully");
      await fetch(page, search);
      return true;
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete");
      return false;
    } finally {
      setSaving(false);
    }
  };

  const handleSearch = (q: string) => {
    setSearch(q);
    setPage(1);
    fetch(1, q);
  };

  const handlePageChange = (p: number) => {
    setPage(p);
    fetch(p, search);
  };

  return { data, total, loading, saving, page, search, create, update, remove, fetch, handleSearch, handlePageChange };
}
