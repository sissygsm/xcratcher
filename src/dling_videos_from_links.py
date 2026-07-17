#########################################################
# Configure FIREFOX_PROFILE_CODE & X_USERNAME in .env
# (copy .env.example to .env and fill in your values)
#########################################################

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

import os
import time

import config

# Create downloads directory if it doesn't exist
DOWNLOADS_DIR = "./downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)


def download_pending_links(username, file="pending_links.txt"):
    user_dir = os.path.join(DOWNLOADS_DIR, username)
    file_path = os.path.join(user_dir, file)

    links = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            links = [line.strip() for line in f]

    # Get the url id number to name the mp4 file
    output_path = os.path.join(user_dir, f'%(original_url.-19:)s.%(ext)s')
    ydl_opts = {
        'cookiesfrombrowser': ('firefox', config.FIREFOX_PROFILE),
        'outtmpl': output_path,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'noplaylist': True
    }
    i = 0
    while True:
        l = links.pop()
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([l])
        except DownloadError as e:
            links.append(l)
            i = 49
        i += 1
        if links == []:
            break
        if i % 50 == 0:  # X/Twitter Rate-limit links to download
            print(f"Rate-limit exceeded -> Wait 10 min or end script")
            with open(file_path, "w") as f:
                f.write("\n".join(links) + "\n")
            time.sleep(600)  # 10min = 600seg
    
    print(f"All videos was downloaded.")
    if os.path.exists(file_path):
        os.remove(file_path)


download_pending_links(username=config.X_USERNAME)
