import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkBreaks from 'remark-breaks'
import { Scale, ChevronDown, Brain } from 'lucide-react'
import ExecutionTimeline from './ExecutionTimeline'

const formatTime = (date) =>
  date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

function ThinkingCollapsible({ thinking }) {
  const [open, setOpen] = useState(false)
  if (!thinking) return null
  return (
    <div className="thinking-block">
      <button
        className={`thinking-toggle${open ? ' open' : ''}`}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        <Brain size={13} />
        <span>Reasoning</span>
        <ChevronDown size={13} className={`thinking-chevron${open ? ' rotated' : ''}`} />
      </button>
      {open && (
        <div className="thinking-content">
          <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
            {thinking}
          </ReactMarkdown>
        </div>
      )}
    </div>
  )
}

export function TypingIndicator() {
  return (
    <div className="message bot" aria-label="Bot is typing">
      <div className="msg-avatar bot"><Scale size={16} /></div>
      <div className="typing-bubble">
        <span className="dot" /><span className="dot" /><span className="dot" />
      </div>
    </div>
  )
}

export function Message({ msg }) {
  const isUser = msg.role === 'user'
  const hasSteps = Array.isArray(msg.executionSteps) && msg.executionSteps.length > 0
  const showInitialLoader = !isUser && msg.awaitingFirstEvent && !hasSteps && !msg.content
  return (
    <div className={`message ${isUser ? 'user' : 'bot'}`}>
      <div className={`msg-avatar ${isUser ? 'user' : 'bot'}`}>
        {isUser ? <span style={{ fontSize: 15 }}>🧑</span> : <Scale size={16} />}
      </div>
      <div className="msg-content">
        <div className="msg-bubble">
          {isUser
            ? msg.content
            : (
              <>
                {showInitialLoader && (
                  <div className="initial-event-loader" aria-live="polite">
                    <span className="dot" />
                    <span className="dot" />
                    <span className="dot" />
                  </div>
                )}
                {hasSteps && <ExecutionTimeline steps={msg.executionSteps} />}
                <ThinkingCollapsible thinking={msg.thinking} />
                {msg.content && (
                  <div className="markdown-body">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkBreaks]}
                      components={{
                        a: ({ href, children, ...props }) => (
                          <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            {...props}
                          >
                            {children}
                          </a>
                        ),
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )}
              </>
            )}
        </div>
        <span className="msg-time">{formatTime(msg.timestamp)}</span>
      </div>
    </div>
  )
}
