from flask import Flask, request, send_from_directory, url_for, render_template, redirect, send_file
from threading import Thread
import requests
import secrets
import time
import os


app = Flask(__name__)
UPLOAD_FOLDER = "files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LIVING_TIME_IN_SECONDS = 10 * 60	
TITLE = "temphost.online"
MAX_FILE_SIZE_MB = 25
VERSION = "0.0.3"

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "GET": 
        return render_template("index.html", title=TITLE, upload_limit=str(MAX_FILE_SIZE_MB), version=VERSION, living_time=str(LIVING_TIME_IN_SECONDS / 60))

    if request.method == "POST":
        file = request.files["file"]

        file.seek(0, os.SEEK_END)
        file_size = file.tell() / (1024 * 1024)
        file.seek(0)

        if file_size > MAX_FILE_SIZE_MB:
            return "File to large"
        
        unique_folder = secrets.token_hex(4)
        path = os.path.join(UPLOAD_FOLDER, unique_folder)

        os.makedirs(path, exist_ok=True)

        file.save(os.path.join(path, file.filename))
        Thread(target=delete_host, args=(f"files/{unique_folder}/{file.filename}",)).start()
        return url_for("download_file", folder=unique_folder, filename=file.filename, _external=True)

def delete_host(file, wait_before: int = LIVING_TIME_IN_SECONDS):
    time.sleep(wait_before)
    os.remove(file)
    os.rmdir(os.path.dirname(file))

@app.route("/download", methods=["POST", "GET"])
def download_from_html():
    if request.method == "GET":
        return "This route is just for posting"
    else:
        file_path = request.form.get("file-path")
        https = "https://temphost.online/"
        http = "http://temphost.online/"
        if https in file_path:
            file_path = file_path.replace(https, "")
        if http in file_path:
            file_path = file_path.replace(http, "")
        try:

            folder, filename = os.path.split(file_path)
            full_folder_path = os.path.join(UPLOAD_FOLDER, folder)
            full_path = os.path.join(full_folder_path, filename)

            return send_file(full_path, as_attachment=True)

        except:
            return "Invalid temphost.online Link"
            

@app.route("/<folder>/<filename>")
def download_file(folder, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder), filename)

@app.route("/<path:path>")
def catch_all(path):
    return redirect(url_for("index"))

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
