import type { ServiceStatus, ServiceStatusValue } from "@/lib/status";

const statusStyles: Record<ServiceStatusValue, { dot: string; label: string; text: string }> = {
  ok: {
    dot: "bg-signal-ok shadow-[0_0_20px_rgb(52_211_153_/_0.45)]",
    label: "bg-emerald-400/10 text-emerald-200 ring-emerald-300/20",
    text: "Operational",
  },
  degraded: {
    dot: "bg-signal-warn shadow-[0_0_20px_rgb(251_191_36_/_0.4)]",
    label: "bg-amber-400/10 text-amber-100 ring-amber-300/20",
    text: "Degraded",
  },
  error: {
    dot: "bg-signal-error shadow-[0_0_20px_rgb(248_113_113_/_0.45)]",
    label: "bg-red-400/10 text-red-100 ring-red-300/20",
    text: "Offline",
  },
  unknown: {
    dot: "bg-slate-500",
    label: "bg-slate-400/10 text-slate-200 ring-slate-300/20",
    text: "Unknown",
  },
};

type StatusCardProps = {
  service: ServiceStatus;
  title: string;
  description: string;
};

export function StatusCard({ service, title, description }: StatusCardProps) {
  const style = statusStyles[service.status] ?? statusStyles.unknown;

  return (
    <article className="rounded-lg border border-white/10 bg-white/[0.035] p-5 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-3">
            <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${style.dot}`} />
            <h2 className="text-base font-semibold text-white">{title}</h2>
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>
        </div>
        <span className={`shrink-0 rounded-md px-2.5 py-1 text-xs font-medium ring-1 ${style.label}`}>
          {style.text}
        </span>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-3 border-t border-white/10 pt-4 text-xs text-slate-400">
        {typeof service.latency_ms === "number" ? <span>{service.latency_ms} ms</span> : <span>No latency</span>}
        {service.message ? <span className="min-w-0 break-words text-red-200">{service.message}</span> : null}
      </div>
    </article>
  );
}
