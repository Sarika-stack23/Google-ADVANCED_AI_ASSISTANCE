import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface QuizState {
  quizTree: any;
  selectedClass: string;
  selectedChapter: string;
  selectedExercise: string;
  selectedQuestionIndex: number;
  currentQuestionRaw: string;
  feedback: string;
  showStuckMenu: boolean;
}

export const NCERTQuizPanel: React.FC = () => {
  const { user } = useAuth();
  const [state, setState] = useState<QuizState>({
    quizTree: {},
    selectedClass: '',
    selectedChapter: '',
    selectedExercise: '',
    selectedQuestionIndex: 0,
    currentQuestionRaw: '',
    feedback: '',
    showStuckMenu: false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(state.feedback);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  useEffect(() => {
    // Fetch quiz tree on mount
    fetch('http://localhost:8080/api/v1/quiz/structure')
      .then(r => r.json())
      .then(data => {
        setState(prev => {
          // Find first available path
          const classes = Object.keys(data).sort();
          const firstClass = classes[0] || '';
          
          const chaps = firstClass ? Object.keys(data[firstClass]).sort((a,b) => parseInt(a.replace('ch','')) - parseInt(b.replace('ch',''))) : [];
          const firstChap = chaps[0] || '';
          
          const exs = firstChap ? Object.keys(data[firstClass][firstChap]).sort() : [];
          const firstEx = exs[0] || '';
          
          const qs = firstEx ? data[firstClass][firstChap][firstEx] : [];
          return {
            ...prev,
            quizTree: data,
            selectedClass: firstClass,
            selectedChapter: firstChap,
            selectedExercise: firstEx,
            selectedQuestionIndex: 0,
            currentQuestionRaw: qs.length > 0 ? qs[0] : ''
          };
        });
      })
      .catch(console.error);
  }, []);

  const handleAction = async (action: string) => {
    if (!user) return;
    setIsLoading(true);

    const token = await user.getIdToken();
    const trackWeakness = async () => {
        try {
            await fetch('http://localhost:8080/api/v1/progress/weakness', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: state.selectedChapter })
            });
        } catch (e) { console.error(e); }
    };
    
    const trackAccuracy = async (correct: boolean) => {
        try {
            await fetch('http://localhost:8080/api/v1/progress/accuracy', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ correct })
            });
        } catch (e) { console.error(e); }
    };
    
    const incrementProgress = async () => {
        try {
            await fetch('http://localhost:8080/api/v1/progress/increment', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
        } catch (e) { console.error(e); }
    };
    
    // If asking for 'answer', we already have it parsed from the raw markdown
    if (action.includes('Show me the full answer for this') || action.includes('Show me the full step-by-step answer')) {
        const parts = state.currentQuestionRaw.split(/Answer:/i);
        incrementProgress();
        if (parts.length > 1) {
            setState(prev => ({ ...prev, feedback: "**Answer:** " + parts[1].trim(), showStuckMenu: false }));
            setIsLoading(false);
            return;
        } else {
            // Some questions might not have an "Answer:" block, so we fall back to AI
            action = 'Solve this problem and show the final answer';
        }
    }
    
    if (action.toLowerCase().includes('hint') || action.toLowerCase().includes('step') || action.includes("I don't understand") || action.includes('explain the underlying concept') || action.includes('break down the formula')) {
        trackWeakness();
    }
    
    if (action === 'I understood it, thanks!') {
        trackAccuracy(true);
        incrementProgress();
        setState(prev => ({ ...prev, feedback: "Great job! Keep up the good work. 💪", showStuckMenu: false }));
        setIsLoading(false);
        return;
    } else if (action === 'I still have a doubt, can you explain further?') {
        trackAccuracy(false);
        trackWeakness();
    }

    try {
      const token = await user.getIdToken();
      
      const questionText = state.currentQuestionRaw.split(/Answer:/i)[0].trim();
      const customKey = localStorage.getItem('custom_gemini_api_key') || "";
      
      // We send the query to the standard /chat/stream endpoint
      const response = await fetch(`http://localhost:8080/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'X-Gemini-API-Key': customKey
        },
        body: JSON.stringify({ 
            query: `Action: ${action}\nQuestion: ${questionText}`, 
            session_id: 'quiz-' + Date.now() 
        })
      });
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // SSE parser
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullResponse = "";
      
      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const dataStr = line.slice(6);
                if (dataStr.trim() === "[DONE]") continue;
                let parsedContent = dataStr;
                try {
                    const parsed = JSON.parse(dataStr);
                    if (parsed.content) parsedContent = parsed.content;
                } catch {}
                
                fullResponse += parsedContent;
                setState(prev => ({ ...prev, feedback: fullResponse, showStuckMenu: false }));
            }
        }
      }
      
    } catch (e) {
      console.error(e);
      setState(prev => ({ ...prev, feedback: "Failed to fetch response from AI." }));
    } finally {
      setIsLoading(false);
    }
  };
  
  // Format the keys (e.g. class_10 -> Class 10)
  const formatKey = (k: string) => {
      if (k.startsWith('class_')) return `Class ${k.split('_')[1]}`;
      if (k.startsWith('ch')) return `Chapter ${k.replace('ch', '')}`;
      if (k.startsWith('ex')) return `Exercise ${k.replace('ex', '')}`;
      return k;
  };

  const handleClassChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      const c = e.target.value;
      const chaps = Object.keys(state.quizTree[c] || {}).sort((a,b) => parseInt(a.replace('ch','')) - parseInt(b.replace('ch','')));
      const firstChap = chaps[0] || '';
      const exs = firstChap ? Object.keys(state.quizTree[c][firstChap] || {}).sort() : [];
      const firstEx = exs[0] || '';
      const qs = firstEx ? state.quizTree[c][firstChap][firstEx] : [];
      setState(prev => ({ ...prev, selectedClass: c, selectedChapter: firstChap, selectedExercise: firstEx, selectedQuestionIndex: 0, currentQuestionRaw: qs.length > 0 ? qs[0] : '', feedback: '' }));
  };

  const handleChapterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      const ch = e.target.value;
      const exs = Object.keys(state.quizTree[state.selectedClass]?.[ch] || {}).sort();
      const firstEx = exs[0] || '';
      const qs = firstEx ? state.quizTree[state.selectedClass][ch][firstEx] : [];
      setState(prev => ({ ...prev, selectedChapter: ch, selectedExercise: firstEx, selectedQuestionIndex: 0, currentQuestionRaw: qs.length > 0 ? qs[0] : '', feedback: '' }));
  };

  const handleExerciseChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      const ex = e.target.value;
      const qs = state.quizTree[state.selectedClass]?.[state.selectedChapter]?.[ex] || [];
      setState(prev => ({ ...prev, selectedExercise: ex, selectedQuestionIndex: 0, currentQuestionRaw: qs.length > 0 ? qs[0] : '', feedback: '' }));
  };

  const handleQuestionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      const qIdx = parseInt(e.target.value);
      const qs = state.quizTree[state.selectedClass]?.[state.selectedChapter]?.[state.selectedExercise] || [];
      setState(prev => ({ ...prev, selectedQuestionIndex: qIdx, currentQuestionRaw: qs[qIdx] || '', feedback: '' }));
  };

  // Only show the question part (not the answer block)
  const displayQuestion = state.currentQuestionRaw.split(/Answer:/i)[0].trim();

  return (
    <div className="main-content" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', width: '100%', overflowY: 'auto', height: '100vh', boxSizing: 'border-box' }}>
      <h2>📚 NCERT Practice</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Select a class, chapter, and exercise to practice NCERT questions.</p>
      
      {/* Selectors */}
      <div className="glass" style={{ padding: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
          <select value={state.selectedClass} onChange={handleClassChange} className="btn btn-outline" style={{ flex: '1 1 150px', justifyContent: 'space-between' }}>
              {Object.keys(state.quizTree).sort().map(c => <option key={c} value={c}>{formatKey(c)}</option>)}
          </select>
          
          <select value={state.selectedChapter} onChange={handleChapterChange} className="btn btn-outline" style={{ flex: '1 1 150px', justifyContent: 'space-between' }}>
              {Object.keys(state.quizTree[state.selectedClass] || {}).sort((a,b) => parseInt(a.replace('ch','')) - parseInt(b.replace('ch',''))).map(ch => <option key={ch} value={ch}>{formatKey(ch)}</option>)}
          </select>
          
          <select value={state.selectedExercise} onChange={handleExerciseChange} className="btn btn-outline" style={{ flex: '1 1 150px', justifyContent: 'space-between' }}>
              {Object.keys(state.quizTree[state.selectedClass]?.[state.selectedChapter] || {}).sort().map(ex => <option key={ex} value={ex}>{formatKey(ex)}</option>)}
          </select>
          
          <select value={state.selectedQuestionIndex} onChange={handleQuestionChange} className="btn btn-outline" style={{ flex: '1 1 150px', justifyContent: 'space-between' }}>
              {(state.quizTree[state.selectedClass]?.[state.selectedChapter]?.[state.selectedExercise] || []).map((q: string, idx: number) => {
                  const qNumMatch = q.match(/Q\d+/);
                  const label = qNumMatch ? qNumMatch[0] : `Question ${idx + 1}`;
                  return <option key={idx} value={idx}>{label}</option>;
              })}
          </select>
      </div>
      
      <div className="glass" style={{ padding: '1.5rem', marginBottom: '1.5rem', minHeight: '150px' }}>
        <p style={{ fontSize: '1.2rem', lineHeight: '1.5', margin: 0 }}>
          {displayQuestion ? <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>{displayQuestion}</ReactMarkdown> : <i>Loading questions or none available...</i>}
        </p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <button className="btn btn-outline" onClick={() => handleAction('Give me a small hint to start solving this')} disabled={isLoading || !displayQuestion}>💡 Hint</button>
        <button className="btn btn-outline" onClick={() => handleAction('Show me the first step to solve this')} disabled={isLoading || !displayQuestion}>📖 Steps</button>
        <button className="btn btn-primary" onClick={() => handleAction('Show me the full answer for this')} disabled={isLoading || !displayQuestion}>✅ Answer</button>
        <button className="btn btn-outline" onClick={() => setState(prev => ({ ...prev, showStuckMenu: !prev.showStuckMenu }))} disabled={isLoading || !displayQuestion}>❓ Ask AI</button>
      </div>

      {state.showStuckMenu && (
        <div className="glass animate-fade-in" style={{ padding: '1.5rem', marginBottom: '1.5rem', backgroundColor: 'var(--bg-secondary)' }}>
          <h4 style={{ marginBottom: '1rem' }}>I'm stuck because...</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <button className="btn btn-outline" onClick={() => handleAction('explain the underlying concept')} style={{ justifyContent: 'flex-start' }}>I don't understand the underlying concept.</button>
            <button className="btn btn-outline" onClick={() => handleAction('show me a similar solved example')} style={{ justifyContent: 'flex-start' }}>Can you show me a similar solved example?</button>
            <button className="btn btn-outline" onClick={() => handleAction('simplify the wording of the question')} style={{ justifyContent: 'flex-start' }}>Can you simplify the wording of the question?</button>
            <button className="btn btn-outline" onClick={() => handleAction('break down the formula needed for this')} style={{ justifyContent: 'flex-start' }}>Break down the formula needed for this.</button>
          </div>
        </div>
      )}

      {state.feedback && (
        <div className="glass animate-fade-in" style={{ padding: '1.5rem', backgroundColor: 'hsla(var(--accent-primary), 0.1)', border: '1px solid hsla(var(--accent-primary), 0.2)', marginBottom: '3rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
             <h4>AI Response</h4>
             <button title="Copy Solution" onClick={handleCopy} style={{ background: 'transparent', border: 'none', color: copied ? 'var(--success)' : 'inherit', opacity: copied ? 1 : 0.6, cursor: 'pointer', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '4px' }}>
               {copied ? <span style={{ fontSize: '0.75rem' }}>Copied!</span> : <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>}
             </button>
          </div>
          <div className="handwritten-math">
            <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>{state.feedback}</ReactMarkdown>
          </div>
          
          {!isLoading && (
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.5rem', flexWrap: 'wrap', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem' }}>
               <button className="btn btn-outline" onClick={() => handleAction("I understood it, thanks!")} style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}>✅ Yes, got it!</button>
               <button className="btn btn-outline" onClick={() => handleAction("I still have a doubt, can you explain further?")} style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}>❓ I have a doubt</button>
               <button className="btn btn-outline" onClick={() => handleAction("Can you explain this differently?")} style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}>🔁 Explain differently</button>
               <button className="btn btn-outline" onClick={() => handleAction("Show me the full step-by-step answer")} style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}>✅ Full Answer</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
