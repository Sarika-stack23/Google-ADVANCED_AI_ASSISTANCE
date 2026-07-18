import React, { useState, useEffect } from 'react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [apiKey, setApiKey] = useState('');
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    const savedKey = localStorage.getItem('custom_gemini_api_key');
    if (savedKey) {
      setApiKey(savedKey);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = () => {
    if (apiKey.trim()) {
      localStorage.setItem('custom_gemini_api_key', apiKey.trim());
    } else {
      localStorage.removeItem('custom_gemini_api_key');
    }
    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
      onClose();
    }, 1000);
  };

  const handleClear = () => {
    setApiKey('');
    localStorage.removeItem('custom_gemini_api_key');
    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
      onClose();
    }, 1000);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      backdropFilter: 'blur(4px)'
    }}>
      <div className="glass animate-fade-in" style={{
        width: '400px',
        padding: '2rem',
        position: 'relative'
      }}>
        <button 
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            fontSize: '1.2rem'
          }}
        >
          ✕
        </button>
        
        <h3 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          ⚙️ Settings
        </h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
          Configure app preferences and API keys for evaluation.
        </p>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: 500 }}>
            Custom Gemini API Key
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="AIzaSy..."
            className="input"
            style={{ width: '100%', padding: '0.75rem' }}
          />
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
            If you provide a key here, it will bypass the backend's default free-tier API key. Useful for bypassing rate limits during testing.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
          <button className="btn btn-outline" onClick={handleClear} disabled={!apiKey && !localStorage.getItem('custom_gemini_api_key')}>
            Clear Key
          </button>
          <button className="btn btn-primary" onClick={handleSave} style={{ minWidth: '100px' }}>
            {isSaved ? '✅ Saved!' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};
