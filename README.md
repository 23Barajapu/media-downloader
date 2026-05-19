---
title: Media Downloader
emoji: 🦖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# 🦖 Universal Media Downloader 📹🎵

[![Deployment Status](https://img.shields.io/badge/Live_Demo-Hugging_Face-orange?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/Barajapu/media-downloader)
[![Python Version](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

Aplikasi web downloader media universal yang sangat elegan, responsif, dan bertenaga tinggi. Mampu berburu dan mengunduh video maupun lagu dari **YouTube, Bstation (Bilibili), TikTok, Instagram, Twitter/X, Facebook, dan 1000+ platform lainnya** secara instan!

Didesain dengan antarmuka **Glassmorphic premium** yang responsif penuh di perangkat seluler (HP) maupun komputer (PC).

> 🚀 **Coba Demo Live Online (24/7):** [media-downloader di Hugging Face Spaces](https://huggingface.co/spaces/Barajapu/media-downloader)

---

## ✨ Fitur Unggulan

- **Dua Mode Berburu**: Mendukung unduhan video kualitas tinggi (MP4) dan ekstraksi audio lagu (MP3).
- **Pilihan Kualitas Dinamis**:
  - **Video**: Kualitas Terbaik (Maksimal), Full HD (1080p), HD (720p), Standar (480p), hingga Rendah (360p).
  - **Audio**: Ultra High (320 kbps), High (192 kbps), Standard (128 kbps), hingga Rendah (96 kbps).
- **Deteksi Platform Cerdas**: Pilihan kualitas akan otomatis disembunyikan jika platform tujuan tidak mendukungnya (misal: Twitter/X, Facebook).
- **Tombol Pembatalan (Cancel)**: Menghentikan proses download di server secara aman dan instan kapan saja.
- **Tombol Pintar Tempel/Hapus**: Tombol dinamis satu ketukan untuk membaca clipboard perangkat kamu atau membersihkan kolom input seketika dengan warna interaktif.
- **Live Logging Console**: Menampilkan catatan berburu (log progres yt-dlp) secara real-time.
- **Siap Terbang ke Cloud**: Dilengkapi dengan konfigurasi Docker untuk di-hosting gratis 24/7 di Hugging Face Spaces atau Render.com!

---

## 🛠️ Panduan Instalasi Lokal (Komputer Kamu)

### 1. Prasyarat Sistem
Pastikan komputer kamu sudah terinstal:
- [Python 3.10 atau versi terbaru](https://www.python.org/)
- **FFmpeg** (Sudah disertakan di folder utama untuk Windows).

### 2. Jalankan Aplikasi
Jalankan perintah berikut di PowerShell atau Command Prompt kamu:

```powershell
# 1. Masuk ke direktori project
cd "C:\laragon\www\media-downloader"

# 2. Instal pustaka yang dibutuhkan
pip install -r requirements.txt

# 3. Nyalakan server lokal
python app.py
```

Setelah server menyala, buka browser kamu di alamat:
- Komputer lokal: `http://127.0.0.1:5000`
- HP (Satu Jaringan Wi-Fi): Buka IP komputer kamu di port 5000 (contoh: `http://192.168.1.10:5000`)



## 🏗️ Struktur Teknologi
* **Backend**: Python 3.10, Flask (Streaming Server-Sent Events / SSE)
* **Frontend**: HTML5, Vanilla CSS Glassmorphic, Modern Javascript (ES6)
* **Downloader Engine**: `yt-dlp` (sangat dinamis dan selalu diperbarui)
* **Processor**: `FFmpeg` (penggabung audio & video instan)
* **Cloud Daemon**: Gunicorn (Multi-threaded production WSGI)

---

## 📜 Lisensi
Project ini dilisensikan di bawah **MIT License**. Bebas dikembangkan dan dimodifikasi!

Dibuat dengan 💖 oleh **Bara444**.
