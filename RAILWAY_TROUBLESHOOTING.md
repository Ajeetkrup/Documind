# Documind Railway Deployment Troubleshooting Guide

This document captures the deployment/runtime issues encountered while deploying the Documind backend to Railway, with practical fixes that can be applied quickly.

---

## 1. Docker Build Command Fails (`buildx requires 1 argument`)
**Error:**  
`docker: 'docker buildx build' requires 1 argument`

**Where it happened:**  
Local terminal while building the backend image.

**Root Cause:**  
`docker build` was executed without a build context path.

**Resolution:**  
Pass the context explicitly.

```bash
# If currently inside server/
docker build -t documind-server .

# If currently at repo root
docker build -t documind-server -f server/Dockerfile server
```

---

## 2. `pip install -r requirements.txt` Fails With Invalid Requirement + Null Bytes
**Error:**  
`Invalid requirement: 'a\x00r\x00i\x00z\x00e...'`

**Where it happened:**  
Railway build stage (and reproducible locally).

**Root Cause:**  
`server/requirements.txt` was saved in UTF-16/UTF-16LE, so `pip` read null-byte-separated text.

**Resolution:**  
Resave `requirements.txt` as UTF-8 (no BOM preferred).  
Then redeploy with cleared build cache.

**Verification command:**
```bash
python -c "from pathlib import Path; b=Path('requirements.txt').read_bytes(); print(b'\\x00' in b)"
```
Expected output: `False`

---

## 3. Container Fails Loading ONNX Model (`onnx_output` treated as HF repo)
**Error:**  
`OSError: onnx_output is not a local folder and is not a valid model identifier`

**Where it happened:**  
Runtime during document upload (embedding initialization).

**Root Cause:**  
`model_path='onnx_output'` is used in code, but the model folder was missing in the container image.  
Transformers then interpreted `onnx_output` as a Hugging Face repo ID and attempted a network fetch.

**Resolution:**  
Bundle model assets in image and use an explicit container path:

```dockerfile
COPY ./onnx_output /src/onnx_output
ENV ONNX_MODEL_PATH=/src/onnx_output
```

And ensure application code reads the env-backed path for model loading.

---

## 4. Runtime Crash on Upload (`ImportError: libxcb.so.1`)
**Error:**  
`ImportError: libxcb.so.1: cannot open shared object file`

**Where it happened:**  
During PDF processing (Docling -> tableformer -> `cv2` import).

**Root Cause:**  
The slim Python image on Railway lacked Linux shared libraries required by OpenCV.

**Resolution:**  
Install required apt packages in Dockerfile:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 libxcb1 \
    && rm -rf /var/lib/apt/lists/*
```

Also prefer headless OpenCV in server environments:

```text
opencv-python-headless
```

## 5. Phoenix Warning: Endpoint Protocol Could Not Be Inferred
**Warning:**  
`Could not infer collector endpoint protocol, defaulting to HTTP`

**Where it happened:**  
Backend startup logs.

**Root Cause:**  
Collector endpoint format may be missing or malformed at startup (for example missing `https://`).

**Resolution:**  
Ensure endpoint is set with full scheme:

```env
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/<tenant-path>/v1/traces
```

---

## 6. Phoenix Warning: No OpenInference Instrumentors Found
**Warning:**  
`No OpenInference instrumentors found... Skipping auto-instrumentation`

**Where it happened:**  
Backend startup logs with `auto_instrument=True`.

**Root Cause:**  
OpenInference instrumentation packages were not installed, so no auto-spans were created for framework components.

**Resolution:**  
Install instrumentation dependencies in backend requirements:

```text
openinference-instrumentation-langchain
```

Then rebuild/redeploy and validate traces in Arize Phoenix.

---

## 7. Railway Port/Startup Pitfall
**Symptom:**  
Service builds but may fail health checks or not respond correctly.

**Root Cause:**  
App runs on fixed port while Railway expects service to bind to `$PORT`.

**Resolution Options:**

- Set Railway Start Command override:
  ```bash
  sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-80}"
  ```
- Or update Docker `CMD` to a shell form that reads `${PORT}`.

---

## 8. Deployment Mode Conflict (Dockerfile vs Custom Build Commands)
**Symptom:**  
Inconsistent behavior, duplicate installs, or conflicting build steps.

**Root Cause:**  
Using Dockerfile deployment while also setting Railway custom install/build commands (for example `pip install -r requirements.txt`).

**Resolution:**  
Use one strategy only:

- **Dockerfile mode:** keep Railway install/build commands empty.
- Set Railway root directory to `server`.
- Let Dockerfile control dependency install and startup (or only override start command if needed).

---

## 9. Recommended Railway Checklist (Backend)
1. Root Directory = `server`
2. Builder = Dockerfile
3. No custom install/build commands in Railway
4. Start command override set **or** Docker CMD handles `${PORT}`
5. Required env vars configured:
   - `GROQ_API_KEY`
   - `PHOENIX_API_KEY`
   - `PHOENIX_COLLECTOR_ENDPOINT`
   - `VITE_API_BASE_URL` (frontend origin)
   - `ONNX_MODEL_PATH` (if using env path)
6. `requirements.txt` is UTF-8
7. Image includes `onnx_output`
8. Linux shared libs for OpenCV installed
9. Redeploy with cleared build cache after major dependency/config changes

---

## Notes
- Startup may be slower during first run because OCR/ML assets can download at runtime.
- Consider adding a persistent volume for `chroma_db` if you need data persistence across restarts.
