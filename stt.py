import speech_recognition as sr
import io
import logging
import os
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# Inisialisasi recognizer
recognizer = sr.Recognizer()


def speech_to_text(audio_bytes: bytes) -> str:
    """
    Mengubah audio bytes (webm/ogg dari browser) menjadi teks Bahasa Indonesia.
    Menggunakan Google Speech Recognition API.
    """
    try:
        # Browser mengirim audio dalam format webm/ogg
        # Konversi ke WAV menggunakan pydub agar bisa dibaca SpeechRecognition
        audio_segment = AudioSegment.from_file(
            io.BytesIO(audio_bytes),
            format="webm"  # MediaRecorder default format
        )

        # Export ke WAV di memory
        wav_buffer = io.BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        # Baca sebagai AudioData untuk SpeechRecognition
        with sr.AudioFile(wav_buffer) as source:
            # Kurangi noise background
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio_data = recognizer.record(source)

        # Kirim ke Google Speech API — Bahasa Indonesia
        teks = recognizer.recognize_google(
            audio_data,
            language="id-ID",  # Bahasa Indonesia
            show_all=False
        )

        logger.info(f"STT berhasil: '{teks}'")
        return teks

    except sr.UnknownValueError:
        logger.warning("Google Speech tidak bisa memahami audio")
        return ""

    except sr.RequestError as e:
        logger.error(f"Error Google Speech API: {e}")
        raise Exception(f"Google Speech API error: {e}")

    except Exception as e:
        logger.error(f"Error STT: {e}")
        raise Exception(f"STT error: {e}")
