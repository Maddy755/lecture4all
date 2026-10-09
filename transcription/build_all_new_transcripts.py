import os
import json
import re

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def clean_vtt_to_chunks(vtt_path, chunk_duration=25.0):
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\s*\n', content)
    unique_lines = []
    prev_line = ''
    for b in blocks:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        if not lines: continue
        time_match = None
        for l in lines:
            m = re.match(r'(\d+:\d+:\d+\.\d+|\d+:\d+\.\d+)\s*-->\s*(\d+:\d+:\d+\.\d+|\d+:\d+\.\d+)', l)
            if m: time_match = m
            elif time_match:
                cleaned = re.sub(r'<[^>]+>', '', l).strip()
                if cleaned and cleaned != prev_line:
                    def to_secs(s):
                        parts = s.split(':')
                        if len(parts) == 3: return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
                        return float(parts[0])*60 + float(parts[1])
                    start = to_secs(time_match.group(1))
                    end = to_secs(time_match.group(2))
                    if end - start >= 0.2:
                        unique_lines.append({'start': round(start, 2), 'end': round(end, 2), 'text': cleaned})
                        prev_line = cleaned

    chunks = []
    if not unique_lines: return chunks
    
    current_chunk = {'start': unique_lines[0]['start'], 'end': unique_lines[0]['end'], 'text_parts': [unique_lines[0]['text']]}
    for item in unique_lines[1:]:
        if item['end'] - current_chunk['start'] < chunk_duration:
            current_chunk['end'] = item['end']
            if item['text'] not in current_chunk['text_parts'][-1]:
                current_chunk['text_parts'].append(item['text'])
        else:
            chunks.append({
                'start': current_chunk['start'],
                'end': current_chunk['end'],
                'text': ' '.join(current_chunk['text_parts'])
            })
            current_chunk = {'start': item['start'], 'end': item['end'], 'text_parts': [item['text']]}
    if current_chunk['text_parts']:
        chunks.append({
            'start': current_chunk['start'],
            'end': current_chunk['end'],
            'text': ' '.join(current_chunk['text_parts'])
        })
    return chunks

def write_srt(chunks, srt_path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, chunk in enumerate(chunks, 1):
            start_str = format_time(chunk["start"])
            end_str = format_time(chunk["end"])
            text = chunk["text"].strip()
            f.write(f"{idx}\n{start_str} --> {end_str}\n{text}\n\n")

VIDEOS = [
    {
        "id": "5LeZflr8Zfs",
        "lang": "en",
        "vtt": "transcription/subtitles/5LeZflr8Zfs.en.vtt",
    },
    {
        "id": "FM2sijgNIH0",
        "lang": "de",
        "vtt": "transcription/subtitles/FM2sijgNIH0.de.vtt",
    },
    {
        "id": "3gu4rbOy2GM",
        "lang": "hi",
        "vtt": "transcription/subtitles/3gu4rbOy2GM.hi.vtt",
    },
    {
        "id": "WLbAukFY2sg",
        "lang": "ml",
        "vtt": "transcription/subtitles/WLbAukFY2sg.ml.vtt",
    }
]

for item in VIDEOS:
    vid = item["id"]
    lang = item["lang"]
    vtt = item["vtt"]
    if not os.path.exists(vtt):
        print(f"VTT not found: {vtt}")
        continue
    
    meta_path = f"transcription/metadata/{vid}_metadata.json"
    with open(meta_path, "r", encoding="utf-8") as mf:
        meta = json.load(mf)[0]
        
    chunks = clean_vtt_to_chunks(vtt)
    print(f"Generated {len(chunks)} chunks for {vid} ({lang})")
    
    # 1. Write SRT
    srt_path = f"transcription/subtitles/{vid}_subtitles.srt"
    write_srt(chunks, srt_path)
    if lang == "de":
        # German also uses _subtitles_de.srt
        write_srt(chunks, f"transcription/subtitles/{vid}_subtitles_de.srt")
        
    # 2. Write processed transcript
    proc_obj = {
        "id": vid,
        "title": meta["title"],
        "speaker": meta["speaker"],
        "category": meta["category"],
        "date": meta["date"],
        "url": meta["url"],
        "m3u8": meta["m3u8"],
        "thumbnail": meta["thumbnail"],
        "language": lang,
        "chunks": chunks
    }
    proc_path = f"transcription/processed_transcripts/{vid}_transcript.json"
    with open(proc_path, "w", encoding="utf-8") as pf:
        json.dump(proc_obj, pf, indent=4, ensure_ascii=False)
        
    # 3. Write raw transcript JSON
    raw_path = f"transcription/transcriptions/{vid}_transcript.json"
    raw_obj = {
        "text": " ".join(c["text"] for c in chunks),
        "segments": [{"start": c["start"], "end": c["end"], "text": c["text"]} for c in chunks],
        "language": lang
    }
    with open(raw_path, "w", encoding="utf-8") as rf:
        json.dump(raw_obj, rf, indent=4, ensure_ascii=False)

# Process dWWgfonwNoU from Whisper transcript
vid_ta = "dWWgfonwNoU"
ta_raw_path = f"transcription/transcriptions/{vid_ta}_transcript.json"
if os.path.exists(ta_raw_path):
    with open(ta_raw_path, "r", encoding="utf-8") as rf:
        ta_data = json.load(rf)
    segs = ta_data.get("segments", [])
    if segs:
        ta_chunks = []
        curr = {"start": segs[0]["start"], "end": segs[0]["end"], "text_parts": [segs[0]["text"].strip()]}
        for s in segs[1:]:
            txt = s["text"].strip()
            if not txt:
                continue
            if s["end"] - curr["start"] < 30.0:
                curr["end"] = s["end"]
                curr["text_parts"].append(txt)
            else:
                ta_chunks.append({
                    "start": round(curr["start"], 2),
                    "end": round(curr["end"], 2),
                    "text": " ".join(curr["text_parts"])
                })
                curr = {"start": s["start"], "end": s["end"], "text_parts": [txt]}
        if curr["text_parts"]:
            ta_chunks.append({
                "start": round(curr["start"], 2),
                "end": round(curr["end"], 2),
                "text": " ".join(curr["text_parts"])
            })
        print(f"Generated {len(ta_chunks)} chunks for {vid_ta} (ta)")
        
        # 1. Write SRT
        srt_path = f"transcription/subtitles/{vid_ta}_subtitles.srt"
        write_srt(ta_chunks, srt_path)
        
        # 2. Write processed transcript
        meta_path = f"transcription/metadata/{vid_ta}_metadata.json"
        with open(meta_path, "r", encoding="utf-8") as mf:
            meta = json.load(mf)[0]
        
        proc_obj = {
            "id": vid_ta,
            "title": meta["title"],
            "speaker": meta["speaker"],
            "category": meta["category"],
            "date": meta["date"],
            "url": meta["url"],
            "m3u8": meta["m3u8"],
            "thumbnail": meta["thumbnail"],
            "language": "ta",
            "chunks": ta_chunks
        }
        proc_path = f"transcription/processed_transcripts/{vid_ta}_transcript.json"
        with open(proc_path, "w", encoding="utf-8") as pf:
            json.dump(proc_obj, pf, indent=4, ensure_ascii=False)

print("Batch processing completed successfully!")
