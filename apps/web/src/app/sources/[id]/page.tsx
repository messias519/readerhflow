import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { getAuthToken, requireCurrentUser } from "@/lib/auth";
import { fetchPanelFlow, type SourceSummary } from "@/lib/panelflow";

export const dynamic = "force-dynamic";

type SourcePageProps = {
  params: Promise<{ id: string }>;
};

export default async function SourcePage({ params }: SourcePageProps) {
  const [{ id }, user, token] = await Promise.all([params, requireCurrentUser(), getAuthToken()]);
  const source = await fetchPanelFlow<SourceSummary>(`/api/sources/${encodeURIComponent(id)}`, token);

  return (
    <AppShell title="Fonte" user={user}>
      {source.error || !source.data ? (
        <div className="rounded-lg border border-red-300/20 bg-red-400/10 p-5 text-sm text-red-100">
          {source.error ?? "Fonte não encontrada."}
        </div>
      ) : (
        <div className="grid gap-5">
          <section className="rounded-lg border border-white/10 bg-ink-850/75 p-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0">
                <p className="text-sm text-signal-cyan">{source.data.language ?? "idioma desconhecido"}</p>
                <h3 className="mt-2 text-2xl font-semibold text-white">
                  {source.data.display_name ?? source.data.name}
                </h3>
                <p className="mt-3 break-all text-sm text-slate-500">{source.data.id}</p>
              </div>
              <Link
                className="rounded-lg bg-signal-cyan px-4 py-2 text-sm font-semibold text-ink-950 transition hover:bg-cyan-200"
                href={`/search?source_id=${encodeURIComponent(source.data.id)}`}
              >
                Buscar nesta fonte
              </Link>
            </div>
          </section>

          <dl className="grid gap-3 sm:grid-cols-2">
            {[
              ["Extensão", source.data.extension_name ?? "Não informado"],
              ["Pacote", source.data.extension_package ?? "Não informado"],
              ["Status", source.data.status],
              ["Latest", source.data.supports_latest ? "Suportado" : "Não informado"],
            ].map(([label, value]) => (
              <div className="rounded-lg border border-white/10 bg-white/[0.035] p-4" key={label}>
                <dt className="text-xs text-slate-500">{label}</dt>
                <dd className="mt-2 break-words text-sm text-slate-200">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </AppShell>
  );
}
