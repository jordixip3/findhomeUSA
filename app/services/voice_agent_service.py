"""
AI Voice Assistant for FindHome USA
"""
import re
import urllib.parse
from typing import Dict, Any, Optional

AGENT_WHATSAPP_NUMBER = "+34603331391"
AGENT_WHATSAPP_CLEAN = "34603331391"

class LocalizedVoiceAgent:
    def __init__(self):
        self.whatsapp_number = AGENT_WHATSAPP_NUMBER
        self.clean_whatsapp = AGENT_WHATSAPP_CLEAN
        self.brand = "FindHome USA"
        self.currency = "$"
        self.lang = "en"

    def process_query(self, message: str, lang: str = "en") -> Dict[str, Any]:
        msg_clean = (message or "").strip().lower()

        # Greetings
        if any(w in msg_clean for w in ["hello", "hi", "hey", "hola", "buenos dias", "buenas tardes"]):
            return self._greeting_response()

        # WhatsApp intent
        if any(w in msg_clean for w in ["whatsapp", "wsp", "phone", "telefono", "call", "llamar", "contact", "contacto", "humano", "agent"]):
            return self._whatsapp_response("Inquiring about roommate matching and viewing appointments")

        # Calculator intent
        calc_match = re.search(r"(\d+)\s*(personas|roommates|amigos|people|rooms|camas|habitaciones)", msg_clean)
        price_match = re.search(r"(\d[\d\.,](2,))", msg_clean)
        if any(k in msg_clean for k in ["calcular", "calculate", "split", "repartir", "arriendo", "rent", "cuanto"]) or (calc_match and price_match):
            roommates = int(calc_match.group(1)) if calc_match else 4
            raw_p = price_match.group(1).replace(".", "").replace(",", "") if price_match else "3000"
            try:
                total_rent = float(raw_p)
            except Exception:
                total_rent = 3000.0
            return self._calculator_response(roommates, total_rent)

        # General advice
        return self._general_response(message)

    def _greeting_response(self) -> Dict[str, Any]:
        reply = "Hello! I am your AI Voice Assistant for FindHome USA. I can help you find verified shared apartments, calculate per-person rent splits in $, or connect directly to our coordinator on WhatsApp +34 603 331 391. What location or budget are you looking for?"
        wa_url = self.build_whatsapp_link(f"Hello FindHome USA, I am looking for shared housing options.")
        return {
            "reply_text": reply,
            "action": "greeting",
            "whatsapp_url": wa_url,
            "whatsapp_display": self.whatsapp_number
        }

    def _whatsapp_response(self, reason: str) -> Dict[str, Any]:
        wa_text = f"Hello, I am reaching out from FindHome USA website. {reason}."
        wa_url = self.build_whatsapp_link(wa_text)
        reply = (
            f"You can message or call our official coordinator on WhatsApp at {self.whatsapp_number} for instant 24/7 assistance!"
            if "en" == "en" else
            f"Puedes escribirnos o llamarnos directamente a nuestro WhatsApp oficial {self.whatsapp_number} con atención 24/7."
        )
        return {
            "reply_text": reply,
            "action": "open_whatsapp",
            "whatsapp_url": wa_url,
            "whatsapp_display": self.whatsapp_number
        }

    def _calculator_response(self, roommates: int, total_rent: float) -> Dict[str, Any]:
        roommates = max(1, roommates)
        per_person = round(total_rent / roommates)
        reply = (
            f"For a total monthly rent of {self.currency} {int(total_rent):,} split among {roommates} roommates, "
            f"each person pays only {self.currency} {int(per_person):,} per month! "
            f"Would you like to reserve a flat with this split via WhatsApp {self.whatsapp_number}?"
            if "en" == "en" else
            f"Para un arriendo total de {self.currency} {int(total_rent):,} compartido entre {roommates} personas, "
            f"cada una paga solo {self.currency} {int(per_person):,} al mes. "
            f"¿Deseas reservar tu cupo o agendar una visita por WhatsApp al {self.whatsapp_number}?"
        )
        wa_text = f"Hi, I want to reserve a flat split of $ {int(total_rent)} among {roommates} roommates ($ {int(per_person)}/mo per person) on FindHome USA."
        return {
            "reply_text": reply,
            "action": "calculator_result",
            "per_person": per_person,
            "total_rent": total_rent,
            "roommates": roommates,
            "whatsapp_url": self.build_whatsapp_link(wa_text),
            "whatsapp_display": self.whatsapp_number
        }

    def _general_response(self, user_msg: str) -> Dict[str, Any]:
        reply = (
            f"FindHome USA enables you to access premium, spacious housing by forming verified minicommunities. "
            f"Our AI Voice Agent is connected directly to WhatsApp {self.whatsapp_number}. Tell me what city you prefer!"
            if "en" == "en" else
            f"FindHome USA te permite acceder a viviendas amplias y dignas mediante minicomunidades verificadas. "
            f"Nuestro agente de voz está conectado a WhatsApp {self.whatsapp_number}. ¿En qué ciudad deseas vivir?"
        )
        wa_text = f"Hi, inquiry on FindHome USA: {user_msg}"
        return {
            "reply_text": reply,
            "action": "general_advice",
            "whatsapp_url": self.build_whatsapp_link(wa_text),
            "whatsapp_display": self.whatsapp_number
        }

    def build_whatsapp_link(self, message: str) -> str:
        encoded = urllib.parse.quote(message)
        return f"https://wa.me/{self.clean_whatsapp}?text={encoded}"

voice_agent = LocalizedVoiceAgent()
