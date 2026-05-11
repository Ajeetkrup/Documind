import { ShieldCheck, Network, Sparkles, Scale, Zap } from 'lucide-react'

const SUGGESTIONS = [
  'Find conflicts in vendor DPAs',
  'Trace liability obligations across all documents',
  'Check compliance with internal policies',
  'Extract indemnification clauses',
]

const FEATURES = [
  { icon: Network,    label: 'Dependency Tracing' },
  { icon: ShieldCheck,   label: 'Conflict Detection' },
  { icon: Sparkles,label: 'Legal Reasoning' },
  { icon: Zap,      label: 'Due Diligence' },
]

export default function WelcomeScreen({ onSendMessage, hasDocs }) {
  return (
    <div className="welcome-screen">
      <h1 className="welcome-title">Contract Risk &<br/>Dependency Intelligence</h1>
      <p className="welcome-sub">
        Automate due diligence, find cross-contract dependencies, and resolve conflicting obligations instantly.
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
