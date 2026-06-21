import type { ReactNode } from "react";
import type { AuthUser } from "@/lib/auth";
import { AppNav } from "@/components/app-nav";
import { LogoutButton } from "@/components/logout-button";

type AppShellProps = {
  children: ReactNode;
  title: string;
  eyebrow?: string;
  user: AuthUser;
};

export function AppShell({ children, title, eyebrow = "reader.hflow", user }: AppShellProps) {
  return (
    <main className="min-h-screen px-5 py-6 sm:px-8 lg:px-10">
      <div className="mx-auto grid w-full max-w-7xl gap-6 lg:grid-cols-[14rem_1fr]">
        <aside className="lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)]">
          <div className="flex h-full flex-col gap-5 border-b border-white/10 pb-5 lg:border-b-0 lg:border-r lg:pb-0 lg:pr-5">
            <div>
              <p className="text-sm font-medium text-signal-cyan">{eyebrow}</p>
              <h1 className="mt-2 text-2xl font-semibold text-white">PanelFlow</h1>
            </div>
            <AppNav />
            <div className="mt-auto hidden text-xs leading-5 text-slate-500 lg:block">
              Suwayomi roda internamente. O navegador fala apenas com a API PanelFlow.
            </div>
          </div>
        </aside>

        <section className="min-w-0">
          <header className="mb-6 flex flex-col gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <p className="text-sm text-slate-400">{user.email}</p>
              <h2 className="mt-2 text-3xl font-semibold text-white">{title}</h2>
            </div>
            <LogoutButton />
          </header>
          {children}
        </section>
      </div>
    </main>
  );
}
