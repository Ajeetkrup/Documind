import ReactMarkdown from 'react-markdown'
import { Bot } from 'lucide-react'

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
  return (
    <div className={`message ${isUser ? 'user' : 'bot'}`}>
      <div className={`msg-avatar ${isUser ? 'user' : 'bot'}`}>
        {isUser ? <span style={{ fontSize: 15 }}>🧑</span> : <Bot size={16} />}
      </div>
      <div className="msg-content">
        <div className="msg-bubble">
          {isUser
            ? msg.content
            : <ReactMarkdown>{msg.content}</ReactMarkdown>}
        </div>
        <span className="msg-time">{formatTime(msg.timestamp)}</span>
      </div>
    </div>
  )
}
