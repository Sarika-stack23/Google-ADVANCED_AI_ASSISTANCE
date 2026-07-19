import React, { createContext, useContext, useEffect, useState } from 'react';
import type { User } from 'firebase/auth';
import { GoogleAuthProvider, signInWithPopup, signInWithRedirect, getRedirectResult, signOut } from 'firebase/auth';
import { auth } from '../firebaseConfig';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check for redirect result first (when returning from Google sign-in)
    getRedirectResult(auth).catch((err) => {
      console.error("Redirect result error:", err);
      setError(err.message || "Failed to complete Google login");
    });

    const unsubscribe = auth.onAuthStateChanged((u) => {
      setUser(u);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    setError(null);
    const provider = new GoogleAuthProvider();
    try {
      // Try popup first (works on localhost)
      await signInWithPopup(auth, provider);
    } catch (err: any) {
      // If popup is blocked or fails, fall back to redirect (works on deployed sites)
      if (err?.code === 'auth/popup-blocked' || 
          err?.code === 'auth/popup-closed-by-user' ||
          err?.code === 'auth/cancelled-popup-request') {
        console.log("Popup blocked, using redirect...");
        await signInWithRedirect(auth, provider);
      } else {
        console.error("Error signing in with Google:", err);
        setError(err.message || "Authentication failed");
      }
    }
  };

  const logout = async () => {
    await signOut(auth);
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, signInWithGoogle, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);

