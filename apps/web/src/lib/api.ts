export function apiBaseUrl() {
  return process.env.API_INTERNAL_URL ?? "http://api:8000";
}
