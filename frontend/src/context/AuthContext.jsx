import { createContext, useContext, useEffect, useState } from "react";
import {
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
} from "../services/authService.js";
import {
  clearAuthSession,
  getAuthSession,
  saveAuthSession,
} from "../utils/authStorage.js";

const AuthContext = createContext(null);

function buildInitialState() {
  const storedSession = getAuthSession();

  return {
    user: storedSession?.user || null,
    accessToken: storedSession?.accessToken || null,
    tokenType: storedSession?.tokenType || "bearer",
    isInitializing: Boolean(storedSession?.accessToken),
  };
}

export function AuthProvider({ children }) {
  const [authState, setAuthState] = useState(buildInitialState);

  useEffect(() => {
    let isMounted = true;

    if (!authState.accessToken) {
      setAuthState((currentState) => ({
        ...currentState,
        isInitializing: false,
      }));
      return () => {
        isMounted = false;
      };
    }

    async function restoreSession() {
      try {
        const user = await getCurrentUser();

        if (!isMounted) {
          return;
        }

        const restoredSession = {
          accessToken: authState.accessToken,
          tokenType: authState.tokenType,
          user,
        };

        saveAuthSession(restoredSession);
        setAuthState({
          ...restoredSession,
          isInitializing: false,
        });
      } catch {
        if (!isMounted) {
          return;
        }

        clearAuthSession();
        setAuthState({
          user: null,
          accessToken: null,
          tokenType: "bearer",
          isInitializing: false,
        });
      }
    }

    restoreSession();

    return () => {
      isMounted = false;
    };
  }, [authState.accessToken, authState.tokenType]);

  function applySession(sessionPayload) {
    const nextSession = {
      accessToken: sessionPayload.accessToken,
      tokenType: sessionPayload.tokenType || "bearer",
      user: sessionPayload.user || null,
    };

    saveAuthSession(nextSession);
    setAuthState({
      ...nextSession,
      isInitializing: false,
    });

    return nextSession;
  }

  async function login(payload) {
    const sessionPayload = await loginRequest(payload);
    return applySession(sessionPayload);
  }

  async function register(payload) {
    const sessionPayload = await registerRequest(payload);
    return applySession(sessionPayload);
  }

  async function logout() {
    try {
      if (authState.accessToken) {
        await logoutRequest();
      }
    } finally {
      clearAuthSession();
      setAuthState({
        user: null,
        accessToken: null,
        tokenType: "bearer",
        isInitializing: false,
      });
    }
  }

  const value = {
    user: authState.user,
    accessToken: authState.accessToken,
    isAuthenticated: Boolean(authState.accessToken && authState.user),
    isInitializing: authState.isInitializing,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }

  return context;
}
