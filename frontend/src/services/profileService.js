import { apiClient } from "./apiClient.js";

export async function getProfile() {
  const response = await apiClient.get("/profile");
  return response.data;
}

export async function deleteProfile() {
  await apiClient.delete("/profile");
}
