import os
import sys
import asyncio

if sys.platform == "darwin":
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models.database import init_db
from app.routers import api

init_db()

app = FastAPI(
    title="FindHome USA — Shared Housing & Co-Living Platform",
    description="Discover verified apartments, calculate fair per-person rent splits in USD, and connect with compatible roommates.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def visitor_tracking_middleware(request, call_next):
    response = await call_next(request)
    path = request.url.path
    if not any(path.endswith(ext) for ext in [".css", ".js", ".jpg", ".png", ".jpeg", ".ico", ".svg", ".woff", ".woff2", ".map"]) and not "/static" in path:
        try:
            from app.services.geoip_service import extract_client_ip, resolve_geoip, detect_device_type
            from app.models.database import record_access_log

            headers = dict(request.headers)
            client_host = request.client.host if request.client else "127.0.0.1"
            ip = extract_client_ip(headers, client_host)
            ua = headers.get("user-agent", "")
            dev = detect_device_type(ua)
            geo = resolve_geoip(ip)

            record_access_log(
                ip=ip,
                country=geo.get("country", "Global"),
                country_code=geo.get("country_code", "UN"),
                region=geo.get("region", ""),
                city=geo.get("city", "Metro"),
                latitude=geo.get("latitude", 0.0),
                longitude=geo.get("longitude", 0.0),
                path=path,
                method=request.method,
                status_code=response.status_code,
                user_agent=ua,
                device_type=dev
            )
        except Exception:
            pass
    return response

app.include_router(api.router)

# Mount static files under both /static and /USA/static
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/USA/static", StaticFiles(directory=static_dir), name="static_routed")
    app.mount("/usa/static", StaticFiles(directory=static_dir), name="static_routed_lower")

@app.get("/", include_in_schema=False)
@app.get("/USA", include_in_schema=False)
@app.get("/USA/", include_in_schema=False)
@app.get("/usa", include_in_schema=False)
@app.get("/usa/", include_in_schema=False)
async def serve_home():
    idx = os.path.join(static_dir, "index.html")
    if os.path.exists(idx):
        return FileResponse(idx, headers={"Cache-Control": "no-cache"})
    return {"message": "FindHome USA API operational"}
