import os
import sys
import socket
from flask import Flask, request, jsonify, render_template_string
import instaloader
import requests

app = Flask(__name__)

# HTML template for the form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Reel Downloader</title>
</head>
<body>
    <h1>Instagram Reel Downloader</h1>
    <form action="/download" method="post">
        <label for="url">Enter Instagram Reel URL:</label><br><br>
        <input type="text" id="url" name="url" placeholder="https://www.instagram.com/reel/..." required style="width: 300px;"><br><br>
        <button type="submit">Download</button>
    </form>
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

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    if not url:
        return jsonify({"status": "error", "message": "Invalid input. Provide a URL."}), 400

    result = download_reel(url)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
