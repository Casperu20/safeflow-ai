import axios from "axios";
import { getStoredAccessToken } from "../utils/authStorage.js";

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000,
  headers: {
    Accept: "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const accessToken = getStoredAccessToken();

  if (accessToken) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

export function getApiErrorMessage(error, fallbackMessage) {
  const responseData = error?.response?.data;

  if (
    typeof responseData?.message === "string" &&
    responseData.message.trim()
  ) {
    const detailMessages = Object.values(responseData.details || {})
      .flat()
      .filter((value) => typeof value === "string" && value.trim());

    if (detailMessages.length > 0) {
      return `${responseData.message} ${detailMessages[0]}`;
    }

    return responseData.message;
  }

  if (error?.code === "ERR_NETWORK") {
    return "Cannot reach the backend service. Check that the backend is running on http://127.0.0.1:8000.";
  }

  return fallbackMessage;
}
