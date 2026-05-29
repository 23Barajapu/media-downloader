# Gunakan image Python resmi yang ringan
FROM python:3.10-slim

# Install ffmpeg dan dependensi sistem lainnya
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Buat user non-root (Wajib untuk Hugging Face Docker Spaces)
RUN useradd -m -u 1000 user
USER user

# Set environment variable untuk user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements dan install
COPY --chown=user requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy seluruh source code
COPY --chown=user . .

# Buat folder penyimpanan media
RUN mkdir -p Unduhan_Media

# Expose port 7860
EXPOSE 7860

# Jalankan aplikasi menggunakan gunicorn
CMD ["python", "app.py"]
