import { apiClient } from "./apiClient.js";

export async function getHistory() {
  const response = await apiClient.get("/history");
  return response.data;
}
