"""
GeoIP and visitor intelligence service
"""
import re
from typing import Dict, Any

CITY_CACHE = {
    "127.0.0.1": {"country": "Local", "country_code": "LOC", "city": "Localhost", "region": "Dev", "latitude": 40.4168, "longitude": -3.7038},
    "localhost": {"country": "Local", "country_code": "LOC", "city": "Localhost", "region": "Dev", "latitude": 40.4168, "longitude": -3.7038}
}

def extract_client_ip(headers: dict, fallback: str = "127.0.0.1") -> str:
    cf_ip = headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    x_forwarded = headers.get("x-forwarded-for")
    if x_forwarded:
        parts = [p.strip() for p in x_forwarded.split(",")]
        for p in parts:
            if not p.startswith(("10.", "192.168.", "172.16.", "127.")):
                return p
        return parts[0]
    x_real = headers.get("x-real-ip")
    if x_real:
        return x_real.strip()
    return fallback

def detect_device_type(user_agent: str) -> str:
    ua = (user_agent or "").lower()
    if any(m in ua for m in ["iphone", "android", "mobile", "phone"]):
        return "Mobile"
    if any(t in ua for t in ["ipad", "tablet"]):
        return "Tablet"
    return "Desktop"

def resolve_geoip(ip: str) -> Dict[str, Any]:
    if ip in CITY_CACHE:
        return CITY_CACHE[ip]
    # Default lookup result
    return {
        "country": "Visitor Network",
        "country_code": "US",
        "city": "Metro Access Node",
        "region": "Global Ingress",
        "latitude": 39.8283,
        "longitude": -98.5795
    }
