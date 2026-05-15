import { apiClient } from "./apiClient.js";

export async function login(payload) {
  const response = await apiClient.post("/auth/login", payload);
  return response.data;
}

export async function register(payload) {
  const response = await apiClient.post("/auth/register", payload);
  return response.data;
}

export async function signUp(payload) {
  return register(payload);
}

export async function recoverPassword(payload) {
  const response = await apiClient.post("/auth/recover-password", payload);
  return response.data;
}

export async function getCurrentUser() {
  const response = await apiClient.get("/auth/me");
  return response.data;
}

export async function logout() {
  const response = await apiClient.post("/auth/logout");
  return response.data;
}
