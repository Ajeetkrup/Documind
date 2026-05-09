import { CheckCircle2, CircleDot, Loader2, Wrench } from 'lucide-react'

const toLabel = (name = '') => name.replace(/_/g, ' ')

export default function ExecutionTimeline({ steps = [] }) {
  if (!steps.length) return null

  return (
    <div className="execution-timeline" aria-live="polite">
      {steps.map((step) => {
        const isTool = step.kind === 'tool'
        const isRunning = step.status === 'running'
        const isDone = step.status === 'done'

        return (
          <div
            key={step.id}
            className={`execution-step ${isRunning ? 'running' : ''} ${isDone ? 'done' : ''}`}
          >
            <span className="execution-step-icon" aria-hidden="true">
              {isRunning
                ? <Loader2 size={14} className="spin" />
                : (isDone ? <CheckCircle2 size={14} /> : <CircleDot size={14} />)}
            </span>
            <span className="execution-step-kind">
              {isTool ? <Wrench size={12} /> : 'Node'}
            </span>
            <span className="execution-step-name">
              {toLabel(step.name)}
            </span>
          </div>
        )
      })}
    </div>
  )
}
