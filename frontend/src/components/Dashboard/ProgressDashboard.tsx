import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Flame, Trophy, CheckCircle, XCircle } from 'lucide-react';

interface UserStats {
  streak: number;
  total_solved: number;
  accuracy: number;
  weak_topics: string[];
}

export const ProgressDashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);

  useEffect(() => {
    const fetchProgress = async () => {
      if (!user) return;
      try {
        const token = await user.getIdToken();
        const response = await fetch('http://localhost:8080/api/v1/progress', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          // accuracy and weak_topics can remain mocked for now, or computed
          setStats({
            streak: data.streak || 0,
            total_solved: data.total_solved || 0,
            accuracy: 85,
            weak_topics: ["Quadratic Equations", "Trigonometry"]
          });
        }
      } catch (err) {
        console.error("Failed to fetch progress", err);
        // Fallback to mock if backend not reachable
        setStats({ streak: 0, total_solved: 0, accuracy: 0, weak_topics: [] });
      }
    };
    fetchProgress();
  }, [user]);

  if (!stats) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading dashboard...</div>;

  return (
    <div className="main-content" style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto', width: '100%' }}>
      <h2 style={{ marginBottom: '2rem' }}>Learning Progress</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="glass" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ backgroundColor: 'hsla(38, 92%, 50%, 0.1)', padding: '1rem', borderRadius: '50%', color: 'hsl(var(--warning))' }}>
            <Flame size={32} />
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', color: 'hsl(var(--text-secondary))' }}>Current Streak</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{stats.streak} Days</div>
          </div>
        </div>
        
        <div className="glass" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ backgroundColor: 'hsla(217, 91%, 60%, 0.1)', padding: '1rem', borderRadius: '50%', color: 'hsl(var(--accent-primary))' }}>
            <Trophy size={32} />
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', color: 'hsl(var(--text-secondary))' }}>Total Solved</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{stats.total_solved}</div>
          </div>
        </div>

        <div className="glass" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ backgroundColor: 'hsla(142, 76%, 36%, 0.1)', padding: '1rem', borderRadius: '50%', color: 'hsl(var(--success))' }}>
            <CheckCircle size={32} />
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', color: 'hsl(var(--text-secondary))' }}>Accuracy</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{stats.accuracy}%</div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="glass" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Activity Heatmap</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '0.5rem' }}>
            {/* Mock calendar squares */}
            {Array.from({ length: 28 }).map((_, i) => (
              <div key={i} style={{ 
                aspectRatio: '1', 
                backgroundColor: Math.random() > 0.3 ? 'hsl(var(--success))' : 'hsl(var(--bg-secondary))',
                borderRadius: '4px',
                opacity: Math.random() > 0.5 ? 1 : 0.4
              }}></div>
            ))}
          </div>
        </div>

        <div className="glass" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Topics to Review</h3>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {stats.weak_topics.map((topic, i) => (
              <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem', backgroundColor: 'hsla(0, 84%, 60%, 0.1)', color: 'hsl(var(--danger))', borderRadius: 'var(--radius)' }}>
                <XCircle size={20} />
                <span style={{ fontWeight: 500 }}>{topic}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
