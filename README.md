---
title: Media Downloader
emoji: 🦖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.19.2
app_file: app.py
---

# 🦖 Universal Media Downloader

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![yt-dlp](https://img.shields.io/badge/Powered_by-yt--dlp-FF0000?style=flat-square)](https://github.com/yt-dlp/yt-dlp)
[![License](https://img.shields.io/badge/License-MIT-8B5CF6?style=flat-square)](LICENSE)

Unduh video & lagu dari **YouTube, Bstation, TikTok, Instagram, Twitter/X, Facebook**, dan 1000+ platform lainnya — langsung dari browser, tanpa install apa pun.

---

## 📖 Cara Menggunakan

### 1. Pilih Mode

| Mode | Hasil |
|------|-------|
| 🎬 **Video (MP4)** | Video lengkap beserta audio |
| 🎵 **Audio (MP3)** | Hanya suaranya saja |

### 2. Masukkan URL

Tempel link video ke kolom input. Gunakan tombol **📋 Tempel** untuk mengisi otomatis dari clipboard, atau **✕ Hapus** untuk mengosongkan.

**Platform yang didukung (contoh):**
```
https://www.youtube.com/watch?v=...
https://www.bilibili.com/video/...
https://www.tiktok.com/@user/video/...
https://www.instagram.com/p/...
https://twitter.com/user/status/...
```

### 3. Pilih Kualitas

**Video:**

| Pilihan | Keterangan |
|---------|------------|
| ⭐ Terbaik | Resolusi tertinggi yang tersedia |
| Full HD | 1080p |
| HD | 720p |
| Standar | 480p |
| Rendah | 360p |

**Audio:**

| Pilihan | Bitrate |
|---------|---------|
| Ultra High | 320 kbps |
| High | 192 kbps |
| Standard | 128 kbps |
| Rendah | 96 kbps |

> Beberapa platform (Twitter/X, Facebook) tidak memiliki pilihan kualitas karena hanya menyediakan satu format.

### 4. Mulai Unduh

Klik **🦖 Mulai Berburu!** — progres unduhan akan tampil secara real-time:
- **Status** — tahap proses saat ini
- **Log Konsol** — catatan teknis dari yt-dlp
- **Progress Bar** — persentase, kecepatan, dan estimasi waktu

### 5. Simpan File

Setelah selesai, klik tombol **⬇️ Unduh File** yang muncul untuk menyimpan file ke perangkat kamu.

---

## 🛡️ Fitur Cerdas

**Auto-Bypass Wilayah**
Jika konten Bstation/Bilibili diblokir karena wilayah (`版权地区受限`), sistem secara otomatis akan mencari dan mencoba proxy Indonesia. Tidak perlu melakukan apa pun.

**Anti-Bot YouTube**
Jika YouTube mendeteksi server sebagai bot, sistem akan otomatis beralih ke proxy alternatif.

**Tombol Batalkan**
Tekan **✕ Batalkan Unduhan** kapan saja untuk menghentikan proses secara aman.

---

## ⚙️ Opsi Lanjutan

Klik **⚙️ Opsi Lanjutan** untuk mengisi proxy manual (opsional):
```
http://ALAMAT_IP:PORT
```
Biarkan kosong untuk menggunakan Auto-Proxy bawaan.

---

## ❓ FAQ

**Muncul error "Sign in to confirm you're not a bot" dari YouTube?**
> Server cloud terdeteksi sebagai bot. Sistem akan otomatis mencoba proxy. Jika gagal terus, coba beberapa menit lagi.

**Bstation gagal karena wilayah terblokir?**
> Fitur Auto-Proxy Indonesia akan aktif secara otomatis.

**Ada batasan ukuran file?**
> Tidak ada dari sisi aplikasi. File >2GB membutuhkan waktu lebih lama.

**Format output apa yang tersedia?**
> **MP4** untuk video, **MP3** untuk audio. Konversi dilakukan otomatis oleh FFmpeg.

---

## 🏗️ Stack Teknologi

| Lapisan | Teknologi |
|---------|-----------|
| Backend | Python 3.10 · Flask · SSE Streaming |
| Frontend | HTML5 · Vanilla CSS Glassmorphic · JavaScript ES6 |
| Engine | yt-dlp |
| Processor | FFmpeg |
| Server | Gunicorn (multi-thread) |
| Container | Docker |

---

Dibuat dengan 💖 oleh **Bara444** · Lisensi MIT
