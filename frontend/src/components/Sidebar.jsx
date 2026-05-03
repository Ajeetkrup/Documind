import { useState, useCallback } from 'react'
import { Upload, CheckCircle2, AlertCircle, Loader2, BookOpen, FileText, X } from 'lucide-react'

const API_BASE = 'http://localhost:8000/api'
const TECH = ['FastAPI', 'LangGraph', 'ChromaDB', 'Docling', 'NVIDIA AI', 'React 19']

export default function Sidebar({ uploadedDocs, onUpload, open, onClose }) {
  const [dragOver, setDragOver]       = useState(false)
  const [uploadState, setUploadState] = useState(null)
  const [uploadMsg, setUploadMsg]     = useState('')

  const handleFile = useCallback(async (file) => {
    if (!file) return
    setUploadState('uploading')
    setUploadMsg(`Uploading ${file.name}…`)
    const form = new FormData()
    form.append('document', file)
    try {
      const res = await fetch(`${API_BASE}/upload-document`, { method: 'POST', body: form })
      if (!res.ok) throw new Error(await res.text())
      setUploadState('success')
      setUploadMsg(`${file.name} ingested!`)
      onUpload(file.name)
      setTimeout(() => setUploadState(null), 3000)
    } catch {
      setUploadState('error')
      setUploadMsg('Upload failed. Try again.')
      setTimeout(() => setUploadState(null), 4000)
    }
  }, [onUpload])

  const onDrop = (e) => {
    e.preventDefault(); setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  return (
    <>
      <div className={`sidebar-overlay ${open ? 'active' : ''}`} onClick={onClose} />
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="logo-icon"><BookOpen size={20} color="#fff" /></div>
          <span className="logo-text">Documind</span>
          <button
            className="close-sidebar-btn"
            onClick={onClose}
            aria-label="Close menu"
          >
            <X size={18} />
          </button>
        </div>

        <div className="sidebar-divider" />

        {/* Upload */}
        <div className="sidebar-section">
          <span className="sidebar-label">Upload Document</span>
          <div
            className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
          >
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.docx,.txt,.md"
              onChange={(e) => handleFile(e.target.files[0])}
            />
            <div className="upload-icon"><Upload size={28} /></div>
            <p className="upload-text"><strong>Click to upload</strong> or drag &amp; drop</p>
            <p className="upload-hint">PDF · DOCX · TXT · MD</p>
          </div>

          {uploadState && (
            <div className={`upload-status ${uploadState}`}>
              {uploadState === 'uploading' && <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />}
              {uploadState === 'success'   && <CheckCircle2 size={14} />}
              {uploadState === 'error'     && <AlertCircle size={14} />}
              {uploadMsg}
            </div>
          )}
        </div>

        {/* Ingested docs */}
        {uploadedDocs.length > 0 && (
          <div className="sidebar-section">
            <span className="sidebar-label">Ingested Documents</span>
            {uploadedDocs.map((name, i) => (
              <div className="doc-item" key={i}>
                <FileText size={14} />{name}
              </div>
            ))}
          </div>
        )}

        {/* Tech stack footer */}
        <div className="sidebar-footer">
          <span className="tech-label">Powered by</span>
          <div className="tech-badges">
            {TECH.map(t => <span className="tech-badge" key={t}>{t}</span>)}
          </div>
        </div>
      </aside>
    </>
  )
}
