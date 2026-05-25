from google import genai
from google.genai import types
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY tidak ditemukan di file .env")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """Kamu adalah seorang HRD profesional dari perusahaan teknologi ternama di Indonesia yang sedang melakukan wawancara kerja.

ATURAN PENTING:
1. Berikan respon secara profesional
2. Gunakan Bahasa Indonesia yang formal namun ramah
3. Ganti antara: memberikan pertanyaan lanjutan, memberikan komentar singkat atas jawaban kandidat, atau meminta klarifikasi
4. Jangan memberi penilaian eksplisit seperti "jawaban Anda bagus/buruk"
5. Fokus pada bidang IT: programming, sistem, manajemen proyek, soft skills
6. Bersikap profesional seperti wawancara sungguhan"""

from database import get_history, save_history, clear_history

async def tanya_gemini(session_id: str, teks_user: str) -> str:
    try:
        riwayat_chat = get_history(session_id)

        riwayat_chat.append({"role": "user", "parts": [{"text": teks_user}]})

        if len(riwayat_chat) > 10:
            riwayat_chat = riwayat_chat[-10:]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=riwayat_chat,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=200,
            )
        )

        respons_hrd = response.text.strip()

        riwayat_chat.append({"role": "model", "parts": [{"text": respons_hrd}]})

        save_history(session_id, riwayat_chat)

        logger.info(f"Gemini respons untuk sesi {session_id}: '{respons_hrd}'")
        return respons_hrd

    except Exception as e:
        logger.error(f"Error Gemini API: {e}")
        raise Exception(f"Gemini API error: {e}")

def reset_sesi(session_id: str):
    clear_history(session_id)
