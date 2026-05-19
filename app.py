import queue
import threading
import json
import os
import ssl
import time
import yt_dlp
import urllib.request
from flask import Flask, render_template, request, Response, send_from_directory
# Patch global untuk menangani error OpenSSL 3.x [SSL: UNEXPECTED_EOF_WHILE_READING]
orig_create_default_context = ssl.create_default_context
def patched_create_default_context(*args, **kwargs):
    context = orig_create_default_context(*args, **kwargs)
    if hasattr(ssl, "OP_IGNORE_UNEXPECTED_EOF"):
        # Abaikan pemutusan koneksi sepihak yang memicu SSLEOFError
        context.options |= ssl.OP_IGNORE_UNEXPECTED_EOF
    return context
ssl.create_default_context = patched_create_default_context

app = Flask(__name__)

@app.route('/healthz')
def healthz():
    return {"status": "ok"}, 200

# ============================================================
# SELF-PING KEEP-ALIVE: Mencegah Platform menidurkan App
# secara otomatis karena dianggap idle/tidak aktif.
# ============================================================
def _keep_alive_pinger():
    """Thread daemon yang mem-ping URL App ini setiap 25 menit."""
    # Beri waktu 60 detik agar server Gunicorn selesai melakukan startup dulu
    time.sleep(60)
    
    # Deteksi URL dari Hugging Face atau Render
    space_host = os.environ.get("SPACE_HOST", "")
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "")
    
    if space_host:
        ping_url = f"https://{space_host}/"
    elif render_url:
        ping_url = render_url
    else:
        print("[KeepAlive] SPACE_HOST / RENDER_EXTERNAL_URL tidak ditemukan. Self-ping dinonaktifkan.")
        return

    print(f"[KeepAlive] Self-ping aktif. Target: {ping_url} (setiap 25 menit)")
    
    while True:
        try:
            req = urllib.request.Request(
                ping_url,
                headers={"User-Agent": "App-KeepAlive/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                print(f"[KeepAlive] Ping OK - Status: {response.status}")
        except Exception as e:
            # Abaikan error jaringan sementara, cukup log saja
            print(f"[KeepAlive] Ping gagal (akan coba lagi): {e}")
        
        # Tunggu 25 menit sebelum ping berikutnya
        time.sleep(25 * 60)

# Jalankan pinger sebagai daemon thread (otomatis mati saat server mati)
_pinger_thread = threading.Thread(target=_keep_alive_pinger, daemon=True)
_pinger_thread.start()

# Set untuk menyimpan ID download yang dibatalkan
canceled_downloads = set()

# Logger kustom untuk menangkap log dari yt-dlp dan membagikannya ke antrian (Queue)
class SSELogger:
    def __init__(self, q, download_id=None):
        self.q = q
        self.download_id = download_id

    def debug(self, msg):
        if self.download_id and self.download_id in canceled_downloads:
            raise Exception("DOWNLOAD_CANCELED")
        # Saring pesan verbose yang tidak perlu
        msg_str = str(msg).strip()
        if msg_str:
            self.q.put({"type": "log", "message": msg_str})

    def warning(self, msg):
        if self.download_id and self.download_id in canceled_downloads:
            raise Exception("DOWNLOAD_CANCELED")
        msg_str = str(msg).strip()
        if msg_str:
            self.q.put({"type": "log", "message": f"[WARNING] {msg_str}"})

    def error(self, msg):
        if self.download_id and self.download_id in canceled_downloads:
            raise Exception("DOWNLOAD_CANCELED")
        msg_str = str(msg).strip()
        if msg_str:
            self.q.put({"type": "error", "message": msg_str})

# Mengambil list proxy Indonesia gratis secara dinamis dari API publik
def get_free_indonesian_proxy():
    api_url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=ID&ssl=all&anonymity=all"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            proxies_text = response.read().decode('utf-8').strip()
            if proxies_text:
                return [p.strip() for p in proxies_text.split('\n') if p.strip()]
    except Exception as e:
        print(f"[ProxyScrape] Gagal mengambil list: {e}")
    
    fallback_url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/countries/id/data.txt"
    try:
        req = urllib.request.Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            proxies_text = response.read().decode('utf-8').strip()
            if proxies_text:
                return [p.strip() for p in proxies_text.split('\n') if p.strip()]
    except Exception as e:
        print(f"[Fallback Proxy] Gagal mengambil list: {e}")
        
    return []

# Hook kustom untuk memantau progres download secara real-time
def make_progress_hook(q, download_id=None):
    def progress_hook(d):
        if download_id and download_id in canceled_downloads:
            raise Exception("DOWNLOAD_CANCELED")
            
        if d['status'] == 'downloading':
            # 1. Hitung persentase secara presisi
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            if total > 0:
                percent = round((downloaded / total) * 100, 1)
            else:
                percent_str = d.get('_percent_str', '0.0%').replace('%', '').strip()
                try:
                    percent = float(percent_str)
                except ValueError:
                    percent = 0.0
            
            # 2. Format kecepatan tarik (Speed) mentah (hitung manual jika None pada HLS/DASH)
            speed_bytes = d.get('speed')
            elapsed = d.get('elapsed', 0)
            if speed_bytes is None and elapsed > 0 and downloaded > 0:
                speed_bytes = downloaded / elapsed
                
            if speed_bytes is not None and speed_bytes > 0:
                if speed_bytes > 1024 * 1024:
                    speed = f"{speed_bytes / (1024 * 1024):.2f} MB/s"
                elif speed_bytes > 1024:
                    speed = f"{speed_bytes / 1024:.2f} KB/s"
                else:
                    speed = f"{speed_bytes:.2f} B/s"
            else:
                speed_str = d.get('_speed_str', '')
                speed = speed_str.strip() if speed_str else 'Menghitung...'
            
            # 3. Format perkiraan waktu sisa (ETA) mentah (hitung manual jika None)
            eta_seconds = d.get('eta')
            if eta_seconds is None and speed_bytes is not None and speed_bytes > 0 and total > downloaded:
                eta_seconds = (total - downloaded) / speed_bytes
                
            if eta_seconds is not None and eta_seconds > 0:
                minutes = int(eta_seconds) // 60
                seconds = int(eta_seconds) % 60
                if minutes > 0:
                    eta = f"{minutes}m {seconds}s"
                else:
                    eta = f"{seconds}s"
            else:
                eta_str = d.get('_eta_str', '')
                eta = eta_str.strip() if eta_str else 'N/A'
            
            filename = os.path.basename(d.get('filename', ''))
            
            q.put({
                "type": "progress",
                "percent": percent,
                "speed": speed,
                "eta": eta,
                "filename": filename
            })
        elif d['status'] == 'finished':
            q.put({
                "type": "progress",
                "percent": 100.0,
                "status": "finished"
            })
    return progress_hook

# Helper untuk mencari file yang baru saja selesai diunduh
def get_latest_downloaded_file(folder):
    if not os.path.exists(folder):
        return None
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        return None
    # Cari file dengan waktu modifikasi paling akhir
    latest_file = max(files, key=os.path.getmtime)
    return os.path.basename(latest_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream_download():
    video_url = request.args.get('url')
    format_type = request.args.get('format', 'video')
    quality = request.args.get('quality', 'best')
    download_id = request.args.get('id', '')
    proxy = request.args.get('proxy', '').strip()
    if not video_url:
        return Response("data: " + json.dumps({"type": "error", "message": "URL tidak boleh kosong!"}) + "\n\n", mimetype="text/event-stream")

    def event_generator():
        q = queue.Queue()

        def start_download():
            output_folder = "Unduhan_Media"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # Konfigurasi yt-dlp dengan logger kustom dan progress hook
            if format_type == 'audio':
                preferred_quality = quality if quality in ['320', '192', '128', '96'] else '192'
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                    'nocheckcertificate': True,
                    'socket_timeout': 30,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'logger': SSELogger(q, download_id),
                    'progress_hooks': [make_progress_hook(q, download_id)],
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'ios']
                        }
                    },
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': preferred_quality,
                    }],
                }
                mode_str = f"Lagu (MP3 - {preferred_quality}kbps)"
            else:
                if quality == '1080':
                    fmt = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
                    mode_str = "Video (MP4 - 1080p)"
                elif quality == '720':
                    fmt = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
                    mode_str = "Video (MP4 - 720p)"
                elif quality == '480':
                    fmt = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
                    mode_str = "Video (MP4 - 480p)"
                elif quality == '360':
                    fmt = 'bestvideo[height<=360]+bestaudio/best[height<=360]/best'
                    mode_str = "Video (MP4 - 360p)"
                else:
                    fmt = 'bestvideo+bestaudio/best'
                    mode_str = "Video (MP4 - Kualitas Terbaik)"

                ydl_opts = {
                    'format': fmt,
                    'merge_output_format': 'mp4',
                    'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                    'nocheckcertificate': True,
                    'socket_timeout': 30,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'logger': SSELogger(q, download_id),
                    'progress_hooks': [make_progress_hook(q, download_id)],
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'ios']
                        }
                    },
                }

            try:
                # Deteksi otomatis berkas cookies.txt untuk melewati blokir cloud YouTube
                if os.path.exists("cookies.txt"):
                    ydl_opts['cookiefile'] = "cookies.txt"
                    
                # Injeksi proxy dinamis dari parameter query jika disediakan
                if proxy:
                    formatted_proxy = proxy
                    if not (proxy.startswith("http://") or proxy.startswith("https://") or proxy.startswith("socks5://") or proxy.startswith("socks4://")):
                        formatted_proxy = "http://" + proxy
                    ydl_opts['proxy'] = formatted_proxy
                    
                q.put({"type": "status", "message": f"Menghubungkan ke server media ({mode_str})..."})
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Mengirimkan pesan sukses dengan nama file agar perangkat remote bisa langsung unduh
                latest_file = get_latest_downloaded_file(output_folder)
                q.put({
                    "type": "success", 
                    "message": f"{mode_str} berhasil didownload dan disimpan!",
                    "filename": latest_file
                })
            except Exception as e:
                err_msg = str(e)
                is_bstation = any(domain in video_url.lower() for domain in ['bilibili', 'bstation', 'b.tv'])
                is_youtube = any(domain in video_url.lower() for domain in ['youtube.com', 'youtu.be'])
                
                # Deteksi jika Bstation terblokir regional atau YouTube mendeteksi bot
                should_bypass = False
                bypass_reason = ""
                if not proxy:
                    if is_bstation and ("版权地区" in err_msg or "NoneType" in err_msg or "blocked" in err_msg.lower() or "limit" in err_msg.lower() or "restricted" in err_msg.lower()):
                        should_bypass = True
                        bypass_reason = "Batas wilayah terdeteksi! Mengaktifkan Auto-Proxy Indonesia..."
                    elif is_youtube and ("confirm you" in err_msg.lower() or "bot" in err_msg.lower() or "captcha" in err_msg.lower() or "403" in err_msg.lower() or "forbidden" in err_msg.lower() or "sign in" in err_msg.lower()):
                        should_bypass = True
                        bypass_reason = "Blokir bot YouTube terdeteksi! Mengaktifkan Auto-Proxy..."

                if should_bypass:
                    q.put({"type": "status", "message": bypass_reason})
                    q.put({"type": "log", "message": "[Auto-Proxy] Mengambil daftar proxy gratis..."})
                    
                    proxies = get_free_indonesian_proxy()
                    if proxies:
                        success = False
                        # Coba maksimal 4 proxy teratas dari list
                        for idx, attempt_proxy in enumerate(proxies[:4]):
                            q.put({"type": "status", "message": f"Bypass: Mencoba Proxy {idx+1}/{min(4, len(proxies))}..."})
                            q.put({"type": "log", "message": f"[Auto-Proxy] Mencoba terhubung melalui http://{attempt_proxy}"})
                            
                            try_opts = ydl_opts.copy()
                            try_opts['proxy'] = f"http://{attempt_proxy}"
                            try_opts['socket_timeout'] = 8
                            
                            try:
                                with yt_dlp.YoutubeDL(try_opts) as ydl:
                                    ydl.download([video_url])
                                success = True
                                break
                            except Exception as proxy_err:
                                q.put({"type": "log", "message": f"[Auto-Proxy] Proxy {attempt_proxy} gagal: {proxy_err}"})
                                
                        if success:
                            latest_file = get_latest_downloaded_file(output_folder)
                            q.put({
                                "type": "success", 
                                "message": f"{mode_str} berhasil didownload melalui Auto-Proxy!",
                                "filename": latest_file
                            })
                        else:
                            q.put({"type": "error", "message": "Gagal! Semua Auto-Proxy sedang sibuk/offline. Silakan coba lagi nanti!"})
                    else:
                        q.put({"type": "error", "message": "Gagal mengambil daftar Auto-Proxy. Silakan coba beberapa saat lagi!"})
                        
                elif "DOWNLOAD_CANCELED" in err_msg:
                    q.put({"type": "status", "message": "Unduhan dibatalkan oleh Anda!"})
                    q.put({"type": "log", "message": "[System] Unduhan dibatalkan."})
                else:
                    q.put({"type": "error", "message": err_msg})
            finally:
                # Bersihkan set cancel
                if download_id in canceled_downloads:
                    try:
                        canceled_downloads.remove(download_id)
                    except KeyError:
                        pass
                # Menandakan bahwa proses selesai
                q.put({"type": "done"})

        # Menjalankan proses download di thread terpisah agar tidak memblokir Flask
        download_thread = threading.Thread(target=start_download)
        download_thread.start()

        # Dengarkan antrian (Queue) dan kirimkan datanya ke halaman web lewat SSE
        while True:
            try:
                # Batas waktu tunggu data baru 10 detik agar bisa mengirim ping berkala
                item = q.get(timeout=10.0)
                yield f"data: {json.dumps(item)}\n\n"
                
                if item.get("type") == "done":
                    break
            except queue.Empty:
                # Jika thread unduhan sudah mati dan antrian kosong, hentikan generator
                if not download_thread.is_alive():
                    break
                # Kirim keep-alive ping berupa komentar agar server reverse proxy tidak menutup koneksi
                yield ": keep-alive ping\n\n"

    return Response(
        event_generator(),
        mimetype="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Content-Type': 'text/event-stream',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/open-folder')
def open_folder():
    folder_path = os.path.abspath("Unduhan_Media")
    if os.path.exists(folder_path):
        try:
            # Perintah khusus Windows untuk membuka file explorer
            os.startfile(folder_path)
            return {"status": "success"}
        except AttributeError:
            # Di Linux / Cloud, kita abaikan karena tidak ada GUI Explorer
            return {"status": "success", "message": "Berjalan di cloud server."}
    return {"status": "error", "message": "Folder unduhan belum dibuat!"}, 404

@app.route('/download-file')
def download_file():
    filename = request.args.get('filename')
    if not filename:
        return "Nama file kosong!", 400
        
    folder_path = os.path.abspath("Unduhan_Media")
    # Kirim file dari folder unduhan ke client/browser
    return send_from_directory(folder_path, filename, as_attachment=True)

@app.route('/cancel')
def cancel_download():
    download_id = request.args.get('id')
    if download_id:
        canceled_downloads.add(download_id)
        return {"status": "success", "message": f"Download {download_id} canceled"}
    return {"status": "error", "message": "No download ID provided"}, 400


if __name__ == '__main__':
    print("==================================================")
    print(" UNIVERSAL MEDIA HUNTER WEB SERVER BERJALAN!")
    print(" Gua kamu sekarang online di jaringan lokal!")
    print(" Buka lewat komputer ini: http://127.0.0.1:5000")
    print(" Buka lewat HP (satu Wi-Fi): http://<IP-KOMPUTER-KAMU>:5000")
    print("==================================================")
    app.run(host='0.0.0.0', debug=True, port=5000)
