import { redirect } from "next/navigation";
import { LoginForm } from "@/components/login-form";
import { getCurrentUser } from "@/lib/auth";

export const dynamic = "force-dynamic";

export default async function LoginPage() {
  const user = await getCurrentUser();
  if (user) {
    redirect("/");
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-10">
      <section className="w-full max-w-md rounded-lg border border-white/10 bg-ink-850/85 p-6 shadow-panel sm:p-8">
        <p className="text-sm font-medium text-signal-cyan">reader.hflow</p>
        <h1 className="mt-3 text-3xl font-semibold text-white">PanelFlow</h1>
        <p className="mt-3 text-sm leading-6 text-slate-400">
          Sign in with the private admin account configured for this instance.
        </p>

        <div className="mt-8">
          <LoginForm />
        </div>
      </section>
    </main>
  );
}
