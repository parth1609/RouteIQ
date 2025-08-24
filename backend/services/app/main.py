from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure environment variables are loaded from project root, regardless of CWD
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv(usecwd=True), override=True)

from backend.zendesk.zendesk_integration import ZendeskIntegration
from backend.zammad.zammad_integration import initialize_zammad_client
from .routers.zendesk_routes import router as zendesk_router
from .routers.zammad_routes import router as zammad_router
from .routers.classifier_routes import router as classifier_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared integrations here
    try:
        app.state.zendesk = ZendeskIntegration()
    except Exception as e:
        # Defer fatal errors to endpoint-level checks to keep the server up
        app.state.zendesk = None
        print(f"[lifespan] Warning: Zendesk integration failed to init: {e}")
    # Initialize Zammad client
    try:
        app.state.zammad = initialize_zammad_client()
    except Exception as e:
        app.state.zammad = None
        print(f"[lifespan] Warning: Zammad client failed to init: {e}")
    yield


app = FastAPI(title="RouteIQ API", version="1.0.0", lifespan=lifespan)

# CORS for Streamlit (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(zendesk_router, prefix="/api/v1/zendesk", tags=["zendesk"]) 
app.include_router(zammad_router, prefix="/api/v1/zammad", tags=["zammad"]) 
app.include_router(classifier_router, prefix="/api/v1/classifier", tags=["classifier"]) 


@app.get("/api/v1/health")
def health():
    status = {
        "api": "ok",
        "zendesk_integration": "ready" if getattr(app.state, "zendesk", None) else "unavailable",
        "zammad_integration": "ready" if getattr(app.state, "zammad", None) else "unavailable",
    }
    return status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.services.app.main:app", host="127.0.0.1", port=8000, reload=True)
    
# from main  dir
# python -m uvicorn backend.services.app.main:app --reload --host 127.0.0.1 --port 8000