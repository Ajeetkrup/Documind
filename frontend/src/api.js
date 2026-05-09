const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8004'
const API_BASE_URL = RAW_API_BASE_URL.endsWith('/api')
  ? RAW_API_BASE_URL
  : `${RAW_API_BASE_URL}/api`

export async function postChatQuery(query) {
  const res = await fetch(`${API_BASE_URL}/chat?query=${encodeURIComponent(query)}`, {
    method: 'POST',
  })

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`)
  }

  return res.json()
}

export function streamChatQuery(query, {
  onStatusEvent,
  onToken,
  onAnswerDone,
  onRunEnd,
  onError,
}) {
  const streamUrl = `${API_BASE_URL}/chat/stream?query=${encodeURIComponent(query)}`
  const eventSource = new EventSource(streamUrl)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      if (!data || typeof data !== 'object') {
        return
      }

      switch (data.type) {
        case 'answer_token':
          onToken?.(data?.payload?.token ?? '')
          break
        case 'answer_done':
          onAnswerDone?.(data)
          break
        case 'run_end':
          onRunEnd?.(data)
          eventSource.close()
          break
        case 'run_start':
        case 'node_start':
        case 'node_end':
        case 'tool_start':
        case 'tool_end':
          onStatusEvent?.(data)
          break
        case 'error':
          onError?.(new Error(data?.payload?.message || 'Streaming request failed.'))
          eventSource.close()
          break
        default:
          // Ignore unknown events for forward compatibility.
          break
      }

      // Backward compatibility with legacy stream payloads.
      if (data?.token) {
        onToken?.(data.token)
      }
      if (data?.done) {
        onRunEnd?.({ type: 'run_end', payload: {} })
        eventSource.close()
      }
    } catch {
      // Ignore malformed chunks and keep stream alive.
    }
  }

  eventSource.onerror = () => {
    onError?.(new Error('Streaming connection failed.'))
    eventSource.close()
  }

  return () => eventSource.close()
}

export async function uploadDocument(file) {
  const form = new FormData()
  form.append('document', file)

  const res = await fetch(`${API_BASE_URL}/upload-document`, {
    method: 'POST',
    body: form,
  })

  if (!res.ok) {
    const errorText = await res.text()
    throw new Error(errorText || `HTTP ${res.status}`)
  }

  return res.json()
}
