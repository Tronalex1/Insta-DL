import os
import sys
import socket
from flask import Flask, request, jsonify, render_template_string, send_file
import instaloader
import requests
import yt_dlp as ytdl  # Import yt-dlp for YouTube video downloads

app = Flask(__name__)

# HTML template with Bootstrap for styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Downloader</title>
    <!-- Bootstrap CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">Video Downloader</h1>
        
        <!-- Instagram Reel Downloader -->
        <h3 class="text-center">Instagram Reel Downloader</h3>
        <form action="/download_reel" method="post">
            <div class="form-group">
                <label for="url">Enter Instagram Reel URL:</label>
                <input type="text" id="url" name="url" class="form-control" placeholder="https://www.instagram.com/reel/..." required>
            </div>
            <button type="submit" class="btn btn-primary btn-block">Download Instagram Reel</button>
        </form>

        <hr>

        <!-- YouTube Video Downloader -->
        <h3 class="text-center">YouTube Video Downloader</h3>
        <form action="/download_ytdl" method="post">
            <div class="form-group">
                <label for="ytdl_url">Enter YouTube Video URL:</label>
                <input type="text" id="ytdl_url" name="ytdl_url" class="form-control" placeholder="https://www.youtube.com/watch?v=..." required>
            </div>
            <button type="submit" class="btn btn-success btn-block">Download YouTube Video</button>
        </form>
    </div>

    <!-- Bootstrap JS, Popper.js, and jQuery -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""

# Function to download the Instagram Reel
def download_reel(url):
    L = instaloader.Instaloader()
    shortcode = url.split('/')[-2]

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        if post.is_video:
            video_url = post.video_url

            # Download the video
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                filename = f"{shortcode}.mp4"
                with open(filename, 'wb') as video_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        video_file.write(chunk)
                return {"status": "success", "message": "Video downloaded successfully!", "file": filename}
            else:
                return {"status": "error", "message": f"Failed to download video. HTTP status code: {response.status_code}"}
        else:
            return {"status": "error", "message": "The post is not a video."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Function to download YouTube video using yt-dlp
def download_ytdl(url):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Download best quality video & audio
            'outtmpl': '%(id)s.%(ext)s',  # Save with video ID as filename
        }

        with ytdl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_file = f"{info_dict['id']}.mp4"
            return {"status": "success", "message": "YouTube video downloaded successfully!", "file": video_file}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/download_reel", methods=["POST"])
def download_reel_route():
    url = request.form.get("url")
    if not url:
        return jsonify({"status": "error", "message": "Invalid input. Provide a URL."}), 400

    result = download_reel(url)
    if result["status"] == "success":
        filepath = result["file"]
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify(result)

@app.route("/download_ytdl", methods=["POST"])
def download_ytdl_route():
    url = request.form.get("ytdl_url")
    if not url:
        return jsonify({"status": "error", "message": "Invalid input. Provide a URL."}), 400

    result = download_ytdl(url)
    if result["status"] == "success":
        filepath = result["file"]
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
