import { MessageSquare, Brain, Search, RotateCcw, Zap } from 'lucide-react'

const SUGGESTIONS = [
  'Summarise this document',
  'What are the key findings?',
  'Explain the main topic',
  'List the important sections',
]

const FEATURES = [
  { icon: Brain,    label: 'Adaptive RAG' },
  { icon: Search,   label: 'Semantic Search' },
  { icon: RotateCcw,label: 'Self-Correcting' },
  { icon: Zap,      label: 'LangGraph' },
]

export default function WelcomeScreen({ onSendMessage, hasDocs }) {
  return (
    <div className="welcome-screen">
      <div className="welcome-glow-ring">
        <div className="welcome-icon">
          <MessageSquare size={38} color="#fff" />
        </div>
      </div>

      <h1 className="welcome-title">Ask your documents anything</h1>
      <p className="welcome-sub">
        Upload a PDF, DOCX, or TXT file, then start a conversation.
        Documind uses an agentic RAG pipeline to retrieve, grade, and reason over your content.
      </p>

      <div className="welcome-features">
        {FEATURES.map(({ icon: Icon, label }) => (
          <div className="feat-pill" key={label}>
            <Icon size={13} />{label}
          </div>
        ))}
      </div>

      <div className="suggestion-chips">
        {SUGGESTIONS.map(s => (
          <button 
            key={s} 
            className="chip" 
            onClick={() => onSendMessage(s)}
            style={{ opacity: hasDocs ? 1 : 0.7, cursor: 'pointer' }}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}
