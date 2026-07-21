"use client";

import { Suspense, useState, useEffect, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api-client";
import { RequirePermission } from "@/components/auth/require-permission";
import { Search, SearchX, GraduationCap, BookOpen, Monitor, FlaskConical, Brain, ExternalLink } from "lucide-react";
import { SearchResult } from "@/types";
import Link from "next/link";

const typeIcon: Record<string, React.ReactNode> = {
  teacher: <GraduationCap size={16} className="text-primary" />,
  subject: <BookOpen size={16} className="text-info" />,
  classroom: <Monitor size={16} className="text-success" />,
  laboratory: <FlaskConical size={16} className="text-warning" />,
  timetable: <Brain size={16} className="text-destructive" />,
};

export default function SearchPage() {
  return <Suspense fallback={<AppShell title="Global Search"><div className="p-6 text-muted-foreground">Loading search...</div></AppShell>}><SearchPageContent /></Suspense>;
}

function SearchPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("");

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) { setResults([]); return; }
    setLoading(true);
    try {
      const params: Record<string, any> = { q };
      if (filter) params.entity_type = filter;
      const data = await api.get<{ results: SearchResult[]; total: number }>("/search", params);
      setResults(data.results || []);
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }, [filter]);

  useEffect(() => {
    const q = searchParams.get("q");
    if (q) { setQuery(q); doSearch(q); }
  }, [searchParams, doSearch]);

  const handleSearch = () => {
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
      doSearch(query);
    }
  };

  const typeCounts: Record<string, number> = {};
  results.forEach((r) => { typeCounts[r.type] = (typeCounts[r.type] || 0) + 1; });

  return (
    <RequirePermission permission="view:search">
      <AppShell title="Global Search">
        <div className="space-y-6 animate-fade-in">
          <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
            <CardContent className="p-6">
              <div className="flex gap-3">
                <div className="relative flex-1">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    placeholder="Search teachers, subjects, rooms, timetables..."
                    className="pl-9 h-10"
                    aria-label="Search"
                  />
                </div>
                <Button onClick={handleSearch} disabled={!query.trim() || loading}>Search</Button>
              </div>
            </CardContent>
          </Card>

          {loading && (
            <div className="space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-16 w-full" />)}</div>
          )}

          {!loading && results.length > 0 && (
            <>
              <div className="flex gap-2 flex-wrap">
                <Button variant={!filter ? "default" : "outline"} size="sm" onClick={() => setFilter("")}>
                  All ({results.length})
                </Button>
                {Object.entries(typeCounts).map(([type, count]) => (
                  <Button key={type} variant={filter === type ? "default" : "outline"} size="sm" onClick={() => setFilter(type)}>
                    {type} ({count})
                  </Button>
                ))}
              </div>

              <div className="space-y-2">
                {results.map((r, i) => (
                  <Link key={`${r.id}-${i}`} href={r.url} className="block">
                    <Card className="hover:bg-muted/30 transition-colors cursor-pointer">
                      <CardContent className="p-4 flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/5">{typeIcon[r.type] || <Search size={16} />}</div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium">{r.label}</p>
                          <p className="text-xs text-muted-foreground">{r.subtitle}</p>
                        </div>
                        <Badge variant="outline" className="text-[10px]">{r.type}</Badge>
                        <ExternalLink size={14} className="text-muted-foreground shrink-0" />
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            </>
          )}

          {!loading && results.length === 0 && query && (
            <Card><CardContent className="p-12 text-center text-muted-foreground">
              <SearchX size={40} className="mx-auto mb-3 opacity-30" />
              <p>No results found for "{query}"</p>
              <p className="text-xs mt-1">Try different keywords or browse from the sidebar</p>
            </CardContent></Card>
          )}
        </div>
      </AppShell>
    </RequirePermission>
  );
}
