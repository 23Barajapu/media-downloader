import os
import tempfile
import urllib.request
import yt_dlp
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# Inisialisasi Supabase Client jika Environment Variables tersedia
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "media-downloads")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[Supabase] Client berhasil terhubung.")
    except Exception as e:
        print(f"[Supabase] Gagal terhubung: {e}")

# Tulis cookies.txt dinamis jika ada env COOKIES_CONTENT
cookies_content = os.environ.get("COOKIES_CONTENT", "")
if cookies_content.strip():
    try:
        with open("/tmp/cookies.txt", "w", encoding="utf-8") as f:
            f.write(cookies_content)
    except Exception:
        pass

def get_free_indonesian_proxy():
    api_url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=ID&ssl=all&anonymity=all"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            proxies_text = response.read().decode('utf-8').strip()
            if proxies_text:
                return [p.strip() for p in proxies_text.split('\n') if p.strip()]
    except Exception:
        pass
    return []

@app.route('/api/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "ok", "supabase": supabase is not None}), 200

@app.route('/api/download', methods=['POST'])
def handle_download():
    data = request.get_json() or {}
    video_url = data.get('url', '').strip()
    format_type = data.get('format', 'video')
    quality = data.get('quality', 'best')

    if not video_url:
        return jsonify({"status": "error", "message": "URL tidak boleh kosong!"}), 400

    tmp_dir = tempfile.gettempdir()
    output_template = os.path.join(tmp_dir, '%(title)s.%(ext)s')

    if format_type == 'audio':
        pref_q = quality.replace("kbps", "").strip() if "kbps" in str(quality) else "192"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'nocheckcertificate': True,
            'socket_timeout': 30,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'extractor_args': {'youtube': {'player_client': ['tv_embedded', 'mweb', 'web_creator']}},
            'geo_bypass': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': pref_q,
            }],
        }
        mode_str = f"Lagu (MP3 - {pref_q}kbps)"
    else:
        q_map = {
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]/best',
        }
        fmt = q_map.get(str(quality), 'bestvideo+bestaudio/best')
        ydl_opts = {
            'format': fmt,
            'merge_output_format': 'mp4',
            'outtmpl': output_template,
            'nocheckcertificate': True,
            'socket_timeout': 30,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'extractor_args': {'youtube': {'player_client': ['tv_embedded', 'mweb', 'web_creator']}},
            'geo_bypass': True,
        }
        mode_str = f"Video ({quality})"

    if os.path.exists("/tmp/cookies.txt"):
        ydl_opts['cookiefile'] = "/tmp/cookies.txt"

    downloaded_file = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            if os.path.exists(filename):
                downloaded_file = filename
    except Exception as e:
        # Fallback auto-proxy
        proxies = get_free_indonesian_proxy()
        for attempt_proxy in proxies[:3]:
            try:
                try_opts = ydl_opts.copy()
                try_opts['proxy'] = f"http://{attempt_proxy}"
                try_opts['socket_timeout'] = 10
                with yt_dlp.YoutubeDL(try_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    filename = ydl.prepare_filename(info)
                    if format_type == 'audio':
                        filename = os.path.splitext(filename)[0] + '.mp3'
                    if os.path.exists(filename):
                        downloaded_file = filename
                        break
            except Exception:
                continue

    if not downloaded_file or not os.path.exists(downloaded_file):
        return jsonify({"status": "error", "message": "Gagal mengunduh media dari URL tersebut."}), 500

    base_name = os.path.basename(downloaded_file)
    download_url = ""

    # Unggah ke Supabase Storage jika terhubung
    if supabase:
        try:
            with open(downloaded_file, 'rb') as f:
                storage_path = f"downloads/{base_name}"
                supabase.storage.from_(SUPABASE_BUCKET).upload(
                    file=f,
                    path=storage_path,
                    file_options={"upsert": "true"}
                )
                download_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)

            # Catat ke Database Supabase
            try:
                supabase.table("downloads").insert({
                    "title": base_name,
                    "url": video_url,
                    "download_url": download_url,
                    "mode": mode_str
                }).execute()
            except Exception as db_err:
                print(f"[Supabase DB Error] {db_err}")

        except Exception as storage_err:
            print(f"[Supabase Storage Error] {storage_err}")

    # Bersihkan file dari /tmp serverless
    try:
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
    except Exception:
        pass

    return jsonify({
        "status": "success",
        "message": f"{mode_str} berhasil diproses!",
        "filename": base_name,
        "download_url": download_url
    }), 200

# Handler untuk Vercel Serverless WSGI
if __name__ == '__main__':
    app.run()
