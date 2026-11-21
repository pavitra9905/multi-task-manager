import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000",
});

// Attach the token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// If the server says the token is bad or expired, log out
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && localStorage.getItem("token")) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export function getErrorMessage(err) {
  const d = err.response?.data;
  if (!d) return "Cannot reach the server. Is the backend running?";
  if (d.error) return d.error;
  if (d.errors) {
    return Object.entries(d.errors)
      .map(([field, msgs]) => `${field}: ${[].concat(msgs).join(", ")}`)
      .join(" | ");
  }
  return "Something went wrong.";
}

export default api;