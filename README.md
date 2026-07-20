# AI Mock Interviewer - Production Server Manual

Aplikasi berbasis FastAPI, WebSockets, STT, Gemini (LLM), dan gTTS yang berjalan di server Ubuntu 24.04 LTS.

---

# Kelompok 1
-Wahid Sandy Pujo Dzulhijayanto (32602300015)
-Novi Mutiara Sari (32602300036)
-Aisyha Nurrahmah Ar-rabbani (32602300078)

---

## Arsitektur Server
- **OS**: Ubuntu Server 24.04 LTS
- **Web Server / Proxy**: Nginx
- **Aplikasi Backend**: Gunicorn + Uvicorn Workers (FastAPI)
- **Database**: SQLite (Menyimpan sesi percakapan)
- **Networking**: Cloudflare Tunnel (Bypass NAT/Firewall, SSL otomatis)

---

## 1. Instalasi Pertama Kali (Dari Awal)
Jika server harus dibangun ulang dari nol, jalankan langkah berikut:

### a. Persiapan Sistem
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx ufw fail2ban ffmpeg sqlite3
```

### b. Clone Repositori dan Setup Python
```bash
git clone <URL_REPO_GITHUB_ANDA> ai-interviewer
cd ai-interviewer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### c. Konfigurasi Environment (API Key)
Buat file `.env`:
```bash
nano .env
```
Isi dengan:
```env
GEMINI_API_KEY=KODE_API_ANDA_DI_SINI
```
Set permissions:
```bash
chmod 600 .env
```

---

## 2. Cara Deploy Update (Ketika ada perubahan di GitHub)
Gunakan skrip `deploy.sh` yang sudah dibuat di root folder:

```bash
cd /home/jules/ai-interviewer
./deploy.sh
```
Skrip ini otomatis akan:
1. Menarik (*pull*) kode terbaru dari branch `main`
2. Mengaktifkan *virtual environment*
3. Menjalankan `pip install` (jika ada dependency baru)
4. Melakukan *restart* pada *service* Gunicorn di background.

---

## 3. Cara Restart Service Secara Manual
Jika terjadi stuck atau memory leak:

- **Restart Aplikasi FastAPI Backend:**
  ```bash
  sudo systemctl restart fastapi-app
  ```
- **Restart Nginx (Web Server):**
  ```bash
  sudo systemctl restart nginx
  ```
- **Restart Cloudflare Tunnel:**
  ```bash
  sudo systemctl restart cloudflared
  ```

---

## 4. Cara Melihat Log
Jika aplikasi mengalami error (500 Internal Server Error, websocket terputus), Anda bisa melihat log secara real-time.

- **Melihat Log Aplikasi (Real-time / Tailing):**
  ```bash
  tail -f /var/log/fastapi-app/gunicorn-error.log
  tail -f /var/log/fastapi-app/gunicorn.log
  ```
- **Melihat Log Systemd (Untuk Gunicorn):**
  ```bash
  sudo journalctl -u fastapi-app -f
  ```
- **Melihat Log Nginx Akses (Siapa saja yang mengakses):**
  ```bash
  tail -f /var/log/nginx/wawancara-access.log
  ```

---

## 5. Manajemen Database (SQLite)

### File Database
Database terletak di direktori root aplikasi dengan nama `interviews.db`.

### Cara Backup Database (Sederhana)
SQLite hanya berbentuk file tunggal. Untuk mem-backup, cukup *copy* file tersebut:
```bash
# Backup manual
cp /home/jules/ai-interviewer/interviews.db /home/jules/ai-interviewer/interviews_backup_$(date +%F).db
```

### Cara Restore Database
Hentikan *service*, *copy* file *backup* ke nama asli, dan jalankan lagi.
```bash
sudo systemctl stop fastapi-app
cp /home/jules/ai-interviewer/interviews_backup_202X-XX-XX.db /home/jules/ai-interviewer/interviews.db
sudo systemctl start fastapi-app
```

---

## 6. Troubleshooting Masalah Umum

**Masalah**: Website menampilkan layar "502 Bad Gateway".
- **Penyebab**: Nginx berjalan normal, namun aplikasi FastAPI di belakang mati.
- **Solusi**: Cek status aplikasi dengan `sudo systemctl status fastapi-app`. Cek log error dengan `tail -n 50 /var/log/fastapi-app/gunicorn-error.log`. Restart service `sudo systemctl restart fastapi-app`.

**Masalah**: Website sama sekali tidak bisa diakses / Time Out / Error 1033 Cloudflare.
- **Penyebab**: Koneksi Cloudflare Tunnel terputus atau server mati internet.
- **Solusi**: Cek status tunnel dengan `sudo systemctl status cloudflared`. Restart tunnel.

**Masalah**: AI membalas "Maaf, saya tidak mendengar jawaban Anda."
- **Penyebab**: Format audio dari browser tidak dikenali atau mic rusak.
- **Solusi**: Pastikan *library* `ffmpeg` sudah terinstal di server (`sudo apt install ffmpeg`), karena modul `pydub` (STT) membutuhkannya untuk mengonversi *webm* ke *wav*.

**Masalah**: Log server terlalu besar dan menghabiskan disk.
- **Solusi**: Harusnya ini di-*handle* otomatis oleh *logrotate*. Anda bisa memaksa rotasi manual dengan: `sudo logrotate -f /etc/logrotate.d/fastapi-app`

---
*Dibuat oleh AI DevOps Engineer*
