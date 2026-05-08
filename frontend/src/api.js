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

export function streamChatQuery(query, { onToken, onDone, onError }) {
  const streamUrl = `${API_BASE_URL}/chat/stream?query=${encodeURIComponent(query)}`
  const eventSource = new EventSource(streamUrl)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      if (data?.token) {
        onToken?.(data.token)
      }

      if (data?.done) {
        onDone?.()
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
