"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";

export function LogoutButton() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  async function handleLogout() {
    await fetch("/api/auth/logout", {
      method: "POST",
    });

    startTransition(() => {
      router.replace("/login");
      router.refresh();
    });
  }

  return (
    <button
      className="rounded-lg border border-white/10 bg-white/[0.035] px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-white/20 hover:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-70"
      disabled={isPending}
      onClick={handleLogout}
      type="button"
    >
      {isPending ? "Signing out..." : "Logout"}
    </button>
  );
}
