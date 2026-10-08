import os
import sys
import re
import requests
import yt_dlp

"""
Author: w4a-backend
Description: Script to download videos from lecture2go links.
"""

def extract_m3u8_from_script(html):
    start = html.find("initVideoPlayer")
    match = re.search(r'(https?://[^"\s\\]+\.m3u8)', html[start:] if start != -1 else html)
    if match:
        return match.group(1)
    return None

def download_video(video_url):
    id = video_url.split("v/")[1]
    output_dir = "videos"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, id + ".mp4")

    if os.path.exists(filename):
        print(f"File {filename} already exists. Skipping download.")
        return

    # Scrape the video page for the m3u8 link
    resp = requests.get(video_url)
    m3u8_url = extract_m3u8_from_script(resp.text)
    if not m3u8_url:
        print(f"Could not find m3u8 link for {video_url}")
        return Exception("No m3u8 found")

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'./videos/{id}.%(ext)s',
        'noplaylist': True,
        'verbose': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([m3u8_url])
    except Exception as e:
        return e

def main():
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    count = 0
    err = 0
    for i in range(start, end + 1):
        link = f"https://lecture2go.uni-hamburg.de/l2go/-/get/v/{i}"
        e = download_video(link)
        if e:
            err += 1
        else:
            count += 1

    print(f"All done! Downloaded {count} videos. {err} Videos had an invalid ID and have not been downloaded.")

if __name__ == "__main__":
    main()
