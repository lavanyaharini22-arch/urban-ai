import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const token = sessionStorage.getItem("token");
    const name = sessionStorage.getItem("name");
    const email = sessionStorage.getItem("email");
    return token ? { token, name, email } : null;
  });

  useEffect(() => {
    if (auth) {
      sessionStorage.setItem("token", auth.token);
      sessionStorage.setItem("name", auth.name || "");
      sessionStorage.setItem("email", auth.email || "");
    } else {
      sessionStorage.removeItem("token");
      sessionStorage.removeItem("name");
      sessionStorage.removeItem("email");
    }
  }, [auth]);

  const login = (data) => setAuth(data);
  const logout = () => setAuth(null);

  return (
    <AuthContext.Provider value={{ auth, login, logout, isAuthenticated: !!auth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
