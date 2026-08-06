import os
import urllib.request
import yt_dlp
import streamlit as st

st.set_page_config(page_title="Universal Media Downloader", page_icon="🎬", layout="centered")

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

st.title("🎬 Universal Media Downloader")
st.caption("Unduh video & audio dari YouTube, TikTok, Facebook, Instagram, Bilibili, dll.")

video_url = st.text_input("URL Media", placeholder="https://www.youtube.com/watch?v=...")
format_type = st.radio("Format Output", ["Video (MP4)", "Audio (MP3)"], horizontal=True)

if format_type == "Audio (MP3)":
    quality = st.selectbox("Kualitas Audio", ["320kbps", "192kbps", "128kbps", "96kbps"], index=1)
else:
    quality = st.selectbox("Kualitas Video", ["Terbaik", "1080p", "720p", "480p", "360p"], index=0)

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
