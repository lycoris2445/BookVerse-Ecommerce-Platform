// src/services/api.js
import axios from "axios";

export const API_BASE =
  process.env.REACT_APP_API_BASE_URL ||
  (process.env.NODE_ENV === 'production' 
    ? 'https://ecomtech.onrender.com/api/v1'
    : 'http://localhost:8000/api/v1'); // only for local dev

const api = axios.create({
  baseURL: API_BASE,           // <-- ĐÃ có /api/v1
  withCredentials: false,      // chỉ bật true nếu cần cookie/session
});

// Chỉ gắn Authorization cho endpoint cần auth
const NO_AUTH_PREFIXES = [
  "/catalog/categories",
  "/catalog/books",
  "/healthz",
  "/swagger", "/schema", "/docs"
];

api.interceptors.request.use((config) => {
  const needAuth = !NO_AUTH_PREFIXES.some((p) => config.url?.startsWith(p));
  const token = localStorage.getItem("accessToken");
  if (needAuth && token) {
    config.headers.Authorization = `Bearer ${token}`;
  } else {
    // với GET/public đừng tự set Content-Type → tránh preflight
    if (config.method?.toLowerCase() === "get") {
      delete config.headers["Content-Type"];
    }
  }
  return config;
});

if (import.meta?.env?.MODE === "development" || process.env.NODE_ENV !== "production") {
  // Debug: in ra base URL 1 lần
  // eslint-disable-next-line no-console
  console.log("[API_BASE]", API_BASE);
}

export default api;
