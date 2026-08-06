from http.server import BaseHTTPRequestHandler
import json
import os
import tempfile
import urllib.request
import yt_dlp

# Supabase init
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "media-downloads")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        pass

# Cookies
cookies_content = os.environ.get("COOKIES_CONTENT", "")
if cookies_content.strip():
    try:
        with open("/tmp/cookies.txt", "w", encoding="utf-8") as f:
            f.write(cookies_content)
    except Exception:
        pass


def get_free_proxy():
    api_url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=ID&ssl=all&anonymity=all"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode('utf-8').strip()
            if text:
                return [p.strip() for p in text.split('\n') if p.strip()]
    except Exception:
        pass
    return []


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}

        video_url = body.get('url', '').strip()
        format_type = body.get('format', 'video')
        quality = body.get('quality', 'best')

        if not video_url:
            self._json(400, {"status": "error", "message": "URL tidak boleh kosong!"})
            return

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
                '1080': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
                '720': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
                '480': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best',
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

        downloaded_file = self._try_download(ydl_opts, video_url, format_type)

        if not downloaded_file:
            proxies = get_free_proxy()
            for proxy in proxies[:3]:
                try_opts = ydl_opts.copy()
                try_opts['proxy'] = f"http://{proxy}"
                try_opts['socket_timeout'] = 10
                downloaded_file = self._try_download(try_opts, video_url, format_type)
                if downloaded_file:
                    break

        if not downloaded_file:
            self._json(500, {"status": "error", "message": "Gagal mengunduh media dari URL tersebut."})
            return

        base_name = os.path.basename(downloaded_file)
        download_url = ""

        if supabase:
            try:
                with open(downloaded_file, 'rb') as f:
                    storage_path = f"downloads/{base_name}"
                    supabase.storage.from_(SUPABASE_BUCKET).upload(
                        file=f, path=storage_path,
                        file_options={"upsert": "true"}
                    )
                    download_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
                try:
                    supabase.table("downloads").insert({
                        "title": base_name, "url": video_url,
                        "download_url": download_url, "mode": mode_str
                    }).execute()
                except Exception:
                    pass
            except Exception:
                pass

        try:
            os.remove(downloaded_file)
        except Exception:
            pass

        self._json(200, {
            "status": "success",
            "message": f"{mode_str} berhasil diproses!",
            "filename": base_name,
            "download_url": download_url
        })

    def _try_download(self, opts, url, format_type):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if format_type == 'audio':
                    filename = os.path.splitext(filename)[0] + '.mp3'
                if os.path.exists(filename):
                    return filename
        except Exception:
            pass
        return None

    def _json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
