import { AppShell } from "@/components/app-shell";
import { CoverImage } from "@/components/cover-image";
import { getAuthToken, requireCurrentUser } from "@/lib/auth";
import { fetchPanelFlow, type LibraryItem } from "@/lib/panelflow";

export const dynamic = "force-dynamic";

type LibraryDetailPageProps = {
  params: Promise<{ id: string }>;
};

export default async function LibraryDetailPage({ params }: LibraryDetailPageProps) {
  const [{ id }, user, token] = await Promise.all([params, requireCurrentUser(), getAuthToken()]);
  const item = await fetchPanelFlow<LibraryItem>(`/api/library/${encodeURIComponent(id)}`, token);

  return (
    <AppShell title="Item da biblioteca" user={user}>
      {item.error || !item.data ? (
        <div className="rounded-lg border border-red-300/20 bg-red-400/10 p-5 text-sm text-red-100">
          {item.error ?? "Item não encontrado."}
        </div>
      ) : (
        <article className="grid gap-6 lg:grid-cols-[18rem_1fr]">
          <div className="overflow-hidden rounded-lg border border-white/10 bg-ink-900">
            <div className="aspect-[3/4]">
              <CoverImage alt={item.data.title} coverUrl={item.data.cover_url} />
            </div>
          </div>

          <div className="min-w-0">
            <p className="text-sm text-signal-cyan">{item.data.source_type}</p>
            <h3 className="mt-2 text-3xl font-semibold text-white">{item.data.title}</h3>
            {item.data.subtitle ? <p className="mt-2 text-slate-300">{item.data.subtitle}</p> : null}
            <p className="mt-5 max-w-3xl text-sm leading-6 text-slate-300">
              {item.data.description ?? "Sem descrição disponível nesta fase."}
            </p>

            <dl className="mt-6 grid gap-3 sm:grid-cols-2">
              {[
                ["Tipo", item.data.item_type],
                ["Status", item.data.status ?? "desconhecido"],
                ["Fonte", item.data.source_id],
                ["ID externo", item.data.external_id],
              ].map(([label, value]) => (
                <div className="rounded-lg border border-white/10 bg-white/[0.035] p-4" key={label}>
                  <dt className="text-xs text-slate-500">{label}</dt>
                  <dd className="mt-2 break-all text-sm text-slate-200">{value}</dd>
                </div>
              ))}
            </dl>

            {item.data.external_url ? (
              <a
                className="mt-6 inline-flex rounded-lg border border-white/10 px-4 py-2 text-sm font-medium text-slate-100 transition hover:border-signal-cyan/40"
                href={item.data.external_url}
                rel="noreferrer"
                target="_blank"
              >
                Abrir origem
              </a>
            ) : null}
          </div>
        </article>
      )}
    </AppShell>
  );
}
