import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { MessageSquare, LayoutDashboard, BookOpen, LogOut, Calculator, LineChart, Menu, X } from 'lucide-react';
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
    <div className="login-container">
      <div className="login-mesh"></div>
      
      <div className="login-card">
        <div style={{ padding: '1rem', background: 'hsla(var(--accent-primary), 0.1)', borderRadius: '50%', marginBottom: '1.5rem' }}>
          <Calculator size={48} style={{ color: 'hsl(var(--accent-primary))' }} />
        </div>
        
        <h1 style={{ fontSize: '2.2rem', fontWeight: 700, marginBottom: '0.5rem', letterSpacing: '-0.02em' }}>
          Welcome to <span className="text-gradient">Math AI</span>
        </h1>
        
        <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '1.1rem', marginBottom: '2rem' }}>
          Your intelligent, personalized mathematics tutor powered by advanced AI.
        </p>

        <button className="google-btn" onClick={signInWithGoogle}>
          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google logo" />
          Continue with Google
        </button>
        
        <div style={{ marginTop: '2rem', fontSize: '0.85rem', color: 'hsl(var(--text-secondary))', opacity: 0.8 }}>
          By continuing, you agree to our Terms of Service and Privacy Policy.
        </div>
      </div>
    </div>
  );
};


const Sidebar: React.FC<{ isOpen: boolean, closeMenu: () => void }> = ({ isOpen, closeMenu }) => {
  const { logout, user } = useAuth();
  
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
    <>
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem', padding: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Calculator size={28} color="hsl(var(--accent-primary))" />
            <h2 style={{ fontSize: '1.2rem', margin: 0 }}>Math AI</h2>
          </div>
          {/* Close button for mobile inside sidebar */}
          <button className="btn btn-outline" onClick={closeMenu} style={{ display: isOpen ? 'flex' : 'none', border: 'none', padding: '4px' }}>
            <X size={20} />
          </button>
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
        <button onClick={() => { closeMenu(); logout(); }} className="btn btn-outline" style={{ width: '100%', justifyContent: 'flex-start' }}>
          <LogOut size={20} /> Sign out
        </button>
      </div>
    </div>
    {isOpen && (
      <div className="mobile-menu-overlay" style={{ display: 'block' }} onClick={closeMenu} />
    )}
    </>
  );
};

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  return (
    <div className="app-container">
      <Sidebar isOpen={isMobileMenuOpen} closeMenu={() => setIsMobileMenuOpen(false)} />
      <div className="main-content" style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
        {/* Mobile Header with Hamburger Menu */}
        <div className="mobile-header">
          <button className="btn btn-outline" onClick={() => setIsMobileMenuOpen(true)} style={{ padding: '0.5rem', border: 'none' }}>
            <Menu size={24} color="hsl(var(--text-primary))" />
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginLeft: '0.5rem' }}>
            <Calculator size={24} color="hsl(var(--accent-primary))" />
            <span style={{ fontWeight: 600, fontSize: '1.1rem' }}>Math AI</span>
          </div>
        </div>
        {/* Page Content */}
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          {children}
        </div>
      </div>
    </div>
  );
};

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
