from gtts import gTTS
import io
import logging

logger = logging.getLogger(__name__)


def text_to_speech(teks: str) -> bytes:
    """
    Mengubah teks Bahasa Indonesia menjadi audio bytes (MP3).
    Menggunakan gTTS (Google Text-to-Speech) — gratis, tidak perlu API key.
    """
    try:
        if not teks or teks.strip() == "":
            raise ValueError("Teks kosong, tidak bisa dikonversi ke audio")

        # Buat objek gTTS
        tts = gTTS(
            text=teks,
            lang="id",       # Bahasa Indonesia
            slow=False,      # Kecepatan normal
            tld="co.id"      # Domain Indonesia untuk aksen lebih natural
        )

        # Simpan ke buffer memory (tidak perlu tulis ke disk)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        audio_bytes = audio_buffer.read()
        logger.info(f"TTS berhasil: {len(audio_bytes)} bytes audio dihasilkan")

        return audio_bytes

    except Exception as e:
        logger.error(f"Error TTS: {e}")
        raise Exception(f"TTS error: {e}")
