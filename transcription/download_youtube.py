import os
import json
import yt_dlp
from datetime import datetime

VIDEOS = [
    {
        "id": "5VGrSzQIfhI",
        "url": "https://www.youtube.com/watch?v=5VGrSzQIfhI",
        "language": "ml",
        "category": "Malayalam - Mathematics & Education"
    },
    {
        "id": "baW4xb7gDcU",
        "url": "https://www.youtube.com/watch?v=baW4xb7gDcU",
        "language": "ml",
        "category": "Malayalam - History & Culture"
    },
    {
        "id": "NHiqHWesFpg",
        "url": "https://www.youtube.com/watch?v=NHiqHWesFpg",
        "language": "hi",
        "category": "Hindi - Mathematics & Algebra"
    },
    {
        "id": "8ZBLx6c2cxw",
        "url": "https://www.youtube.com/watch?v=8ZBLx6c2cxw",
        "language": "hi",
        "category": "Hindi - General Knowledge & History"
    },
    {
        "id": "Og9ZKAf8ecg",
        "url": "https://www.youtube.com/watch?v=Og9ZKAf8ecg",
        "language": "ta",
        "category": "Tamil - Psychology & Self Improvement"
    },
    {
        "id": "ufRLns-QQh0",
        "url": "https://www.youtube.com/watch?v=ufRLns-QQh0",
        "language": "ta",
        "category": "Tamil - Computer Science & Programming"
    }
]

os.makedirs("videos", exist_ok=True)
os.makedirs("metadata", exist_ok=True)

ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': './videos/%(id)s.%(ext)s',
    'quiet': False,
    'no_warnings': True
}

for item in VIDEOS:
    vid = item["id"]
    url = item["url"]
    cat = item["category"]
    video_path = f"./videos/{vid}.mp4"
    meta_path = f"./metadata/{vid}_metadata.json"

    print("=" * 60)
    print(f"Processing: {vid} ({cat})")
    print("=" * 60)

    # 1. Fetch info with yt_dlp
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", vid)
            uploader = info.get("uploader") or info.get("channel") or "Unknown"
            upload_date = info.get("upload_date")
            if upload_date and len(upload_date) == 8:
                formatted_date = f"{upload_date[6:8]}.{upload_date[4:6]}.{upload_date[0:4]}"
            else:
                formatted_date = datetime.now().strftime("%d.%m.%Y")
            
            thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

            # Save metadata
            meta_data = [{
                "id": vid,
                "url": url,
                "thumbnail": thumb,
                "m3u8": f"/videos/{vid}.mp4",
                "title": title,
                "date": formatted_date,
                "speaker": uploader,
                "category": cat
            }]
            with open(meta_path, "w", encoding="utf-8") as mf:
                json.dump(meta_data, mf, indent=4, ensure_ascii=False)
            print(f"Saved metadata to {meta_path}: {title} by {uploader}")

    except Exception as e:
        print(f"Error fetching metadata for {vid}: {e}")

    # 2. Download video if not already present
    if os.path.exists(video_path):
        print(f"Video {video_path} already exists. Skipping download.")
    else:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"Downloaded video to {video_path}")
        except Exception as e:
            print(f"Error downloading video {vid}: {e}")

print("All downloads and metadata extraction complete!")
