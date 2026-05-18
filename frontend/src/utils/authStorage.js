const AUTH_SESSION_KEY = "safeflow_auth_session";

export function saveAuthSession(session) {
  localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(session));
}

export function getAuthSession() {
  const rawValue = localStorage.getItem(AUTH_SESSION_KEY);

  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue);
  } catch {
    clearAuthSession();
    return null;
  }
}

export function getStoredAccessToken() {
  return getAuthSession()?.accessToken || null;
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_SESSION_KEY);
}