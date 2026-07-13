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

SYSTEM_PROMPT = """Kamu adalah seorang Rekruter/HRD profesional di sebuah perusahaan IT yang sedang mewawancarai kandidat.

ATURAN PENTING:
1. Berperanlah sebagai pewawancara sungguhan. DILARANG menggunakan placeholder (seperti [Nama Perusahaan]).
2. Jangan pernah mengulang sapaan pembuka. Wawancara sudah dimulai.
3. Gunakan Bahasa Indonesia yang profesional dan ramah.
4. Tanggapi jawaban kandidat secara singkat dan apresiatif.
5. Fokus pertanyaan pada hal-hal STRATEGIS di bidang IT (misalnya: arsitektur sistem, skalabilitas, problem-solving tingkat lanjut, resolusi konflik, atau pengambilan keputusan teknis). Hindari pertanyaan dasar.
6. Buat respon ringkas dan padat (maksimal 2-3 kalimat) agar terdengar natural saat diucapkan sebagai suara."""

from database import get_history, save_history, clear_history

async def tanya_gemini(session_id: str, teks_user: str) -> str:
    try:
        riwayat_chat = get_history(session_id)

        # Jika riwayat kosong, masukkan konteks sapaan pertama agar AI nyambung
        if not riwayat_chat:
            riwayat_chat.append({"role": "user", "parts": [{"text": "(Kandidat siap memulai wawancara)"}]})
            riwayat_chat.append({"role": "model", "parts": [{"text": "Selamat datang di sesi wawancara. Perkenalkan diri Anda terlebih dahulu, nama dan posisi apa yang Anda lamar?"}]})

        riwayat_chat.append({"role": "user", "parts": [{"text": teks_user}]})

        # Hitung sudah berapa kali kandidat menjawab
        jumlah_tanya_jawab = len([msg for msg in riwayat_chat if msg["role"] == "user"]) - 1 # dikurangi 1 untuk konteks awal

        # Modifikasi prompt secara dinamis berdasarkan jumlah pertanyaan
        prompt_dinamis = SYSTEM_PROMPT
        if jumlah_tanya_jawab >= 7:
            prompt_dinamis += "\n\nPERHATIAN: Wawancara sudah mencapai 7 pertanyaan dan HARUS DIAKHIRI SEKARANG. JANGAN memberikan pertanyaan baru. Cukup ucapkan terima kasih atas waktunya, beri tahu kandidat bahwa wawancara telah selesai, dan sampaikan salam penutup dengan sopan."
        else:
            prompt_dinamis += f"\n\nPERHATIAN: Saat ini kita berada di tahapan ke-{jumlah_tanya_jawab} dari 7 pertanyaan. Kamu HARUS mengakhiri responmu dengan 1 pertanyaan strategis baru untuk menggali kemampuan teknis/kepemimpinan kandidat."

        # Potong riwayat jika terlalu panjang, pastikan jumlah yang dipotong GENAP 
        # agar riwayat selalu diawali oleh role 'user'
        if len(riwayat_chat) > 10:
            potong = len(riwayat_chat) - 10
            if potong % 2 != 0:
                potong += 1
            riwayat_chat = riwayat_chat[potong:]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=riwayat_chat,
            config=types.GenerateContentConfig(
                system_instruction=prompt_dinamis,
                max_output_tokens=300,
                temperature=0.7,
            )
        )

        respons_hrd = response.text.strip()

        riwayat_chat.append({"role": "model", "parts": [{"text": respons_hrd}]})

        save_history(session_id, riwayat_chat)

        logger.info(f"Gemini respons untuk sesi {session_id} (Turn {jumlah_tanya_jawab}): '{respons_hrd}'")
        return respons_hrd

    except Exception as e:
        logger.error(f"Error Gemini API: {e}")
        raise Exception(f"Gemini API error: {e}")

def reset_sesi(session_id: str):
    clear_history(session_id)
