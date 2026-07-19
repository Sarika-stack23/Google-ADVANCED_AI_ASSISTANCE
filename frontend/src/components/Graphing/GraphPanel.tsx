import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import * as math from 'mathjs';

export const GraphPanel: React.FC = () => {
  const [expression, setExpression] = useState('sin(x)');
  const [inputVal, setInputVal] = useState('sin(x)');
  const [error, setError] = useState('');
  const [domain] = useState({ min: -10, max: 10 });

  const data = useMemo(() => {
    try {
      const compiled = math.compile(expression);
      const points = [];
      const step = (domain.max - domain.min) / 100;

      for (let x = domain.min; x <= domain.max; x += step) {
        try {
          const y = compiled.evaluate({ x });
          if (typeof y === 'number' && !isNaN(y) && isFinite(y)) {
            // Cap extreme values to prevent recharts from crashing or zooming out too much
            const cappedY = Math.max(-50, Math.min(50, y));
            points.push({ x: Number(x.toFixed(2)), y: Number(cappedY.toFixed(2)) });
          }
        } catch {
          // Skip invalid points for this x
        }
      }
      setError('');
      return points;
    } catch (e: any) {
      setError(e.message || 'Invalid mathematical expression');
      return [];
    }
  }, [expression, domain]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setExpression(inputVal);
  };

  return (
    <div className="main-content" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ marginBottom: '1.5rem' }}>📈 Interactive Graphing</h2>
      
      <div className="glass" style={{ padding: '1.5rem', marginBottom: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '300px' }}>
            <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Graphing</h3>
            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <label style={{ fontWeight: 'bold' }}>f(x) = </label>
            <input 
                type="text" 
                className="input" 
                style={{ flex: 1 }}
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                placeholder="e.g. x^2 + 2x - 1"
            />
            <button type="submit" className="btn btn-primary">Plot</button>
            </form>
            {error && <p style={{ color: '#ef4444', marginTop: '0.5rem', fontSize: '0.9rem' }}>{error}</p>}
        </div>
        <div style={{ flex: 1, minWidth: '300px', borderLeft: '1px solid var(--border)', paddingLeft: '1rem' }}>
            <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>⚡ Symbolic Compute</h3>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <button className="btn btn-outline" onClick={async () => {
                    try {
                        const res = await fetch(import.meta.env.VITE_API_URL + '/api/v1/symbolic', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ expression: expression, operation: 'differentiate' })
                        });
                        const data = await res.json();
                        alert(`Derivative: ${data.result}`);
                    } catch { alert('Error computing derivative'); }
                }}>d/dx</button>
                <button className="btn btn-outline" onClick={async () => {
                    try {
                        const res = await fetch(import.meta.env.VITE_API_URL + '/api/v1/symbolic', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ expression: expression, operation: 'integrate' })
                        });
                        const data = await res.json();
                        alert(`Integral: ${data.result}`);
                    } catch { alert('Error computing integral'); }
                }}>∫ dx</button>
                <button className="btn btn-outline" onClick={async () => {
                    try {
                        const res = await fetch(import.meta.env.VITE_API_URL + '/api/v1/symbolic', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ expression: expression, operation: 'solve' })
                        });
                        const data = await res.json();
                        alert(`Roots (f(x)=0): ${data.result}`);
                    } catch { alert('Error finding roots'); }
                }}>Solve f(x)=0</button>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                Computes exact symbolic math for the current `f(x)` function using SymPy.
            </p>
        </div>
      </div>

      <div className="glass" style={{ flex: 1, padding: '1rem', minHeight: '400px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                  dataKey="x" 
                  type="number" 
                  domain={['dataMin', 'dataMax']} 
                  stroke="var(--text-secondary)" 
                  tickFormatter={(val) => val.toFixed(1)}
              />
              <YAxis 
                  stroke="var(--text-secondary)" 
                  domain={['auto', 'auto']}
              />
              <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '8px' }}
                  labelFormatter={(val) => `x = ${val}`}
                  formatter={(val: any) => [`y = ${val}`, '']}
              />
              <ReferenceLine y={0} stroke="rgba(255,255,255,0.3)" />
              <ReferenceLine x={0} stroke="rgba(255,255,255,0.3)" />
              <Line 
                  type="monotone" 
                  dataKey="y" 
                  stroke="hsl(var(--accent-primary))" 
                  strokeWidth={3} 
                  dot={false}
                  isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p style={{ color: 'var(--text-secondary)' }}>No data to display. Please check your expression.</p>
        )}
      </div>
    </div>
  );
};
