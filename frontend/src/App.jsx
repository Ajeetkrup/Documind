import { useState, useRef, useEffect, useCallback } from 'react'
import { Bot, Send, Loader2, Sparkles, Menu, AlertCircle } from 'lucide-react'

import Sidebar from './components/Sidebar'
import { Message, TypingIndicator } from './components/Message'
import WelcomeScreen from './components/WelcomeScreen'
import { postChatQuery } from './api'

export default function App() {
  const [messages, setMessages]         = useState([])
  const [input, setInput]               = useState('')
  const [loading, setLoading]           = useState(false)
  const [uploadedDocs, setUploadedDocs] = useState([])
  const [sidebarOpen, setSidebarOpen]   = useState(false)
  const [showToast, setShowToast]       = useState(false)
  
  const bottomRef   = useRef(null)
  const textareaRef = useRef(null)
  const toastTimer  = useRef(null)

  const hasDocs = uploadedDocs.length > 0;

  const triggerUploadPrompt = useCallback(() => {
    setShowToast(true)
    if (toastTimer.current) clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setShowToast(false), 3000)
    
    // Auto-open sidebar on mobile to help them upload
    if (window.innerWidth <= 768) {
      setSidebarOpen(true)
    }
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`
  }, [input])

  const extractAnswer = (response) => {
    if (!response) return 'No response received.'
    return response.message
  }

  const sendMessage = useCallback(async (text) => {
    if (!hasDocs) {
      triggerUploadPrompt();
      return;
    }
    const trimmed = (text ?? input).trim()
    if (!trimmed || loading) return
    const userMsg = { role: 'user', content: trimmed, timestamp: new Date() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    try {
      const data = await postChatQuery(trimmed)
      setMessages(prev => [...prev, { role: 'bot', content: extractAnswer(data), timestamp: new Date() }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'bot',
        content: `⚠️ Something went wrong: ${err.message}`,
        timestamp: new Date(),
      }])
    } finally {
      setLoading(false)
    }
  }, [input, loading, hasDocs, triggerUploadPrompt])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  return (
    <div className="app">
      <Sidebar
        uploadedDocs={uploadedDocs}
        onUpload={(name) => setUploadedDocs(prev => [name, ...prev])}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="chat-area">
        {/* Header */}
        <header className="chat-header">
          <button
            id="menu-btn"
            className="menu-btn"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
          >
            <Menu size={22} />
          </button>

          <div className="header-avatar"><Bot size={20} color="#fff" /></div>

          <div className="header-info">
            <div className="header-title">Documind AI</div>
            <div className="header-sub">
              <span className="status-dot" />
              Agentic RAG · LangGraph · Self-Correcting
            </div>
          </div>

          <div className="header-badges">
            <span className="header-badge hb-purple">LangGraph</span>
            <span className="header-badge hb-teal">Adaptive RAG</span>
          </div>

          <Sparkles size={18} color="var(--text-muted)" style={{ flexShrink: 0 }} />
        </header>

        {/* Messages */}
        <div className="messages-container" role="log" aria-live="polite">
          {messages.length === 0 ? (
            <WelcomeScreen onSendMessage={sendMessage} hasDocs={hasDocs} />
          ) : (
            messages.map((msg, i) => <Message key={i} msg={msg} />)
          )}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="input-area">
          <div className="input-bar">
            <textarea
              ref={textareaRef}
              id="chat-input"
              className="msg-input"
              placeholder="Ask anything about your documents…"
              value={input}
              rows={1}
              onChange={(e) => {
                if (!hasDocs) {
                  triggerUploadPrompt();
                  return;
                }
                setInput(e.target.value)
              }}
              onClick={() => {
                if (!hasDocs) triggerUploadPrompt();
              }}
              onKeyDown={(e) => {
                if (!hasDocs) {
                  e.preventDefault();
                  triggerUploadPrompt();
                  return;
                }
                handleKeyDown(e);
              }}
              disabled={loading}
              aria-label="Chat message input"
            />
            <button
              id="send-btn"
              className="send-btn"
              onClick={() => sendMessage()}
              disabled={loading}
              aria-label="Send message"
              style={{ opacity: (!input.trim() && hasDocs) ? 0.5 : 1 }}
            >
              {loading
                ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                : <Send size={18} />}
            </button>
          </div>
          <p className="input-hint">Enter to send · Shift+Enter for new line</p>
        </div>
      </main>

      {/* Upload Prompt Toast */}
      {showToast && (
        <div className="toast-popup">
          <AlertCircle size={18} color="#ef4444" />
          <span>Please upload a document first to start chatting.</span>
        </div>
      )}
    </div>
  )
}
