import { apiClient } from "./apiClient.js";

export async function login(payload) {
  const response = await apiClient.post("/auth/login", payload);
  return response.data;
}

export async function signUp(payload) {
  const response = await apiClient.post("/auth/signup", payload);
  return response.data;
}

export async function recoverPassword(payload) {
  await apiClient.post("/auth/recover-password", payload);
}
