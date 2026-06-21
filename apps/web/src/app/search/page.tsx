import { AppShell } from "@/components/app-shell";
import { getAuthToken, requireCurrentUser } from "@/lib/auth";
import { fetchPanelFlow, type SourceSummary } from "@/lib/panelflow";
import { SearchClient } from "@/app/search/search-client";

export const dynamic = "force-dynamic";

type SearchPageProps = {
  searchParams: Promise<{ source_id?: string }>;
};

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const [params, user, token] = await Promise.all([searchParams, requireCurrentUser(), getAuthToken()]);
  const sources = await fetchPanelFlow<SourceSummary[]>("/api/sources", token);

  return (
    <AppShell title="Buscar" user={user}>
      {sources.error ? (
        <div className="rounded-lg border border-red-300/20 bg-red-400/10 p-5 text-sm leading-6 text-red-100">
          {sources.error}
        </div>
      ) : (
        <SearchClient initialSourceId={params.source_id} sources={sources.data ?? []} />
      )}
    </AppShell>
  );
}
