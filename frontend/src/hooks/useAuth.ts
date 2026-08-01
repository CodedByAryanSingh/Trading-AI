import { useState, useEffect, useCallback } from "react";
import api from "@/lib/api";

interface User { id: number; username: string; email: string; }

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) { setLoading(false); return; }
    try {
      const res = await api.get("/auth/me");
      setUser(res.data);
    } catch { localStorage.removeItem("token"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchUser(); }, [fetchUser]);

  const login = async (username: string, password: string) => {
    const res = await api.post("/auth/login", { username, password });
    localStorage.setItem("token", res.data.access_token);
    await fetchUser();
  };

  const register = async (username: string, email: string, password: string) => {
    const res = await api.post("/auth/register", { username, email, password });
    localStorage.setItem("token", res.data.access_token);
    await fetchUser();
  };

  const logout = () => { localStorage.removeItem("token"); setUser(null); };

  return { user, loading, login, register, logout };
}
