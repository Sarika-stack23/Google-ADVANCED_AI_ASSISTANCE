import React, { useState, useRef, useEffect } from 'react';
import Latex from 'react-latex-next';
import 'katex/dist/katex.min.css';
import { Send, Image as ImageIcon, HelpCircle, ThumbsUp, ThumbsDown, Copy, FileText, Camera, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  imageUrl?: string;
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

      const response = await fetch('http://localhost:8080/api/v1/documents/upload', {
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
              const response = await fetch('http://localhost:8080/api/v1/vision/extract', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
              });
              if (!response.ok) throw new Error("Upload failed");
              const data = await response.json();
              const solutionContent = data.solution ? `**Extracted Math:**\n\n${data.extracted_math}\n\n**Solution:**\n\n${data.solution}` : `**Extracted Math:**\n\n${data.extracted_math}`;
              setMessages(prev => prev.map(m => m.id === assistantMsgId ? { ...m, content: solutionContent } : m));
            } catch (error) {
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
    const sessionId = 'session-' + user.uid;

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
                  const parsed = JSON.parse(data);
                  if (parsed.content) {
                    setMessages(prev => prev.map(m => 
                      m.id === assistantMsgId ? { ...m, content: m.content + parsed.content } : m
                    ));
                  }
                } catch (e) {
                  if (data && data !== '[DONE]' && !data.startsWith('{')) {
                      setMessages(prev => prev.map(m => 
                          m.id === assistantMsgId ? { ...m, content: m.content + data } : m
                      ));
                  }
                }
              }
            }
        }
      }
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

      const response = await fetch('http://localhost:8080/api/v1/vision/extract', {
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
          <div style={{ textAlign: 'center', color: 'hsl(var(--text-secondary))', marginTop: 'auto', marginBottom: 'auto' }}>
            <HelpCircle size={48} style={{ opacity: 0.5, marginBottom: '1rem', margin: '0 auto' }} />
            <h3>How can I help you with math today?</h3>
            <p>Ask me to solve equations, or upload a photo of a math problem!</p>
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
            {msg.imageUrl && (
                <img src={msg.imageUrl} alt="Uploaded" style={{ maxWidth: '100%', borderRadius: '8px', marginBottom: '0.5rem' }} />
            )}
            {msg.content && <div className={msg.role === 'assistant' ? 'handwritten-math' : ''}><Latex>{msg.content}</Latex></div>}
            {msg.role === 'assistant' && !isLoading && (
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)', justifyContent: 'flex-end' }}>
                <button title="Helpful" onClick={() => {}} style={{ background: 'transparent', border: 'none', color: 'inherit', opacity: 0.6, cursor: 'pointer' }}><ThumbsUp size={16} /></button>
                <button title="Not Helpful" onClick={() => {}} style={{ background: 'transparent', border: 'none', color: 'inherit', opacity: 0.6, cursor: 'pointer' }}><ThumbsDown size={16} /></button>
                <button title="Copy Solution" onClick={() => navigator.clipboard.writeText(msg.content)} style={{ background: 'transparent', border: 'none', color: 'inherit', opacity: 0.6, cursor: 'pointer' }}><Copy size={16} /></button>
              </div>
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
          <div style={{ alignSelf: 'flex-start', padding: '1rem', color: 'hsl(var(--text-secondary))' }}>
            Thinking...
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
            accept="application/pdf" 
            style={{ display: 'none' }} 
            ref={pdfInputRef}
            onChange={handlePdfUpload}
        />
        <button 
            type="button" 
            className="btn btn-outline" 
            title="Scan with Camera"
            onClick={startCamera}
            disabled={isLoading || isScanning}
        >
          <Camera size={20} />
        </button>
        <button 
            type="button" 
            className="btn btn-outline" 
            title="Upload Math Image"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
        >
          <ImageIcon size={20} />
        </button>
        <button 
            type="button" 
            className="btn btn-outline" 
            title="Upload Document"
            onClick={() => pdfInputRef.current?.click()}
            disabled={isLoading}
        >
          <FileText size={20} />
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
