import os
if os.name == 'nt':
    import shutil
    def _symlink_fallback(src, dst, *args, **kwargs):
        try:
            # huggingface_hub uses relative paths for symlinks!
            if not os.path.isabs(src):
                src = os.path.normpath(os.path.join(os.path.dirname(dst), src))
                
            if os.path.isdir(src):
                import _winapi
                _winapi.CreateJunction(src, dst)
            else:
                shutil.copy2(src, dst)
        except Exception as e:
            print(f"Symlink fallback failed: {e}")
            raise OSError(e)
    os.symlink = _symlink_fallback

from phoenix.otel import register
from src.utils.config import settings

tracer_provider = register(
  project_name="documind",
  endpoint=settings.PHOENIX_COLLECTOR_ENDPOINT,
  api_key=settings.PHOENIX_API_KEY,
  auto_instrument=True
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.api import router as api_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Documind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.VITE_API_BASE_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api", tags=["API"])

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}