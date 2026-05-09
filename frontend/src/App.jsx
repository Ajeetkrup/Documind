import { useState, useRef, useEffect, useCallback } from 'react'
import { Bot, Send, Loader2, Sparkles, Menu, AlertCircle } from 'lucide-react'

import Sidebar from './components/Sidebar'
import { Message } from './components/Message'
import WelcomeScreen from './components/WelcomeScreen'
import { streamChatQuery } from './api'

const createMessageId = () =>
  (typeof crypto !== 'undefined' && crypto.randomUUID)
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`

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

  const sendMessage = useCallback(async (text) => {
    if (!hasDocs) {
      triggerUploadPrompt();
      return;
    }
    const trimmed = (text ?? input).trim()
    if (!trimmed || loading) return
    const userMsg = { id: createMessageId(), role: 'user', content: trimmed, timestamp: new Date() }
    const botMessageId = createMessageId()
    const botMsg = {
      id: botMessageId,
      role: 'bot',
      content: '',
      timestamp: new Date(),
      executionSteps: [],
    }
    setMessages(prev => [...prev, userMsg, botMsg])
    setInput('')
    setLoading(true)

    try {
      await new Promise((resolve, reject) => {
        const updateBot = (updater) => {
          setMessages(prev => {
            const updated = [...prev]
            const idx = updated.findIndex((msg) => msg.id === botMessageId)
            if (idx === -1) return prev
            updated[idx] = updater(updated[idx])
            return updated
          })
        }

        const upsertStep = (event, status) => {
          const kind = event.type.startsWith('tool_') ? 'tool' : 'node'
          const name = event.name || 'unknown'
          const stepId = `${kind}:${name}`

          updateBot((bot) => {
            const steps = Array.isArray(bot.executionSteps) ? [...bot.executionSteps] : []
            const stepIndex = steps.findIndex((step) => step.id === stepId)
            if (stepIndex >= 0) {
              steps[stepIndex] = { ...steps[stepIndex], status }
            } else {
              steps.push({ id: stepId, kind, name, status })
            }
            return { ...bot, executionSteps: steps }
          })
        }

        const closeStream = streamChatQuery(trimmed, {
          onStatusEvent: (event) => {
            if (event.type === 'node_start' || event.type === 'tool_start') {
              upsertStep(event, 'running')
            }
            if (event.type === 'node_end' || event.type === 'tool_end') {
              upsertStep(event, 'done')
            }
          },
          onToken: (token) => {
            if (!token) return
            updateBot((bot) => ({ ...bot, content: `${bot.content}${token}` }))
          },
          onRunEnd: (event) => {
            const finalAnswer = event?.payload?.answer
            if (typeof finalAnswer === 'string') {
              updateBot((bot) => (
                bot.content.trim()
                  ? bot
                  : { ...bot, content: finalAnswer }
              ))
            }
            closeStream()
            resolve()
          },
          onError: (err) => {
            closeStream()
            reject(err)
          },
        })
      })
    } catch (err) {
      setMessages((prev) => prev.map((msg) => {
        if (msg.id === botMessageId) {
          const fallback = msg.content?.trim()
            ? msg.content
            : `⚠️ Something went wrong: ${err.message}`
          return { ...msg, content: fallback }
        }
        return msg
      }))
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
            messages.map((msg) => <Message key={msg.id} msg={msg} />)
          )}
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
