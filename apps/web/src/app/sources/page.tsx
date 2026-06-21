import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { getAuthToken, requireCurrentUser } from "@/lib/auth";
import { fetchPanelFlow, type SourceSummary } from "@/lib/panelflow";

export const dynamic = "force-dynamic";

export default async function SourcesPage() {
  const [user, token] = await Promise.all([requireCurrentUser(), getAuthToken()]);
  const sources = await fetchPanelFlow<SourceSummary[]>("/api/sources", token);

  return (
    <AppShell title="Fontes" user={user}>
      <div className="grid gap-5">
        {sources.error ? (
          <div className="rounded-lg border border-red-300/20 bg-red-400/10 p-5 text-sm leading-6 text-red-100">
            {sources.error}
          </div>
        ) : null}

        {!sources.error && sources.data?.length === 0 ? (
          <div className="rounded-lg border border-white/10 bg-ink-850/75 p-6 text-sm leading-6 text-slate-300">
            Nenhuma fonte instalada foi encontrada. Abra temporariamente a interface interna do Suwayomi pelo VPS
            para instalar/configurar extensões e depois volte a esta página.
          </div>
        ) : null}

        <section className="grid gap-3">
          {(sources.data ?? []).map((source) => (
            <Link
              className="rounded-lg border border-white/10 bg-white/[0.035] p-5 transition hover:border-signal-cyan/40 hover:bg-white/[0.055]"
              href={`/sources/${encodeURIComponent(source.id)}`}
              key={source.id}
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <h3 className="text-base font-semibold text-white">{source.display_name ?? source.name}</h3>
                  <p className="mt-2 break-all text-xs text-slate-500">{source.id}</p>
                  <p className="mt-3 text-sm text-slate-400">{source.extension_name ?? "Extensão instalada"}</p>
                </div>
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="rounded-md bg-white/[0.06] px-2.5 py-1 text-slate-300">
                    {source.language ?? "idioma desconhecido"}
                  </span>
                  <span className="rounded-md bg-white/[0.06] px-2.5 py-1 text-slate-300">{source.status}</span>
                </div>
              </div>
            </Link>
          ))}
        </section>
      </div>
    </AppShell>
  );
}
