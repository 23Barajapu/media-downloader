# Gunakan image Python resmi yang ringan
FROM python:3.10-slim

# Install ffmpeg dan dependensi sistem lainnya
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code
COPY . .

# Buat folder penyimpanan media agar tidak eror
RUN mkdir -p Unduhan_Media

# Expose port 7860 (Hugging Face Spaces strict port, works perfectly on Render too)
EXPOSE 7860

# Jalankan aplikasi menggunakan gunicorn dengan setelan thread untuk SSE
CMD ["gunicorn", "--workers=1", "--threads=8", "--timeout=120", "--bind", "0.0.0.0:7860", "app:app"]
