import os
import sys
import socket
from flask import Flask, request, jsonify, render_template_string, send_file
import instaloader
import requests

app = Flask(__name__)

# Updated HTML template with enhanced Bootstrap design
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Reel Downloader</title>
    <!-- Bootstrap CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background-color: #007bff;
            border-color: #007bff;
        }
        .btn-primary:hover {
            background-color: #0056b3;
        }
        footer {
            position: absolute;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 10px 0;
            background-color: #343a40;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4">
            <h1 class="text-center mb-4">Instagram Reel Downloader</h1>
            <form action="/download" method="post">
                <div class="form-group">
                    <label for="url">Enter Instagram Reel URL:</label>
                    <input type="text" id="url" name="url" class="form-control" placeholder="https://www.instagram.com/reel/..." required>
                </div>
                <button type="submit" class="btn btn-primary btn-block">Download</button>
            </form>
        </div>
    </div>
    <footer>
        <p>&copy; 2024 Instagram Reel Downloader | Made with ❤️ by Tushar</p>
    </footer>

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

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    if not url:
        return jsonify({"status": "error", "message": "Invalid input. Provide a URL."}), 400

    result = download_reel(url)
    if result["status"] == "success":
        filepath = result["file"]
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
