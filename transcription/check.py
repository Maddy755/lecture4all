import re, sys, requests
vid = sys.argv[1]
r = requests.get(f"https://lecture2go.uni-hamburg.de/l2go/-/get/v/{vid}")
print("HTTP status:", r.status_code, "| page length:", len(r.text))
print("has initVideoPlayer:", "initVideoPlayer" in r.text)
print("m3u8 links:", re.findall(r'https?://[^"\s\\]+\.m3u8', r.text)[:3])
print("mp4 links:", re.findall(r'https?://[^"\s\\]+\.mp4', r.text)[:3])