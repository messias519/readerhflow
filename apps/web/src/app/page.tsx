import { StatusCard } from "@/components/status-card";
import { fetchApiStatus } from "@/lib/status";

export const dynamic = "force-dynamic";

const services = [
  {
    key: "app",
    title: "API",
    description: "FastAPI service reachable from the web container.",
  },
  {
    key: "database",
    title: "Database",
    description: "PostgreSQL 16 connectivity check with a lightweight query.",
  },
  {
    key: "redis",
    title: "Redis",
    description: "Redis 7 cache and queue dependency ping.",
  },
  {
    key: "suwayomi",
    title: "Suwayomi",
    description: "Internal Suwayomi Server connection used for future source features.",
  },
  {
    key: "storage",
    title: "Storage",
    description: "Library path exists and accepts writes at /data/library.",
  },
] as const;

export default async function Home() {
  const status = await fetchApiStatus();
  const checkedAt = new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(status.checked_at));

  return (
    <main className="min-h-screen px-5 py-6 sm:px-8 lg:px-10">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8">
        <header className="flex flex-col gap-5 border-b border-white/10 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium text-signal-cyan">reader.hflow</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-normal text-white sm:text-4xl">PanelFlow</h1>
          </div>
          <div className="rounded-lg border border-white/10 bg-ink-850/80 px-4 py-3 text-sm text-slate-300">
            Infrastructure status
          </div>
        </header>

        <section className="grid gap-4 lg:grid-cols-[1.4fr_0.8fr]">
          <div className="rounded-lg border border-white/10 bg-ink-850/75 p-6 shadow-panel">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-sm text-slate-400">Overall health</p>
                <h2 className="mt-2 text-2xl font-semibold capitalize text-white">{status.status}</h2>
              </div>
              <p className="text-sm text-slate-400">Checked at {checkedAt} UTC</p>
            </div>
            <p className="mt-5 max-w-2xl text-sm leading-6 text-slate-300">
              Phase 1 is limited to infrastructure visibility. Auth, uploads, readers, source browsing, PDF, CBZ
              and offline PWA behavior are intentionally not implemented yet.
            </p>
          </div>

          <aside className="rounded-lg border border-white/10 bg-white/[0.035] p-6">
            <h2 className="text-base font-semibold text-white">Production target</h2>
            <dl className="mt-5 grid gap-4 text-sm">
              <div>
                <dt className="text-slate-500">Domain</dt>
                <dd className="mt-1 text-slate-200">reader.hflow.top</dd>
              </div>
              <div>
                <dt className="text-slate-500">Proxy route</dt>
                <dd className="mt-1 text-slate-200">NPM to panelflow-web:3000</dd>
              </div>
              <div>
                <dt className="text-slate-500">External network</dt>
                <dd className="mt-1 text-slate-200">npm_default</dd>
              </div>
            </dl>
          </aside>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          {services.map((item) => (
            <StatusCard
              key={item.key}
              service={status.services[item.key]}
              title={item.title}
              description={item.description}
            />
          ))}
        </section>
      </div>
    </main>
  );
}
