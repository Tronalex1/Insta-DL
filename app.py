import os
import sys
import socket
from flask import Flask, request, jsonify, render_template_string, send_file
import instaloader
import requests

app = Flask(__name__)

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
            font-family: Arial, sans-serif;
        }
        .container {
            max-width: 600px;
            margin-top: 50px;
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #007bff;
        }
        .btn-block {
            font-size: 16px;
            padding: 12px;
        }
        .alert {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center">Instagram Reel Downloader</h1>
        <form id="downloadForm" action="/download" method="post">
            <div class="form-group">
                <label for="url">Enter Instagram Reel URL:</label>
                <input type="text" id="url" name="url" class="form-control" placeholder="https://www.instagram.com/reel/..." required>
            </div>
            <button type="submit" class="btn btn-primary btn-block">Download</button>
        </form>

        <div id="responseMessage"></div>
    </div>

    <!-- Bootstrap JS, Popper.js, and jQuery -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>

    <script>
        // Handle form submission
        document.getElementById("downloadForm").onsubmit = function(event) {
            event.preventDefault();
            const url = document.getElementById("url").value;

            // Clear previous message
            document.getElementById("responseMessage").innerHTML = "";

            // Validate URL
            if (!url) {
                alert("Please enter a valid Instagram URL.");
                return;
            }

            // Submit the URL via POST request
            fetch("/download", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({ url: url })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    // Clear the input box and show success message
                    document.getElementById("url").value = "";
                    document.getElementById("responseMessage").innerHTML = 
                        `<div class="alert alert-success" role="alert">
                            ${data.message} <br> <strong>File:</strong> ${data.file}
                        </div>`;
                } else {
                    // Show error message
                    document.getElementById("responseMessage").innerHTML = 
                        `<div class="alert alert-danger" role="alert">${data.message}</div>`;
                }
            })
            .catch(error => {
                document.getElementById("responseMessage").innerHTML = 
                    `<div class="alert alert-danger" role="alert">An error occurred. Please try again later.</div>`;
            });
        };
    </script>
</body>
</html>
"""
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
