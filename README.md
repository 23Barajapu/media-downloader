---
title: Media Downloader
emoji: 🦖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# 🦖 Universal Media Downloader — Panduan Pengguna

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Powered By](https://img.shields.io/badge/Powered_By-yt--dlp-red?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

Aplikasi web untuk mengunduh video dan lagu dari **YouTube, Bstation, TikTok, Instagram, Twitter/X, Facebook, dan 1000+ platform lainnya** — langsung dari browser, tanpa install aplikasi apa pun!

---

## 🚀 Cara Menggunakan

### 1. Pilih Mode Unduhan

Di bagian paling atas halaman, kamu akan menemukan dua tombol pilihan mode:

| Mode | Ikon | Fungsi |
|------|------|--------|
| **Video (MP4)** | 🎬 | Mengunduh video lengkap dengan audio |
| **Audio (MP3)** | 🎵 | Mengekstrak hanya suara/lagu dari video |

Klik salah satu untuk memilih mode yang kamu inginkan.

---

### 2. Tempel URL Video

Di kolom input bertuliskan **"Tempel URL video di sini..."**, masukkan link/URL video yang ingin kamu unduh.

**Tips cepat:**
- Klik tombol **📋 Tempel** untuk langsung menempelkan URL dari clipboard kamu.
- Klik tombol **✕ Hapus** untuk mengosongkan kolom input seketika.

**Contoh URL yang didukung:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.bilibili.com/video/BV1xx411c7mu
https://www.tiktok.com/@username/video/123456
https://www.instagram.com/p/AbCdEfG/
https://twitter.com/user/status/123456789
```

---

### 3. Pilih Kualitas (Opsional)

Setelah URL dimasukkan, pilih kualitas yang diinginkan:

**Untuk Video (MP4):**
| Pilihan | Resolusi |
|---------|----------|
| ⭐ Terbaik | Kualitas maksimal yang tersedia |
| Full HD | 1080p |
| HD | 720p |
| Standar | 480p |
| Rendah | 360p |

**Untuk Audio (MP3):**
| Pilihan | Bitrate |
|---------|---------|
| Ultra High | 320 kbps |
| High | 192 kbps |
| Standard | 128 kbps |
| Rendah | 96 kbps |

> **Catatan:** Untuk beberapa platform seperti Twitter/X dan Facebook, pilihan kualitas disembunyikan secara otomatis karena platform tersebut hanya menyediakan satu kualitas.

---

### 4. Klik Tombol Download

Klik tombol besar **"🦖 Mulai Berburu!"** untuk memulai proses pengunduhan.

Selama proses berlangsung, kamu akan melihat:
- **Status** — menampilkan tahap proses saat ini (misal: *Mengunduh...*, *Memproses...*)
- **Log Konsol** — catatan teknis detail dari proses pengunduhan secara real-time
- **Progress Bar** — persentase unduhan, kecepatan, dan estimasi waktu selesai

---

### 5. Unduh File ke Perangkat Kamu

Setelah proses selesai, tombol **"⬇️ Unduh File"** akan muncul secara otomatis.

Klik tombol tersebut untuk menyimpan file video/audio langsung ke perangkat kamu.

---

## 🔄 Fitur Auto-Bypass Wilayah (Bstation)

Jika kamu mengunduh konten Bstation/Bilibili yang diblokir berdasarkan wilayah (ditandai dengan pesan error `版权地区受限`), aplikasi ini akan **otomatis** mencoba menemukan jalur alternatif melalui proxy Indonesia.

Kamu **tidak perlu melakukan apa pun** — sistem akan bekerja sendiri dan memberi tahu progresnya di konsol log.

---

## ⚙️ Opsi Lanjutan (Advanced)

Klik tombol **"⚙️ Opsi Lanjutan"** untuk membuka panel pengaturan tambahan.

**Kolom Proxy Manual:**
Jika kamu memiliki alamat proxy pribadi (misal: proxy premium), kamu bisa memasukkannya di sini dalam format:
```
http://ALAMAT_IP:PORT
```
Biarkan kosong jika ingin menggunakan sistem Auto-Proxy bawaan.

---

## ❌ Membatalkan Unduhan

Jika ingin menghentikan proses yang sedang berjalan, klik tombol **"✕ Batalkan Unduhan"** yang muncul saat proses sedang berlangsung. Server akan menghentikan proses secara aman dan instan.

---

## ❓ FAQ — Pertanyaan Umum

**Q: Mengapa muncul error "Sign in to confirm you're not a bot" saat mengunduh dari YouTube?**
> A: IP server cloud terdeteksi sebagai bot oleh YouTube. Sistem akan otomatis mencoba menggunakan proxy alternatif. Jika terus gagal, coba lagi beberapa menit kemudian.

**Q: Mengapa unduhan Bstation gagal dengan pesan wilayah terblokir?**
> A: Bstation membatasi beberapa konten hanya untuk wilayah tertentu. Fitur Auto-Proxy akan otomatis aktif untuk mencoba melewati batasan ini.

**Q: Apakah ada batasan ukuran file?**
> A: Tidak ada batasan ukuran dari sisi aplikasi. Namun, unduhan file yang sangat besar (>2GB) mungkin membutuhkan waktu lebih lama tergantung kecepatan server.

**Q: Format apa yang didukung untuk output?**
> A: **MP4** untuk video dan **MP3** untuk audio. Konversi dilakukan otomatis menggunakan FFmpeg di sisi server.

---

## 🏗️ Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python 3.10 + Flask (SSE Streaming) |
| Frontend | HTML5 + Vanilla CSS Glassmorphic + JavaScript ES6 |
| Downloader | `yt-dlp` |
| Processor | `FFmpeg` |
| Server | Gunicorn (multi-thread) |
| Container | Docker |

---

## 📜 Lisensi

Dilisensikan di bawah **MIT License**. Bebas dikembangkan dan dimodifikasi!

Dibuat dengan 💖 oleh **Bara444**.
