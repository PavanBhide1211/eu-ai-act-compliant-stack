// API URLs. Override at build time via VITE_* env vars if needed.

const env = (typeof import.meta !== "undefined" && import.meta.env) || {};

export const COMPLIANT_API =
  env.VITE_COMPLIANT_API || "http://localhost:8000";
export const TRADITIONAL_API =
  env.VITE_TRADITIONAL_API || "http://localhost:8001";
