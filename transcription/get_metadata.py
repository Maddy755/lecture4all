import os
import requests
import json
from bs4 import BeautifulSoup
import re
import sys

url = "https://lecture2go.uni-hamburg.de/l2go/-/get/v/"
img = "https://lecture2go.uni-hamburg.de/images/"
video_directory = "./videos"
videos = []

def get_m3u8_link(video_url):
    resp = requests.get(video_url)
    if resp.status_code != 200:
        print(f"Failed to fetch {video_url}")
        return None
    start = resp.text.find("initVideoPlayer")
    match = re.search(r'(https?://[^"\s\\]+\.m3u8)', resp.text[start:] if start != -1 else resp.text)
    if match:
        return match.group(1)
    print(f"Fehler beim Abrufen des m3u8-Links: No m3u8 found in {video_url}")
    return None

def get_thumbnail_link(video_url):
    resp = requests.get(video_url)
    if resp.status_code != 200:
        print(f"Failed to fetch {video_url}")
        return None
    match = re.search(r'initVideoPlayer\(.*?,\s*"(https?://[^"]+\.jpg)\?lastmodified', resp.text, re.DOTALL)
    if match:
        return match.group(1)
    print(f"Fehler beim Abrufen des Thumbnail-Links: No thumbnail found in {video_url}")
    return None

if __name__ == "__main__":
    os.makedirs("metadata", exist_ok=True)
    start_index = int(sys.argv[1])
    end_index = int(sys.argv[2])
    
    for i in range(start_index, end_index + 1):
        metadata = []
        if not (os.path.exists(f"{video_directory}/{i}.mp4") or os.path.exists(f"{video_directory}/{i}.mp3")):
            print(f"Video {i} does not exist. Skipping...")
            continue
        print(f"Processing video {i}")
        video_id = str(i)
        video_url = url + video_id
        response = requests.get(video_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('h2', class_='video-title').text.strip() if soup.find('h2', class_='video-title') else 'Keine Angabe'
            speaker = soup.find('div', class_='allcreators').text.strip() if soup.find('div', class_='allcreators') else 'Keine Angaben'
            video_labels = soup.find_all('div', class_='video-label')
            date = video_labels[0].text.strip() if len(video_labels) > 0 else 'Keine Angaben'
            category = video_labels[1].text.strip() if len(video_labels) > 1 else 'Keine Angaben'
            video_thumbnail = get_thumbnail_link(video_url)
            if video_thumbnail is None:
                video_thumbnail = "https://lecture2go.uni-hamburg.de/o/de.uhh.l2g.themes.uhhci//images/audio_only_big.png"
            m3u8_link = get_m3u8_link(video_url)
            video_data = {
                "id": video_id,
                "url": video_url,
                "thumbnail": video_thumbnail,
                "m3u8": m3u8_link,
                "title": title,
                "date": date,
                "speaker": speaker,
                "category": category
            }
            metadata.append(video_data)
        else:
            print(f"Failed to retrieve metadata for video ID: {video_id}")
            
        metadata_path = os.path.join("metadata", f"{i}_metadata.json")

        with open(metadata_path, "w") as json_file:
            json.dump(metadata, json_file, indent=4, ensure_ascii=False)
        print(f"Metadata saved to {i}_metadata.json")
