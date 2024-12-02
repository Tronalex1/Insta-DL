import os
import sys
import socket
from flask import Flask, request, jsonify
import instaloader
import requests

app = Flask(__name__)

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
def hello_world():
    version = sys.version_info
    res = (
        "<h1>Instagram Reel Downloader</h1>"
        f"<h2>{os.getenv('ENV', 'Development Environment')}</h2></br>"
        f"Running Python: {version.major}.{version.minor}.{version.micro}<br>"
        f"Hostname: {socket.gethostname()}"
    )
    return res

@app.route("/download", methods=["POST"])
def download():
    data = request.json
    if not data or "url" not in data:
        return jsonify({"status": "error", "message": "Invalid input. Provide a URL."}), 400

    url = data["url"]
    result = download_reel(url)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
