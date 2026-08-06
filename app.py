import os
import urllib.request
import yt_dlp
import streamlit as st

st.set_page_config(page_title="Universal Media Hunter", page_icon="🦖", layout="centered")

# Inject Custom CSS (Glassmorphism, Dark Mode, Google Fonts, Glow Effects)
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Outfit:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0b0813 0%, #171128 50%, #0d0614 100%) !important;
    color: #f3f4f6 !important;
    font-family: 'Outfit', sans-serif !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* Glassmorphic card styling */
.main .block-container {
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(25px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 24px !important;
    padding: 2.5rem !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 30px rgba(139, 92, 246, 0.15) !important;
    margin-top: 2rem !important;
}

h1 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #d946ef 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center !important;
    font-size: 2.5rem !important;
}

.stCaption {
    text-align: center !important;
    color: #9ca3af !important;
    font-size: 1rem !important;
}

/* Custom Input Styling */
input[type="text"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-size: 1.05rem !important;
}
input[type="text"]:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 15px rgba(139, 92, 246, 0.4) !important;
}

/* Primary Button Styling */
div.stButton > button {
    background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border-radius: 14px !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4) !important;
    transition: all 0.3s ease !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 30px rgba(217, 70, 239, 0.6) !important;
}

/* Download Button Styling */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border-radius: 14px !important;
    border: none !important;
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
}

/* Selectbox & Radio */
div[role="radiogroup"] {
    background: rgba(255, 255, 255, 0.04) !important;
    padding: 8px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Tulis cookies.txt dinamis jika ada env COOKIES_CONTENT
cookies_content = os.environ.get("COOKIES_CONTENT", "")
if cookies_content.strip():
    try:
        with open("cookies.txt", "w", encoding="utf-8") as f:
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

def get_latest_downloaded_file(folder):
    if not os.path.exists(folder):
        return None
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

st.markdown("<h1>🦖 Universal Media Hunter</h1>", unsafe_allow_html=True)
st.caption("Unduh video & audio dari YouTube, TikTok, Facebook, Instagram, Bilibili, dan 1000+ situs lainnya")

st.markdown("<br>", unsafe_allow_html=True)

video_url = st.text_input("🔗 Paste URL Video / Media", placeholder="https://www.youtube.com/watch?v=...")
format_type = st.radio("⚡ Format Output", ["Video (MP4)", "Audio (MP3)"], horizontal=True)

if format_type == "Audio (MP3)":
    quality = st.selectbox("🎵 Kualitas Audio", ["320kbps", "192kbps", "128kbps", "96kbps"], index=1)
else:
    quality = st.selectbox("🎬 Kualitas Video", ["Terbaik", "1080p", "720p", "480p", "360p"], index=0)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 Download Sekarang", type="primary", use_container_width=True):
    if not video_url or not video_url.strip():
        st.error("❌ URL tidak boleh kosong!")
    else:
        output_folder = "Unduhan_Media"
        os.makedirs(output_folder, exist_ok=True)

        status = st.empty()
        status.info("⏳ Menyiapkan unduhan...")

        if format_type == "Audio (MP3)":
            pref_q = quality.replace("kbps", "").strip()
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

        download_success = False
        try:
            status.info(f"⬇️ Mendownload {mode_str}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            download_success = True
        except Exception as e:
            err_msg = str(e)
            status.warning("⚠️ Mencoba bypass proxy...")
            proxies = get_free_indonesian_proxy()
            if proxies:
                for attempt_proxy in proxies[:3]:
                    try:
                        try_opts = ydl_opts.copy()
                        try_opts['proxy'] = f"http://{attempt_proxy}"
                        try_opts['socket_timeout'] = 10
                        with yt_dlp.YoutubeDL(try_opts) as ydl:
                            ydl.download([video_url])
                        download_success = True
                        break
                    except Exception:
                        continue
            if not download_success:
                status.error(f"❌ Gagal: {err_msg}")

        if download_success:
            file_path = get_latest_downloaded_file(output_folder)
            if file_path and os.path.exists(file_path):
                filename = os.path.basename(file_path)
                status.success(f"✅ Sukses! {mode_str} berhasil diunduh.")
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"💾 Simpan File: {filename}",
                        data=f.read(),
                        file_name=filename,
                        mime="application/octet-stream",
                        use_container_width=True
                    )
