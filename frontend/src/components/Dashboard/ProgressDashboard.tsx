import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Flame, Trophy, CheckCircle, BookOpen, Star } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
interface UserStats {
  streak: number;
  total_solved: number;
  accuracy: number;
  weak_topics: string[];
  activity_map: Record<string, number>;
}

export const ProgressDashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);

  useEffect(() => {
    const fetchProgress = async () => {
      if (!user) {
        setStats({ streak: 0, total_solved: 0, accuracy: 0, weak_topics: [], activity_map: {} });
        return;
      }
      try {
        const token = await user.getIdToken();
        const response = await fetch(import.meta.env.VITE_API_URL + '/api/v1/progress', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setStats({
            streak: data.streak || 0,
            total_solved: data.total_solved || 0,
            accuracy: data.accuracy ?? 100,
            weak_topics: data.weak_topics || [],
            activity_map: data.activity_map || {}
          });
        } else {
          // API returned error (401, 500, etc.) — show empty stats instead of loading forever
          setStats({ streak: 0, total_solved: 0, accuracy: 0, weak_topics: [], activity_map: {} });
        }
      } catch (err) {
        console.error("Failed to fetch progress", err);
        setStats({ streak: 0, total_solved: 0, accuracy: 0, weak_topics: [], activity_map: {} });
      }
    };
    fetchProgress();
  }, [user]);

  if (!stats) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading dashboard...</div>;

  const chartData = Array.from({ length: 14 }).map((_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (13 - i));
    const dateStr = d.toISOString().split('T')[0];
    const shortDate = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    return {
      date: shortDate,
      solved: stats.activity_map[dateStr] || 0
    };
  });

  return (
    <div className="main-content" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
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

        <div className="glass" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ backgroundColor: 'hsla(280, 91%, 60%, 0.1)', padding: '1rem', borderRadius: '50%', color: '#a855f7' }}>
            <Star size={32} />
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', color: 'hsl(var(--text-secondary))' }}>Total Score</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{(stats.total_solved * 100) + (stats.streak * 50)}</div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="glass" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Activity Heatmap</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '0.5rem' }}>
            {Array.from({ length: 28 }).map((_, i) => {
              const d = new Date();
              d.setDate(d.getDate() - (27 - i));
              const dateStr = d.toISOString().split('T')[0];
              const count = stats.activity_map[dateStr] || 0;
              return (
                <div key={i} title={`${dateStr}: ${count} solved`} style={{ 
                  aspectRatio: '1', 
                  backgroundColor: count > 0 ? 'hsl(var(--success))' : 'hsl(var(--bg-secondary))',
                  borderRadius: '4px',
                  opacity: count > 0 ? Math.min(1, 0.4 + (count * 0.15)) : 0.5
                }}></div>
              );
            })}
          </div>
        </div>

        <div className="glass" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Topics to Review</h3>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {stats.weak_topics.length > 0 ? stats.weak_topics.map((topic, i) => (
              <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem', backgroundColor: 'hsla(217, 91%, 60%, 0.1)', color: 'hsl(var(--accent-primary))', borderRadius: 'var(--radius)' }}>
                <BookOpen size={20} />
                <span style={{ fontWeight: 500 }}>{topic}</span>
              </li>
            )) : (
              <p style={{ color: 'var(--text-secondary)' }}>You don't have any weak topics yet! Keep solving problems.</p>
            )}
          </ul>
        </div>
      </div>

      <div className="glass" style={{ padding: '1.5rem', marginTop: '1.5rem' }}>
        <h3 style={{ marginBottom: '1.5rem' }}>Problems Solved (Last 14 Days)</h3>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
              <YAxis stroke="rgba(255,255,255,0.5)" allowDecimals={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'hsl(var(--bg-primary))', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                itemStyle={{ color: 'hsl(var(--accent-primary))' }}
              />
              <Line type="monotone" dataKey="solved" name="Questions Solved" stroke="hsl(var(--accent-primary))" strokeWidth={3} dot={{ r: 4, fill: 'hsl(var(--accent-primary))' }} activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
