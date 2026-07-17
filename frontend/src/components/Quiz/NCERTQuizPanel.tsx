import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import Latex from 'react-latex-next';
import 'katex/dist/katex.min.css';

interface QuizState {
  currentQuestion: string;
  feedback: string;
  showStuckMenu: boolean;
}

export const NCERTQuizPanel: React.FC = () => {
  const { user } = useAuth();
  const [state, setState] = useState<QuizState>({
    currentQuestion: "Find the roots of the quadratic equation: x^2 - 5x + 6 = 0",
    feedback: "",
    showStuckMenu: false
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleAction = async (action: string) => {
    if (!user) return;
    setIsLoading(true);
    
    try {
      const token = await user.getIdToken();
      // Use existing prompt service for quiz actions
      const response = await fetch(`http://localhost:8080/api/v1/prompt/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ action, context: state.currentQuestion })
      });
      
      const data = await response.json();
      setState(prev => ({ ...prev, feedback: data.response, showStuckMenu: false }));
    } catch (e) {
      console.error(e);
      setState(prev => ({ ...prev, feedback: "Failed to fetch response." }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="main-content" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
      <h2>NCERT Exercise 6.1 (Class 10)</h2>
      
      <div className="glass" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <h3>Question 1</h3>
        <p style={{ fontSize: '1.2rem', marginTop: '1rem' }}>
          <Latex>{state.currentQuestion}</Latex>
        </p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <button className="btn btn-outline" onClick={() => handleAction('hint')} disabled={isLoading}>Give me a hint</button>
        <button className="btn btn-outline" onClick={() => handleAction('steps')} disabled={isLoading}>Show first step</button>
        <button className="btn btn-outline" onClick={() => handleAction('answer')} disabled={isLoading}>Show answer</button>
        <button className="btn btn-primary" onClick={() => setState(prev => ({ ...prev, showStuckMenu: !prev.showStuckMenu }))}>Ask AI (Stuck?)</button>
      </div>

      {state.showStuckMenu && (
        <div className="glass animate-fade-in" style={{ padding: '1.5rem', marginBottom: '1.5rem', backgroundColor: 'var(--bg-secondary)' }}>
          <h4 style={{ marginBottom: '1rem' }}>I'm stuck because...</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <button className="btn btn-outline" onClick={() => handleAction('explain_concept')} style={{ justifyContent: 'flex-start' }}>I don't understand the underlying concept.</button>
            <button className="btn btn-outline" onClick={() => handleAction('similar_example')} style={{ justifyContent: 'flex-start' }}>Can you show me a similar solved example?</button>
            <button className="btn btn-outline" onClick={() => handleAction('check_work')} style={{ justifyContent: 'flex-start' }}>I have a partial answer, can you check it?</button>
            <button className="btn btn-outline" onClick={() => handleAction('simplify')} style={{ justifyContent: 'flex-start' }}>Can you simplify the wording of the question?</button>
            <button className="btn btn-outline" onClick={() => handleAction('breakdown')} style={{ justifyContent: 'flex-start' }}>Break down the formula needed for this.</button>
          </div>
        </div>
      )}

      {state.feedback && (
        <div className="glass animate-fade-in" style={{ padding: '1.5rem', backgroundColor: 'hsla(var(--accent-primary), 0.1)', border: '1px solid hsla(var(--accent-primary), 0.2)' }}>
          <h4>AI Response</h4>
          <div style={{ marginTop: '0.5rem' }}>
            <Latex>{state.feedback}</Latex>
          </div>
        </div>
      )}
    </div>
  );
};
