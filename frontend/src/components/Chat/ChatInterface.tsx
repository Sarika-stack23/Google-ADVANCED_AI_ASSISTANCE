import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { Send, Image as ImageIcon, ThumbsUp, ThumbsDown, Copy, FileText, Camera, X, Plus, Edit2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  imageUrl?: string;
}

export const MessageActionButtons = ({ content }: { content: string }) => {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)', justifyContent: 'flex-end', alignItems: 'center' }}>
      <button 
        title="Helpful" 
        onClick={() => setFeedback('up')} 
        style={{ background: 'transparent', border: 'none', color: feedback === 'up' ? 'var(--success)' : 'inherit', opacity: feedback === 'up' ? 1 : 0.6, cursor: 'pointer', transition: 'all 0.2s' }}
      >
        <ThumbsUp size={16} />
      </button>
      <button 
        title="Not Helpful" 
        onClick={() => setFeedback('down')} 
        style={{ background: 'transparent', border: 'none', color: feedback === 'down' ? 'var(--danger)' : 'inherit', opacity: feedback === 'down' ? 1 : 0.6, cursor: 'pointer', transition: 'all 0.2s' }}
      >
        <ThumbsDown size={16} />
      </button>
      <button 
        title="Copy Solution" 
        onClick={handleCopy} 
        style={{ background: 'transparent', border: 'none', color: copied ? 'var(--success)' : 'inherit', opacity: copied ? 1 : 0.6, cursor: 'pointer', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '4px' }}
      >
        {copied ? <span style={{ fontSize: '0.75rem' }}>Copied!</span> : <Copy size={16} />}
      </button>
    </div>
  );
};

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showAttachments, setShowAttachments] = useState(false);

  const incrementProgress = async () => {
    if (!user) return;
    try {
      const token = await user.getIdToken();
      await fetch(import.meta.env.VITE_API_URL + '/api/v1/progress/increment', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (e) {
      console.error("Failed to increment progress", e);
    }
  };

  const [isScanning, setIsScanning] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pdfInputRef = useRef<HTMLInputElement>(null);

  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !user) return;
    
    e.target.value = '';
    
    const userMsgId = Date.now().toString();
    setMessages(prev => [...prev, { 
      id: userMsgId, 
      role: 'user', 
      content: `Uploaded PDF: ${file.name}`
    }]);

    setIsLoading(true);
    const assistantMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: 'Processing document...' }]);

    try {
      const token = await user.getIdToken();
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(import.meta.env.VITE_API_URL + '/api/v1/documents/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (!response.ok) throw new Error("Upload failed");
      const data = await response.json();
      
      setMessages(prev => prev.map(m => 
        m.id === assistantMsgId ? { ...m, content: `Successfully indexed ${data.chunks_added} chunks from ${file.name}. You can now ask questions about it!` } : m
      ));
    } catch (error) {
      console.error(error);
      setMessages(prev => prev.map(m => 
        m.id === assistantMsgId ? { ...m, content: 'Failed to process PDF.' } : m
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const startCamera = async () => {
    setIsScanning(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      alert("Could not access camera. Please check permissions.");
      setIsScanning(false);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsScanning(false);
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(async (blob) => {
          if (blob && user) {
            stopCamera();
            const file = new File([blob], "scan.jpg", { type: "image/jpeg" });
            
            const objectUrl = URL.createObjectURL(file);
            const userMsgId = Date.now().toString();
            setMessages(prev => [...prev, { id: userMsgId, role: 'user', content: 'Scanned an image', imageUrl: objectUrl }]);
            
            setIsLoading(true);
            const assistantMsgId = (Date.now() + 1).toString();
            setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: 'Extracting and solving...' }]);
            
            try {
              const token = await user.getIdToken();
              const formData = new FormData();
              formData.append('file', file);
              formData.append('solve', 'true');
              const response = await fetch(import.meta.env.VITE_API_URL + '/api/v1/vision/extract', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
              });
              if (!response.ok) throw new Error("Upload failed");
              const data = await response.json();
              const solutionContent = data.solution ? `**Extracted Math:**\n\n${data.extracted_math}\n\n**Solution:**\n\n${data.solution}` : `**Extracted Math:**\n\n${data.extracted_math}`;
              setMessages(prev => prev.map(m => m.id === assistantMsgId ? { ...m, content: solutionContent } : m));
              await incrementProgress();
            } catch {
              setMessages(prev => prev.map(m => m.id === assistantMsgId ? { ...m, content: 'Failed to process image.' } : m));
            } finally {
              setIsLoading(false);
            }
          }
        }, 'image/jpeg');
      }
    }
  };

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
    const customKey = localStorage.getItem('custom_gemini_api_key') || "";

    const assistantMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: '' }]);

    try {
      const response = await fetch(import.meta.env.VITE_API_URL + '/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'X-Gemini-API-Key': customKey
        },
        body: JSON.stringify({ query: userMsg.content, session_id: 'default' })
      });

      if (!response.body) throw new Error("No readable stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
            const chunkValue = decoder.decode(value);
            const lines = chunkValue.split('\n');
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') {
                  done = true;
                  break;
                }
                try {
                  let parsedContent = data;
                  try {
                    const parsed = JSON.parse(data);
                    if (parsed.content) parsedContent = parsed.content;
                  } catch {}
                  
                  setMessages(prev => prev.map(m => 
                    m.id === assistantMsgId ? { ...m, content: m.content + parsedContent } : m
                  ));
                } catch (e) {
                  console.error("SSE update error", e);
                }
              }
            }
        }
      }
      await incrementProgress();
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => prev.map(m => 
          m.id === assistantMsgId ? { ...m, content: "An error occurred while connecting to the server." } : m
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !user) return;
    
    e.target.value = '';

    const objectUrl = URL.createObjectURL(file);
    const userMsgId = Date.now().toString();
    
    setMessages(prev => [...prev, { 
      id: userMsgId, 
      role: 'user', 
      content: 'Uploaded an image',
      imageUrl: objectUrl 
    }]);

    setIsLoading(true);
    const assistantMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: 'Extracting and solving...' }]);

    try {
      const token = await user.getIdToken();
      const formData = new FormData();
      formData.append('file', file);
      formData.append('solve', 'true');

      const response = await fetch(import.meta.env.VITE_API_URL + '/api/v1/vision/extract', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (!response.ok) throw new Error("Upload failed");
      const data = await response.json();
      
      const solutionContent = data.solution ? `**Extracted Math:**\n\n${data.extracted_math}\n\n**Solution:**\n\n${data.solution}` : `**Extracted Math:**\n\n${data.extracted_math}`;

      setMessages(prev => prev.map(m => 
        m.id === assistantMsgId ? { ...m, content: solutionContent } : m
      ));
      await incrementProgress();
    } catch (error) {
      console.error(error);
      setMessages(prev => prev.map(m => 
        m.id === assistantMsgId ? { ...m, content: 'Failed to process image.' } : m
      ));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="main-content" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
      <h2 style={{ marginBottom: '1.5rem' }}>Math Assistant</h2>
      
      <div className="glass" style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem', borderRadius: '12px' }}>
        {messages.length === 0 && (
          <div className="animate-fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '2rem', opacity: 0.8 }}>
            <h2 className="text-gradient" style={{ fontSize: '2rem', marginBottom: '1rem' }}>How can I help you learn today?</h2>
            <p style={{ color: 'hsl(var(--text-secondary))', marginBottom: '2rem' }}>Ask any math question or upload a document to get started.</p>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center', maxWidth: '600px' }}>
              {["Solve a quadratic equation", "Explain calculus limits", "Help with trigonometry", "Graph a parabola"].map(q => (
                <button key={q} className="btn glass-panel" style={{ color: 'hsl(var(--text-primary))', fontSize: '0.9rem' }} onClick={() => setInput(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {messages.map((msg) => (
          <div key={msg.id} className="animate-fade-in" style={{ 
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
            backgroundColor: msg.role === 'user' ? 'hsl(var(--accent-primary))' : 'hsl(var(--bg-secondary))',
            color: msg.role === 'user' ? 'white' : 'inherit',
            padding: '1rem',
            borderRadius: '12px',
            maxWidth: '85%',
            position: 'relative'
          }}>
            {msg.role === 'user' && (
              <button 
                title="Edit Message" 
                onClick={() => setInput(msg.content)} 
                style={{ position: 'absolute', top: '0.5rem', right: '0.5rem', background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.7)', cursor: 'pointer', transition: 'opacity 0.2s' }}
                onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
                onMouseLeave={(e) => e.currentTarget.style.opacity = '0.7'}
              >
                <Edit2 size={14} />
              </button>
            )}
            {msg.imageUrl && (
                <img src={msg.imageUrl} alt="Uploaded" style={{ maxWidth: '100%', borderRadius: '8px', marginBottom: '0.5rem' }} />
            )}
            {msg.content && (
              <div className={msg.role === 'assistant' ? 'handwritten-math' : ''}>
                <ReactMarkdown 
                  remarkPlugins={[remarkMath]} 
                  rehypePlugins={[rehypeKatex]}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>
            )}
            {msg.role === 'assistant' && !isLoading && (
              <MessageActionButtons content={msg.content} />
            )}
          </div>
        ))}
        
        {isScanning && (
          <div className="glass animate-fade-in" style={{ alignSelf: 'center', padding: '1rem', borderRadius: '12px', position: 'relative', width: '100%', maxWidth: '400px' }}>
            <video ref={videoRef} autoPlay playsInline style={{ width: '100%', borderRadius: '8px' }} />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem' }}>
              <button className="btn btn-outline" onClick={stopCamera} style={{ color: 'var(--danger)' }}><X size={20} /> Cancel</button>
              <button className="btn btn-primary" onClick={captureImage}><Camera size={20} /> Capture</button>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="glass animate-fade-in" style={{ alignSelf: 'flex-start', padding: '1rem 1.5rem', borderRadius: '16px', color: 'hsl(var(--text-secondary))' }}>
            <div style={{ display: 'flex', gap: '4px', alignItems: 'center', height: '24px' }}>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
        <input 
            type="file" 
            accept="image/*" 
            style={{ display: 'none' }} 
            ref={fileInputRef}
            onChange={handleImageUpload}
        />
        <input 
            type="file" 
            accept=".pdf,application/pdf" 
            style={{ display: 'none' }} 
            ref={pdfInputRef}
            onChange={handlePdfUpload}
        />
        <div style={{ position: 'relative' }}>
          <button 
              type="button" 
              className="btn btn-outline" 
              title="Add Attachment"
              onClick={() => setShowAttachments(!showAttachments)}
              disabled={isLoading || isScanning}
          >
            <Plus size={20} />
          </button>
          {showAttachments && (
            <div className="glass animate-fade-in" style={{ position: 'absolute', bottom: '100%', left: 0, marginBottom: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem', padding: '0.5rem', minWidth: '180px', zIndex: 10 }}>
              <button type="button" className="btn btn-outline" style={{ justifyContent: 'flex-start', border: 'none', fontSize: '0.9rem' }} onClick={() => { startCamera(); setShowAttachments(false); }}><Camera size={16} /> Scan Math</button>
              <button type="button" className="btn btn-outline" style={{ justifyContent: 'flex-start', border: 'none', fontSize: '0.9rem' }} onClick={() => { fileInputRef.current?.click(); setShowAttachments(false); }}><ImageIcon size={16} /> Upload Image</button>
              <button type="button" className="btn btn-outline" style={{ justifyContent: 'flex-start', border: 'none', fontSize: '0.9rem' }} onClick={() => { pdfInputRef.current?.click(); setShowAttachments(false); }}><FileText size={16} /> Upload PDF</button>
            </div>
          )}
        </div>
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
