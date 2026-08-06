import os
import urllib.request
import yt_dlp
import streamlit as st

st.set_page_config(page_title="Universal Media Hunter", page_icon="🦖", layout="centered")

# Inject Custom CSS - High Contrast, Clear Typography, Comfortable UX
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c1b 0%, #1a162b 50%, #110a1f 100%) !important;
    color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* Glassmorphic main container */
.main .block-container {
    background: rgba(30, 24, 50, 0.6) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 20px !important;
    padding: 2.5rem 2rem !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), 0 0 20px rgba(139, 92, 246, 0.2) !important;
    margin-top: 1.5rem !important;
    max-width: 680px !important;
}

/* High Contrast Labels */
label, [data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.3px !important;
}

/* Header styling */
h1 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    text-align: center !important;
    font-size: 2.3rem !important;
    margin-bottom: 0.3rem !important;
}

.stCaption {
    text-align: center !important;
    color: #d1d5db !important;
    font-size: 0.95rem !important;
    margin-bottom: 1.5rem !important;
}

/* Text Input Styling */
input[type="text"] {
    background: #ffffff !important;
    color: #111827 !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    border-radius: 10px !important;
    border: 2px solid #8b5cf6 !important;
    padding: 0.6rem 1rem !important;
}

/* Selectbox Dropdown Styling */
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #111827 !important;
    border-radius: 10px !important;
    border: 2px solid #8b5cf6 !important;
    font-weight: 600 !important;
}
div[data-baseweb="select"] span {
    color: #111827 !important;
    font-weight: 600 !important;
}

/* Radio Group Box */
div[role="radiogroup"] {
    background: rgba(255, 255, 255, 0.08) !important;
    padding: 10px 14px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    display: flex !important;
    gap: 20px !important;
}

div[role="radiogroup"] label {
    background: transparent !important;
}

div[role="radiogroup"] label p {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}

/* Primary Button Styling */
div.stButton > button {
    background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(217, 70, 239, 0.7) !important;
}

/* Download Button Styling */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5) !important;
}

/* Status Alert boxes */
.stAlert {
    border-radius: 10px !important;
    font-weight: 500 !important;
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
st.caption("Unduh video & audio dari YouTube, TikTok, Facebook, Instagram, Bilibili, dll.")

video_url = st.text_input("🔗 Paste URL Video / Media", placeholder="https://www.youtube.com/watch?v=...")
format_type = st.radio("⚡ Format Output", ["Video (MP4)", "Audio (MP3)"], horizontal=True)

if format_type == "Audio (MP3)":
    quality = st.selectbox("🎵 Kualitas Audio", ["320kbps", "192kbps", "128kbps", "96kbps"], index=1)
else:
    quality = st.selectbox("🎬 Kualitas Video", ["Terbaik", "1080p", "720p", "480p", "360p"], index=0)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

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
                'extractor_args': {'youtube': {'player_client': ['mweb', 'web', 'tvhtml5']}},
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
            fmt = q_map.get(quality, 'bestvideo+bestaudio/best')
            ydl_opts = {
                'format': fmt,
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                'nocheckcertificate': True,
                'socket_timeout': 30,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'extractor_args': {'youtube': {'player_client': ['mweb', 'web', 'tvhtml5']}},
                'geo_bypass': True,
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
