import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { CoverImage } from "@/components/cover-image";
import { getAuthToken, requireCurrentUser } from "@/lib/auth";
import { fetchPanelFlow, type LibraryItem } from "@/lib/panelflow";

export const dynamic = "force-dynamic";

export default async function LibraryPage() {
  const [user, token] = await Promise.all([requireCurrentUser(), getAuthToken()]);
  const library = await fetchPanelFlow<LibraryItem[]>("/api/library", token);

  return (
    <AppShell title="Biblioteca" user={user}>
      {library.error ? (
        <div className="rounded-lg border border-red-300/20 bg-red-400/10 p-5 text-sm text-red-100">
          {library.error}
        </div>
      ) : null}

      {!library.error && library.data?.length === 0 ? (
        <div className="rounded-lg border border-white/10 bg-white/[0.035] p-5 text-sm leading-6 text-slate-300">
          Sua biblioteca ainda está vazia. Use a busca para salvar mangás e manhwas vindos do Suwayomi.
        </div>
      ) : null}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {(library.data ?? []).map((item) => (
          <Link
            className="overflow-hidden rounded-lg border border-white/10 bg-white/[0.035] transition hover:border-signal-cyan/40"
            href={`/library/${item.id}`}
            key={item.id}
          >
            <div className="aspect-[3/4] bg-ink-900">
              <CoverImage alt={item.title} coverUrl={item.cover_url} />
            </div>
            <div className="p-4">
              <h3 className="line-clamp-2 text-base font-semibold text-white">{item.title}</h3>
              <p className="mt-2 break-all text-xs text-slate-500">{item.source_id}</p>
              <p className="mt-3 text-sm text-slate-300">{item.status ?? "status desconhecido"}</p>
            </div>
          </Link>
        ))}
      </section>
    </AppShell>
  );
}
