import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkBreaks from 'remark-breaks'
import { Bot } from 'lucide-react'
import ExecutionTimeline from './ExecutionTimeline'

const formatTime = (date) =>
  date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

export function TypingIndicator() {
  return (
    <div className="message bot" aria-label="Bot is typing">
      <div className="msg-avatar bot"><Bot size={16} /></div>
      <div className="typing-bubble">
        <span className="dot" /><span className="dot" /><span className="dot" />
      </div>
    </div>
  )
}

export function Message({ msg }) {
  const isUser = msg.role === 'user'
  const hasSteps = Array.isArray(msg.executionSteps) && msg.executionSteps.length > 0
  return (
    <div className={`message ${isUser ? 'user' : 'bot'}`}>
      <div className={`msg-avatar ${isUser ? 'user' : 'bot'}`}>
        {isUser ? <span style={{ fontSize: 15 }}>🧑</span> : <Bot size={16} />}
      </div>
      <div className="msg-content">
        <div className="msg-bubble">
          {isUser
            ? msg.content
            : (
              <>
                {hasSteps && <ExecutionTimeline steps={msg.executionSteps} />}
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
