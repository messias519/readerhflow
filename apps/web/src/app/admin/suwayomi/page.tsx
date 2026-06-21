import { AppShell } from "@/components/app-shell";
import { requireCurrentUser } from "@/lib/auth";

export const dynamic = "force-dynamic";

export default async function AdminSuwayomiPage() {
  const user = await requireCurrentUser();
  const isAdmin = user.role === "admin";

  return (
    <AppShell title="Admin Suwayomi" user={user}>
      {!isAdmin ? (
        <div className="rounded-lg border border-red-300/20 bg-red-400/10 p-5 text-sm text-red-100">
          Apenas administradores podem acessar o painel interno do Suwayomi.
        </div>
      ) : (
        <div className="grid gap-5">
          <section className="rounded-lg border border-amber-300/20 bg-amber-400/10 p-5 text-sm leading-6 text-amber-100">
            Esta área administra o Suwayomi interno usado para fontes/extensões. Use apenas em ambiente privado.
          </section>

          <div className="overflow-hidden rounded-lg border border-white/10 bg-ink-950 shadow-panel">
            <div className="flex flex-col gap-3 border-b border-white/10 bg-ink-850/90 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-slate-300">WebUI via proxy protegido do PanelFlow</p>
              <a
                className="rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-medium text-slate-100 transition hover:border-signal-cyan/40"
                href="/api/admin/suwayomi"
                rel="noreferrer"
                target="_blank"
              >
                Abrir painel Suwayomi protegido
              </a>
            </div>
            <iframe
              className="h-[75vh] w-full bg-white"
              referrerPolicy="same-origin"
              sandbox="allow-forms allow-modals allow-popups allow-same-origin allow-scripts"
              src="/api/admin/suwayomi"
              title="Suwayomi WebUI"
            />
          </div>
        </div>
      )}
    </AppShell>
  );
}
