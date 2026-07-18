import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { MessageSquare, LayoutDashboard, BookOpen, LogOut, Calculator, LineChart } from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ChatInterface } from './components/Chat/ChatInterface';
import { ProgressDashboard } from './components/Dashboard/ProgressDashboard';
import { NCERTQuizPanel } from './components/Quiz/NCERTQuizPanel';
import { GraphPanel } from './components/Graphing/GraphPanel';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  return <>{children}</>;
};

const Login: React.FC = () => {
  const { signInWithGoogle, user } = useAuth();
  if (user) return <Navigate to="/" />;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', gap: '2rem' }}>
      <div style={{ textAlign: 'center' }}>
        <Calculator size={48} style={{ color: 'hsl(var(--accent-primary))', marginBottom: '1rem' }} />
        <h1>Advanced Math Assistant</h1>
        <p style={{ color: 'hsl(var(--text-secondary))', marginTop: '0.5rem' }}>Your personal AI math tutor</p>
      </div>
      <button className="btn btn-primary" onClick={signInWithGoogle} style={{ padding: '1rem 2rem', fontSize: '1.1rem' }}>
        Sign in with Google
      </button>
    </div>
  );
};

import { SettingsModal } from './components/SettingsModal';

const Sidebar: React.FC = () => {
  const { logout, user } = useAuth();
  const [isSettingsOpen, setIsSettingsOpen] = React.useState(false);
  
  const navStyle = ({ isActive }: { isActive: boolean }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.75rem 1rem',
    borderRadius: 'var(--radius)',
    textDecoration: 'none',
    color: isActive ? 'hsl(var(--accent-primary))' : 'hsl(var(--text-primary))',
    backgroundColor: isActive ? 'hsla(var(--accent-primary), 0.1)' : 'transparent',
    fontWeight: isActive ? 600 : 400,
    transition: 'all 0.2s'
  });

  return (
    <div className="sidebar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem', padding: '0.5rem' }}>
        <Calculator size={28} color="hsl(var(--accent-primary))" />
        <h2 style={{ fontSize: '1.2rem', margin: 0 }}>Math AI</h2>
      </div>
      
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        <NavLink to="/" style={navStyle} end>
          <MessageSquare size={20} /> Chat
        </NavLink>
        <NavLink to="/quiz" style={navStyle}>
          <BookOpen size={20} /> NCERT Quiz
        </NavLink>
        <NavLink to="/graph" style={navStyle}>
          <LineChart size={20} /> Graphing
        </NavLink>
        <NavLink to="/dashboard" style={navStyle}>
          <LayoutDashboard size={20} /> Dashboard
        </NavLink>
      </nav>

      <div style={{ borderTop: '1px solid hsl(var(--border))', paddingTop: '1rem', marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div style={{ padding: '0.5rem', fontSize: '0.9rem', color: 'hsl(var(--text-secondary))', marginBottom: '0.5rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {user?.email}
        </div>
        <button onClick={() => setIsSettingsOpen(true)} className="btn btn-outline" style={{ width: '100%', justifyContent: 'flex-start' }}>
          ⚙️ Settings
        </button>
        <button onClick={logout} className="btn btn-outline" style={{ width: '100%', justifyContent: 'flex-start' }}>
          <LogOut size={20} /> Sign out
        </button>
      </div>
      
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </div>
  );
};

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="app-container">
    <Sidebar />
    {children}
  </div>
);

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><AppLayout><ChatInterface /></AppLayout></ProtectedRoute>} />
          <Route path="/quiz" element={<ProtectedRoute><AppLayout><NCERTQuizPanel /></AppLayout></ProtectedRoute>} />
          <Route path="/graph" element={<ProtectedRoute><AppLayout><GraphPanel /></AppLayout></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><AppLayout><ProgressDashboard /></AppLayout></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
