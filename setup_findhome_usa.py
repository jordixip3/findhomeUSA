import os
import re

# 1. Update app/services/voice_agent_service.py
voice_agent_content = '''"""
FindHome USA — AI Voice Agent Service
Autonomous Voice Assistant for American Shared Housing & Co-Living Across All 50 US States.
Connected to official WhatsApp support line: +34 603 331 391
"""

import re
import urllib.parse
from typing import Dict, Any, List, Optional
from app.models.database import get_properties

AGENT_WHATSAPP_NUMBER = "+34603331391"
AGENT_WHATSAPP_CLEAN = "34603331391"

class USHousingVoiceAgent:
    """
    Intelligent conversational voice agent that understands American housing inquiries,
    recommends flats, calculates per-person splits in USD ($), and connects users directly
    to WhatsApp +34 603 331 391 for automated voice notes, virtual tours, and roommate reservations.
    """

    def __init__(self):
        self.whatsapp_number = AGENT_WHATSAPP_NUMBER
        self.clean_whatsapp = AGENT_WHATSAPP_CLEAN

    def process_query(self, message: str, lang: str = "en") -> Dict[str, Any]:
        msg_clean = (message or "").strip().lower()
        
        # 1. Detect greetings
        if any(w in msg_clean for w in ["hello", "hi", "hey", "good morning", "good afternoon", "hola"]):
            return self._greeting_response()

        # 2. Detect WhatsApp / Call intent
        if any(w in msg_clean for w in ["whatsapp", "wsp", "phone", "call", "contact", "agent", "human", "talk"]):
            return self._whatsapp_direct_response("Inquiring about co-living roommate matching or booking a visit")

        # 3. Detect Calculator / Split Rent intent
        calc_match = re.search(r"(\d+)\s*(people|roommates|rooms|friends|beds)", msg_clean)
        price_match = re.search(r"(\d{3,5})\s*(\$|dollars|bucks)?", msg_clean)
        if "calculate" in msg_clean or "split" in msg_clean or "share" in msg_clean or "math" in msg_clean or (calc_match and price_match):
            roommates = int(calc_match.group(1)) if calc_match else 4
            total_rent = float(price_match.group(1)) if price_match else 3200.0
            return self._calculator_response(roommates, total_rent)

        # 4. Detect State / City search intent
        us_cities = [
            "new york", "brooklyn", "manhattan", "queens", "los angeles", "san francisco",
            "san diego", "san jose", "chicago", "austin", "houston", "dallas", "miami",
            "orlando", "tampa", "seattle", "boston", "denver", "atlanta", "charlotte",
            "philadelphia", "phoenix", "portland", "las vegas", "nashville", "washington"
        ]
        matched_city = None
        for city in us_cities:
            if city in msg_clean:
                matched_city = city.title()
                break

        beds_match = re.search(r"(\d+)\s*(bedroom|bed|br|room)", msg_clean)
        bedrooms = int(beds_match.group(1)) if beds_match else None

        if matched_city or any(w in msg_clean for w in ["apartment", "house", "loft", "rent", "flat", "room"]):
            return self._property_search_response(matched_city, bedrooms)

        return self._general_advice_response(message)

    def _greeting_response(self) -> Dict[str, Any]:
        reply = (
            "Hello! I am your FindHome USA AI Voice Assistant. "
            "I can help you discover verified co-living apartments in New York, Los Angeles, Austin, Miami, Seattle, and across all 50 US States, "
            "calculate individual rent splits in USD ($), or connect you instantly with our coordinator on WhatsApp +34 603 331 391. "
            "What city or monthly budget are you looking for?"
        )
        wa_url = self.build_whatsapp_link("Hello FindHome USA Voice Agent, I would like information on finding a shared apartment in the US.")
        return {
            "reply_text": reply,
            "action": "greeting",
            "whatsapp_url": wa_url,
            "whatsapp_display": self.whatsapp_number,
            "suggested_properties": []
        }

    def _whatsapp_direct_response(self, reason: str) -> Dict[str, Any]:
        wa_text = f"Hello, I am reaching out from FindHome USA website. {reason}. I would like assistance from the AI agent."
        wa_url = self.build_whatsapp_link(wa_text)
        reply = (
            f"You can message or call our official AI coordinator on WhatsApp at {self.whatsapp_number}. "
            "You can send voice notes or text messages 24/7 for instant roommate matching, virtual tours, and lease inquiries!"
        )
        return {
            "reply_text": reply,
            "action": "open_whatsapp",
            "whatsapp_url": wa_url,
            "whatsapp_display": self.whatsapp_number,
            "suggested_properties": []
        }

    def _calculator_response(self, roommates: int, total_rent: float) -> Dict[str, Any]:
        roommates = max(1, roommates)
        per_person = round(total_rent / roommates)
        savings = max(0, 1800 - per_person)

        reply = (
            f"For a total monthly rent of ${int(total_rent):,} shared among {roommates} roommates, "
            f"each person pays only ${per_person:,} per month! "
            f"Compared to renting a solo 1-bedroom apartment in the US, you save approximately ${savings:,} every single month. "
            f"Would you like to reserve a co-living flat with this split via WhatsApp {self.whatsapp_number}?"
        )
        wa_text = f"Hi, I want to reserve a co-living flat split of ${int(total_rent)} among {roommates} roommates (${per_person}/mo per person) on FindHome USA."
        return {
            "reply_text": reply,
            "action": "calculator_result",
            "per_person": per_person,
            "total_rent": total_rent,
            "roommates": roommates,
            "whatsapp_url": self.build_whatsapp_link(wa_text),
            "whatsapp_display": self.whatsapp_number,
            "suggested_properties": []
        }

    def _property_search_response(self, city: Optional[str], bedrooms: Optional[int]) -> Dict[str, Any]:
        all_props = get_properties()
        matches = []
        for p in all_props:
            if city and city.lower() not in p.get("city", "").lower():
                continue
            if bedrooms and p.get("bedrooms", 0) < bedrooms:
                continue
            matches.append(p)

        if not matches:
            matches = all_props[:3]

        suggested = matches[:3]
        city_name = city or "major US metropolitan areas"
        best = suggested[0]
        rent_p = round(best.get("rent_per_person", 750))

        reply = (
            f"I found premier shared housing opportunities in {city_name}. "
            f"For example: '{best.get('title')}' with {best.get('bedrooms')} bedrooms for only ${rent_p:,}/mo per person. "
            f"I have highlighted {len(suggested)} options on your screen. "
            f"You can also chat directly via WhatsApp at {self.whatsapp_number} to schedule an in-person or virtual tour!"
        )
        wa_text = f"Hi, I am interested in '{best.get('title')}' in {best.get('city')} (${rent_p}/person). Can we arrange a viewing?"
        return {
            "reply_text": reply,
            "action": "property_recommendations",
            "city": city_name,
            "suggested_properties": suggested,
            "whatsapp_url": self.build_whatsapp_link(wa_text),
            "whatsapp_display": self.whatsapp_number
        }

    def _general_advice_response(self, user_msg: str) -> Dict[str, Any]:
        reply = (
            "FindHome USA empowers you to access premium, affordable housing across all 50 US States "
            "by forming co-living pods to split large apartments and townhouses. "
            f"Our AI Voice Agent is connected to WhatsApp {self.whatsapp_number}. "
            "Tell me which US city or state you want to move to, or click below to message an agent directly!"
        )
        wa_text = f"Hi, I have a question about FindHome USA: {user_msg}"
        return {
            "reply_text": reply,
            "action": "general_advice",
            "whatsapp_url": self.build_whatsapp_link(wa_text),
            "whatsapp_display": self.whatsapp_number,
            "suggested_properties": []
        }

    def build_whatsapp_link(self, message: str) -> str:
        encoded = urllib.parse.quote(message)
        return f"https://wa.me/{self.clean_whatsapp}?text={encoded}"

# Global instance
voice_agent = USHousingVoiceAgent()
'''

with open('app/services/voice_agent_service.py', 'w') as f:
    f.write(voice_agent_content)

print("Updated app/services/voice_agent_service.py")
