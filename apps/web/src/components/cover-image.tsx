import { coverSrc } from "@/lib/panelflow";

type CoverImageProps = {
  alt: string;
  coverUrl?: string | null;
};

export function CoverImage({ alt, coverUrl }: CoverImageProps) {
  const src = coverSrc(coverUrl);

  if (!src) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-white/[0.04] text-xs text-slate-500">
        Sem capa
      </div>
    );
  }

  return <img alt={alt} className="h-full w-full object-cover" referrerPolicy="no-referrer" src={src} />;
}
