import { useRef, useEffect, useState } from 'react'
import { CheckCircle2, Loader2, Wrench, ChevronDown, Zap } from 'lucide-react'

const toLabel = (name = '') => name.replace(/_/g, ' ')

export default function ExecutionTimeline({ steps = [] }) {
  const [expanded, setExpanded] = useState(false)
  const scrollRef = useRef(null)

  const isAllDone = steps.length > 0 && steps.every((s) => s.status === 'done')
  const runningStep = steps.find((s) => s.status === 'running')

  // Auto-scroll inside the list to the last step when expanded + running
  useEffect(() => {
    if (expanded && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [steps, expanded])

  if (!steps.length) return null

  return (
    <div className="et-block">
      {/* ── Toggle header ── */}
      <button
        className={`et-header${expanded ? ' et-header--open' : ''}`}
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
      >
        <span className="et-header-left">
          {isAllDone ? (
            <span className="et-label-done">
              {steps.length > 0 ? toLabel(steps[steps.length - 1].name) : 'Completed'}
            </span>
          ) : (
            <span className="et-label-running et-shimmer-text">
              {runningStep ? toLabel(runningStep.name) : 'Thinking…'}
            </span>
          )}
        </span>
        <ChevronDown
          size={13}
          className={`et-chevron${expanded ? ' et-chevron--open' : ''}`}
        />
      </button>

      {/* ── Collapsible step list ── */}
      {expanded && (
        <div className="et-body" ref={scrollRef}>
          {steps.map((step) => {
            const isTool    = step.kind === 'tool'
            const isRunning = step.status === 'running'
            const isDone    = step.status === 'done'
            return (
              <div
                key={step.id}
                className={`et-step${isRunning ? ' et-step--running' : ''}${isDone ? ' et-step--done' : ''}`}
              >
                <span className="et-step-icon">
                  {isRunning
                    ? <Loader2 size={12} className="spin" />
                    : <CheckCircle2 size={12} />}
                </span>
                <span className="et-step-kind">
                  {isTool ? <Wrench size={9} /> : 'NODE'}
                </span>
                <span className="et-step-name">{toLabel(step.name)}</span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
