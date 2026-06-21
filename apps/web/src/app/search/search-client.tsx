"use client";

import { FormEvent, useMemo, useState, useTransition } from "react";
import { CoverImage } from "@/components/cover-image";
import type { LibraryItem, SearchResponse, SearchResult, SourceSummary } from "@/lib/panelflow";

function messageFromPayload(payload: unknown, fallback: string) {
  if (payload && typeof payload === "object") {
    const detail = (payload as { detail?: unknown }).detail;
    if (detail && typeof detail === "object" && "message" in detail) {
      const message = (detail as { message?: unknown }).message;
      if (typeof message === "string") {
        return message;
      }
    }
    const message = (payload as { message?: unknown }).message;
    if (typeof message === "string") {
      return message;
    }
  }
  return fallback;
}

type SearchClientProps = {
  sources: SourceSummary[];
  initialSourceId?: string;
};

export function SearchClient({ sources, initialSourceId = "" }: SearchClientProps) {
  const [sourceId, setSourceId] = useState(initialSourceId);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState("");
  const [added, setAdded] = useState<Record<string, number>>({});
  const [isPending, startTransition] = useTransition();

  const sourceNameById = useMemo(() => {
    return new Map(sources.map((source) => [source.id, source.display_name ?? source.name]));
  }, [sources]);

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResults([]);

    startTransition(async () => {
      const params = new URLSearchParams({ source_id: sourceId, query });
      const response = await fetch(`/api/search?${params.toString()}`);
      const payload = await response.json().catch(() => null);

      if (!response.ok) {
        setError(messageFromPayload(payload, "Não foi possível pesquisar essa fonte."));
        return;
      }

      setResults((payload as SearchResponse).results);
    });
  }

  async function addToLibrary(result: SearchResult) {
    setError("");
    const response = await fetch("/api/library/external", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(result),
    });
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      setError(messageFromPayload(payload, "Não foi possível adicionar à biblioteca."));
      return;
    }

    const item = payload as LibraryItem;
    setAdded((current) => ({ ...current, [`${result.source_id}:${result.external_id}`]: item.id }));
  }

  return (
    <div className="grid gap-6">
      <form className="grid gap-3 rounded-lg border border-white/10 bg-ink-850/75 p-5 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)_auto]" onSubmit={handleSearch}>
        <label className="grid gap-2 text-sm text-slate-300">
          Fonte
          <select
            className="h-11 rounded-lg border border-white/10 bg-ink-900 px-3 text-sm text-white outline-none focus:border-signal-cyan"
            onChange={(event) => setSourceId(event.target.value)}
            required
            value={sourceId}
          >
            <option value="">Escolha uma fonte</option>
            {sources.map((source) => (
              <option key={source.id} value={source.id}>
                {source.display_name ?? source.name} ({source.language ?? "?"})
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-2 text-sm text-slate-300">
          Termo
          <input
            className="h-11 rounded-lg border border-white/10 bg-ink-900 px-3 text-sm text-white outline-none focus:border-signal-cyan"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Ex: Solo Leveling"
            required
            value={query}
          />
        </label>

        <button
          className="h-11 self-end rounded-lg bg-signal-cyan px-5 text-sm font-semibold text-ink-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
          disabled={isPending || sources.length === 0}
          type="submit"
        >
          {isPending ? "Buscando..." : "Buscar"}
        </button>
      </form>

      {sources.length === 0 ? (
        <div className="rounded-lg border border-white/10 bg-white/[0.035] p-5 text-sm leading-6 text-slate-300">
          Nenhuma fonte disponível. Instale extensões no Suwayomi e atualize esta página.
        </div>
      ) : null}

      {error ? (
        <div className="rounded-lg border border-red-300/20 bg-red-400/10 p-4 text-sm text-red-100">{error}</div>
      ) : null}

      {!isPending && results.length === 0 && query ? (
        <div className="rounded-lg border border-white/10 bg-white/[0.035] p-5 text-sm text-slate-400">
          Nenhum resultado para esta busca.
        </div>
      ) : null}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {results.map((result) => {
          const key = `${result.source_id}:${result.external_id}`;
          const addedId = added[key];
          return (
            <article className="overflow-hidden rounded-lg border border-white/10 bg-white/[0.035]" key={key}>
              <div className="aspect-[3/4] bg-ink-900">
                <CoverImage alt={result.title} coverUrl={result.cover_url} />
              </div>
              <div className="grid gap-3 p-4">
                <div>
                  <h3 className="line-clamp-2 text-base font-semibold text-white">{result.title}</h3>
                  <p className="mt-2 text-xs text-slate-500">
                    {result.source_name ?? sourceNameById.get(result.source_id) ?? result.source_id}
                  </p>
                </div>
                <button
                  className="h-10 rounded-lg border border-white/10 bg-white/[0.04] px-3 text-sm font-medium text-slate-100 transition hover:border-signal-cyan/40 disabled:cursor-default disabled:opacity-70"
                  disabled={Boolean(addedId)}
                  onClick={() => addToLibrary(result)}
                  type="button"
                >
                  {addedId ? "Na biblioteca" : "Adicionar à biblioteca"}
                </button>
              </div>
            </article>
          );
        })}
      </section>
    </div>
  );
}
