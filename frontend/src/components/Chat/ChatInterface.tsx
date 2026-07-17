import React, { useState, useRef, useEffect } from 'react';
import Latex from 'react-latex-next';
import 'katex/dist/katex.min.css';
import { Send, Image, HelpCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !user) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    const token = await user.getIdToken();
    const sessionId = 'session-' + user.uid; // Basic session management

    // Prepare assistant message stub for streaming
    const assistantMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: '' }]);

    try {
      const response = await fetch('http://localhost:8080/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: userMsg.content, session_id: sessionId })
      });

      if (!response.body) throw new Error("No readable stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        const chunkValue = decoder.decode(value);
        
        // SSE parsing
        const lines = chunkValue.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              done = true;
              break;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                setMessages(prev => prev.map(m => 
                  m.id === assistantMsgId ? { ...m, content: m.content + parsed.content } : m
                ));
              }
            } catch (e) {
              console.error("Error parsing SSE data", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, { id: Date.now().toString(), role: 'assistant', content: "An error occurred while connecting to the server." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="main-content" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
      <h2 style={{ marginBottom: '1.5rem' }}>Math Assistant</h2>
      
      <div className="glass" style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem', borderRadius: '12px' }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'hsl(var(--text-secondary))', marginTop: 'auto', marginBottom: 'auto' }}>
            <HelpCircle size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
            <h3>How can I help you with math today?</h3>
            <p>Ask me to solve equations, differentiate, or plot functions.</p>
          </div>
        )}
        
        {messages.map((msg) => (
          <div key={msg.id} className="animate-fade-in" style={{ 
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
            backgroundColor: msg.role === 'user' ? 'hsl(var(--accent-primary))' : 'hsl(var(--bg-secondary))',
            color: msg.role === 'user' ? 'white' : 'inherit',
            padding: '1rem',
            borderRadius: '12px',
            maxWidth: '85%'
          }}>
            <Latex>{msg.content}</Latex>
          </div>
        ))}
        {isLoading && (
          <div style={{ alignSelf: 'flex-start', padding: '1rem', color: 'hsl(var(--text-secondary))' }}>
            Thinking...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
        <button type="button" className="btn btn-outline" title="Upload Image (Phase 10)">
          <Image size={20} />
        </button>
        <input 
          type="text" 
          className="input" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a math question..." 
          disabled={isLoading}
        />
        <button type="submit" className="btn btn-primary" disabled={isLoading || !input.trim()}>
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};
