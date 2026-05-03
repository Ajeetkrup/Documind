const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8004/api'

export async function postChatQuery(query) {
  const res = await fetch(`${API_BASE_URL}/api/chat?query=${encodeURIComponent(query)}`, {
    method: 'POST',
  })

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`)
  }

  return res.json()
}

export async function uploadDocument(file) {
  const form = new FormData()
  form.append('document', file)

  const res = await fetch(`${API_BASE_URL}/api/upload-document`, {
    method: 'POST',
    body: form,
  })

  if (!res.ok) {
    const errorText = await res.text()
    throw new Error(errorText || `HTTP ${res.status}`)
  }

  return res.json()
}
