from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List, Dict, Any
from app.models.schemas import VoiceQueryRequest, AdminLoginRequest
from app.models.database import (
    get_properties, get_property, SUBDIVISIONS,
    get_access_logs, record_whatsapp_log, get_whatsapp_logs
)
from app.services.portal_adapter import SUPPORTED_PORTALS
from app.services.voice_agent_service import voice_agent

router = APIRouter(prefix="/api/v1", tags=["FindHome USA API"])

@router.get("/properties")
async def list_properties(
    city: Optional[str] = Query(None),
    subdivision: Optional[str] = Query(None),
    portal: Optional[str] = Query(None),
    min_bedrooms: Optional[int] = Query(None),
    max_total_rent: Optional[float] = Query(None)
):
    return get_properties(
        city=city,
        subdivision=subdivision,
        portal=portal,
        min_bedrooms=min_bedrooms,
        max_total_rent=max_total_rent
    )

@router.get("/properties/{property_id}")
async def get_property_detail(property_id: str):
    p = get_property(property_id)
    if not p:
        raise HTTPException(status_code=404, detail="Property not found")
    return p

@router.get("/portals")
async def get_portals():
    return SUPPORTED_PORTALS

@router.get("/subdivisions")
async def get_subdivisions():
    return SUBDIVISIONS

@router.post("/voice/query")
async def query_voice_agent(payload: VoiceQueryRequest):
    return voice_agent.process_query(payload.query, lang=payload.lang)

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(payload: Dict[str, Any]):
    message_text = payload.get("message", payload.get("Body", payload.get("text", "")))
    sender_phone = payload.get("from", payload.get("From", "WhatsApp Visitor"))
    sender_name = payload.get("name", payload.get("ProfileName", "Direct Inquiry"))

    result = voice_agent.process_query(message_text, lang="en")
    reply_text = result.get("reply_text", "Thank you for contacting FindHome USA. We will connect you shortly.")
    record_whatsapp_log(str(sender_phone), str(sender_name), str(message_text), str(reply_text))

    return {
        "status": "success",
        "sender": sender_phone,
        "reply": reply_text,
        "action": result.get("action"),
        "whatsapp_url": result.get("whatsapp_url")
    }

@router.get("/whatsapp/logs")
async def view_whatsapp_logs(limit: int = 50):
    return get_whatsapp_logs(limit)

@router.post("/admin/login")
async def admin_login(payload: AdminLoginRequest):
    if payload.password == "admin123":
        return {"authenticated": True, "status": "authenticated", "message": "Access granted"}
    raise HTTPException(status_code=401, detail="Invalid administrator credentials")

@router.get("/admin/access-logs")
async def fetch_access_logs(limit: int = 100):
    return get_access_logs(limit)

@router.get("/admin/stats")
async def fetch_admin_stats():
    logs = get_access_logs(500)
    total = len(logs)
    countries = set(l.get("country", "") for l in logs if l.get("country"))
    cities = set(l.get("city", "") for l in logs if l.get("city"))
    return {
        "total_visits": total,
        "unique_countries": len(countries),
        "unique_cities": len(cities),
        "active_subscribers": 142
    }
