import os
import urllib.request
import yt_dlp
import gradio as gr

# Tulis cookies.txt dinamis jika ada env COOKIES_CONTENT
cookies_content = os.environ.get("COOKIES_CONTENT", "")
if cookies_content.strip():
    try:
        with open("cookies.txt", "w", encoding="utf-8") as f:
            f.write(cookies_content)
        print("[Cookies] cookies.txt dibuat.")
    except Exception as e:
        print(f"[Cookies] Gagal: {e}")

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

def get_latest_downloaded_file(folder):
    if not os.path.exists(folder):
        return None
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        return None
try:
    import spaces
    gpu_decorator = spaces.GPU
except Exception:
    gpu_decorator = lambda func: func

@gpu_decorator
def download_media(video_url, format_type, quality, progress=gr.Progress()):
    if not video_url or not video_url.strip():
        return None, "❌ URL tidak boleh kosong!"

    output_folder = "Unduhan_Media"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    progress(0.1, desc="Menyiapkan unduhan...")

    if format_type == "Audio (MP3)":
        pref_q = quality.replace("kbps", "").strip() if "kbps" in quality else "192"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'nocheckcertificate': True,
            'socket_timeout': 30,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
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
        fmt = q_map.get(quality, 'bestvideo+bestaudio/best')
        ydl_opts = {
            'format': fmt,
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'nocheckcertificate': True,
            'socket_timeout': 30,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
        }
        mode_str = f"Video ({quality})"

    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"

    progress(0.3, desc=f"Mendownload {mode_str}...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        file_path = get_latest_downloaded_file(output_folder)
        progress(1.0, desc="Selesai!")
        return file_path, f"✅ Sukses! {mode_str} berhasil diunduh."
    except Exception as e:
        err_msg = str(e)
        progress(0.5, desc="Mencoba Bypass Proxy...")
        proxies = get_free_indonesian_proxy()
        if proxies:
            for attempt_proxy in proxies[:3]:
                try:
                    try_opts = ydl_opts.copy()
                    try_opts['proxy'] = f"http://{attempt_proxy}"
                    try_opts['socket_timeout'] = 10
                    with yt_dlp.YoutubeDL(try_opts) as ydl:
                        ydl.download([video_url])
                    file_path = get_latest_downloaded_file(output_folder)
                    progress(1.0, desc="Selesai via Proxy!")
                    return file_path, f"✅ Sukses via Auto-Proxy! {mode_str}"
                except Exception:
                    continue
        return None, f"❌ Gagal mendownload: {err_msg}"

def update_qualities(format_type):
    if format_type == "Audio (MP3)":
        return gr.Dropdown(choices=["320kbps", "192kbps", "128kbps", "96kbps"], value="192kbps", label="Kualitas Audio")
    return gr.Dropdown(choices=["Terbaik", "1080p", "720p", "480p", "360p"], value="Terbaik", label="Kualitas Video")

with gr.Blocks(title="Media Downloader") as demo:
    gr.Markdown("# 🎬 Universal Media Downloader")
    gr.Markdown("Download video & audio dari YouTube, TikTok, Facebook, Instagram, Bilibili, dll.")

    with gr.Row():
        with gr.Column():
            url_input = gr.Textbox(label="URL Media", placeholder="https://www.youtube.com/watch?v=...")
            fmt_input = gr.Radio(choices=["Video (MP4)", "Audio (MP3)"], value="Video (MP4)", label="Format Output")
            quality_input = gr.Dropdown(choices=["Terbaik", "1080p", "720p", "480p", "360p"], value="Terbaik", label="Kualitas Video")
            btn_submit = gr.Button("🚀 Download Sekarang", variant="primary")

        with gr.Column():
            status_output = gr.Textbox(label="Status Unduhan", interactive=False)
            file_output = gr.File(label="Hasil Unduhan (Klik untuk Simpan)")

    fmt_input.change(fn=update_qualities, inputs=[fmt_input], outputs=[quality_input])
    btn_submit.click(
        fn=download_media,
        inputs=[url_input, fmt_input, quality_input],
        outputs=[file_output, status_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
