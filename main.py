from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import logging
import os
import uuid
from stt import speech_to_text
from llm import tanya_gemini
from tts import text_to_speech
from database import init_db, clear_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inisialisasi Database SQLite
init_db()

app = FastAPI(title="AI Mock Interviewer")

# Sajikan folder static (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Generate unique session ID untuk koneksi ini
    session_id = str(uuid.uuid4())
    logger.info(f"Client terhubung. Session ID: {session_id}")

    # Kirim pesan pembuka dari HRD
    salam_pembuka = "Selamat datang di sesi wawancara. Perkenalkan diri Anda terlebih dahulu, nama dan posisi apa yang Anda lamar?"
    audio_pembuka = await asyncio.to_thread(text_to_speech, salam_pembuka)
    await websocket.send_bytes(audio_pembuka)

    try:
        while True:
            # Terima audio dari client (bytes)
            data = await websocket.receive_bytes()
            logger.info(f"Audio diterima dari {session_id}: {len(data)} bytes")

            # Kirim status processing
            await websocket.send_text("processing")

            try:
                # Step 1: STT — audio bytes → teks
                teks_user = await asyncio.to_thread(speech_to_text, data)
                logger.info(f"STT hasil untuk {session_id}: {teks_user}")

                if not teks_user or teks_user.strip() == "":
                    await websocket.send_text("error:Maaf, saya tidak mendengar jawaban Anda. Silakan ulangi.")
                    continue

                # Kirim teks yang terdeteksi ke client (untuk ditampilkan)
                await websocket.send_text(f"transcript:{teks_user}")

                # Step 2: LLM — teks → respons HRD
                respons_hrd = await tanya_gemini(session_id, teks_user)
                logger.info(f"LLM respons untuk {session_id}: {respons_hrd}")

                # Kirim teks respons ke client
                await websocket.send_text(f"response:{respons_hrd}")

                # Step 3: TTS — respons teks → audio bytes
                audio_respons = await asyncio.to_thread(text_to_speech, respons_hrd)

                # Kirim audio balik ke client
                await websocket.send_bytes(audio_respons)

            except Exception as e:
                logger.error(f"Error pipeline AI ({session_id}): {e}")
                await websocket.send_text(f"error:Terjadi kesalahan teknis: {str(e)}")

    except WebSocketDisconnect:
        logger.info(f"Client {session_id} terputus")
        clear_history(session_id)  # Optional: bersihkan riwayat saat diskonek atau biarkan saja
