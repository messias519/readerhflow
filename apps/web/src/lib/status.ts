import { apiBaseUrl } from "@/lib/api";

export type ServiceStatusValue = "ok" | "degraded" | "error" | "unknown";

export type ServiceStatus = {
  name: string;
  status: ServiceStatusValue;
  message?: string;
  latency_ms?: number;
  details?: Record<string, unknown>;
};

export type ApiStatus = {
  app: string;
  environment: string;
  status: ServiceStatusValue;
  checked_at: string;
  services: {
    app: ServiceStatus;
    database: ServiceStatus;
    redis: ServiceStatus;
    suwayomi: ServiceStatus;
    storage: ServiceStatus;
  };
};

const fallbackStatus: ApiStatus = {
  app: "PanelFlow",
  environment: "phase-3",
  status: "error",
  checked_at: new Date().toISOString(),
  services: {
    app: {
      name: "app",
      status: "error",
      message: "API is not reachable from the web container.",
    },
    database: { name: "database", status: "unknown" },
    redis: { name: "redis", status: "unknown" },
    suwayomi: { name: "suwayomi", status: "unknown" },
    storage: { name: "storage", status: "unknown" },
  },
};

export async function fetchApiStatus(): Promise<ApiStatus> {
  try {
    const response = await fetch(`${apiBaseUrl()}/api/status`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!response.ok) {
      return {
        ...fallbackStatus,
        services: {
          ...fallbackStatus.services,
          app: {
            ...fallbackStatus.services.app,
            message: `API returned HTTP ${response.status}.`,
          },
        },
      };
    }

    return (await response.json()) as ApiStatus;
  } catch (error) {
    return {
      ...fallbackStatus,
      services: {
        ...fallbackStatus.services,
        app: {
          ...fallbackStatus.services.app,
          message: error instanceof Error ? error.message : "Unknown API error.",
        },
      },
    };
  }
}
