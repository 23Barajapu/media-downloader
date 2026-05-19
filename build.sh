#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create directory for static binaries
mkdir -p opt/bin

# Download static FFmpeg for Linux x86_64
echo "Downloading static FFmpeg..."
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz

echo "Extracting FFmpeg..."
tar -xf ffmpeg.tar.xz

# Find the extracted directory name and move binaries
FFMPEG_DIR=$(find . -maxdepth 1 -type d -name "ffmpeg-*" | head -n 1)
mv "$FFMPEG_DIR/ffmpeg" opt/bin/
mv "$FFMPEG_DIR/ffprobe" opt/bin/

# Clean up temporary files
rm -rf ffmpeg.tar.xz "$FFMPEG_DIR"

echo "FFmpeg successfully installed in opt/bin/"
chmod +x opt/bin/ffmpeg opt/bin/ffprobe
