import os
import json
import re
import whisper_timestamped

VIDEOS_INFO = [
    {
        "id": "Og9ZKAf8ecg",
        "lang": "ta",
        "path": "videos/Og9ZKAf8ecg.mp4"
    },
    {
        "id": "ufRLns-QQh0",
        "lang": "ta",
        "path": "videos/ufRLns-QQh0.mp4"
    },
    {
        "id": "NHiqHWesFpg",
        "lang": "hi",
        "path": "videos/NHiqHWesFpg.mp4"
    },
    {
        "id": "8ZBLx6c2cxw",
        "lang": "hi",
        "path": "videos/8ZBLx6c2cxw.mp4"
    },
    {
        "id": "baW4xb7gDcU",
        "lang": "ml",
        "path": "videos/baW4xb7gDcU.mp4"
    },
    {
        "id": "5VGrSzQIfhI",
        "lang": "ml",
        "path": "videos/5VGrSzQIfhI.mp4"
    }
]

def clean_repeated_chars(text):
    if not text:
        return ""
    # Collapse 4+ identical characters down to 1
    return re.sub(r'(.)\1{3,}', r'\1', text)

def remove_repetitive_ngrams_from_words(words, max_n=5, max_repeats=1):
    result = list(words)
    changed = True
    while changed:
        changed = False
        for n in range(max_n, 0, -1):
            i = 0
            new_result = []
            while i < len(result):
                ngram = [clean_repeated_chars(w.get('text', '').strip()) for w in result[i:i+n]]
                if len(ngram) < n or not any(ngram):
                    new_result.extend(result[i:])
                    break
                repeat_count = 1
                j = i + n
                while j + n <= len(result) and [clean_repeated_chars(w.get('text', '').strip()) for w in result[j:j+n]] == ngram:
                    repeat_count += 1
                    j += n
                if repeat_count > max_repeats:
                    for _ in range(max_repeats):
                        new_result.extend(result[i:i+n])
                    i = j
                    changed = True
                else:
                    new_result.extend(result[i:i+n])
                    i += n
            result = new_result
    return result

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def create_srt(segments):
    srt_str = ""
    idx = 1
    for seg in segments:
        text = seg.get('text', '').strip()
        if not text:
            continue
        start = format_time(seg.get('start', 0.0))
        end = format_time(seg.get('end', 0.0))
        srt_str += f"{idx}\n{start} --> {end}\n{text}\n\n"
        idx += 1
    return srt_str

print("Loading Whisper base model on CPU...")
model = whisper_timestamped.load_model("base", device="cpu")

for item in VIDEOS_INFO:
    vid = item["id"]
    lang = item["lang"]
    vpath = item["path"]
    
    print("=" * 60)
    print(f"Transcribing and cleaning: {vid} (language={lang})")
    print("=" * 60)
    
    try:
        raw_res = whisper_timestamped.transcribe(
            model,
            vpath,
            language=lang,
            condition_on_previous_text=False,
            compression_ratio_threshold=2.0
        )
    except Exception as e:
        print(f"Error transcribing {vid}: {e}")
        continue

    # Process and deduplicate segments and words
    cleaned_segments = []
    full_text_pieces = []
    
    for seg in raw_res.get("segments", []):
        words = seg.get("words", [])
        if words:
            cleaned_words = remove_repetitive_ngrams_from_words(words, max_n=5, max_repeats=1)
            # Filter empty or noisy single chars
            cleaned_words = [w for w in cleaned_words if clean_repeated_chars(w.get('text', '').strip())]
            seg["words"] = cleaned_words
            seg_text = " ".join(clean_repeated_chars(w.get('text', '').strip()) for w in cleaned_words)
        else:
            seg_text = clean_repeated_chars(seg.get("text", "").strip())
        
        seg["text"] = seg_text
        if seg_text:
            cleaned_segments.append(seg)
            full_text_pieces.append(seg_text)

    # Secondary segment deduplication: skip consecutive identical segment texts
    deduped_segments = []
    prev_text = ""
    for s in cleaned_segments:
        curr_text = s["text"].strip()
        if curr_text == prev_text:
            continue
        deduped_segments.append(s)
        prev_text = curr_text

    raw_res["segments"] = deduped_segments
    raw_res["text"] = " ".join(s["text"] for s in deduped_segments)
    raw_res["language"] = lang

    # 1. Save cleaned transcript
    trans_out = f"transcriptions/{vid}_transcript.json"
    with open(trans_out, "w", encoding="utf-8") as f:
        json.dump(raw_res, f, indent=4, ensure_ascii=False)
    print(f"Saved cleaned transcript to {trans_out}")

    # 2. Save cleaned SRT subtitle
    srt_out = f"subtitles/{vid}_subtitles.srt"
    srt_text = create_srt(deduped_segments)
    with open(srt_out, "w", encoding="utf-8") as f:
        f.write(srt_text)
    print(f"Saved cleaned subtitles to {srt_out}")

    # 3. Create cleaned processed chunks
    meta_path = f"metadata/{vid}_metadata.json"
    title = vid
    speaker = "Unknown"
    category = "General"
    date = "Unknown"
    url = f"https://www.youtube.com/watch?v={vid}"
    m3u8 = f"/videos/{vid}.mp4"
    thumbnail = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as mf:
            m_data = json.load(mf)[0]
            title = m_data.get("title", title)
            speaker = m_data.get("speaker", speaker)
            category = m_data.get("category", category)
            date = m_data.get("date", date)
            url = m_data.get("url", url)
            m3u8 = m_data.get("m3u8", m3u8)
            thumbnail = m_data.get("thumbnail", thumbnail)

    chunks = []
    current_chunk_words = []
    chunk_start = None
    chunk_len = 12.0

    for seg in deduped_segments:
        for w in seg.get("words", []):
            wt = w.get("text", "").strip()
            ws = w.get("start")
            we = w.get("end")
            if not wt or ws is None or we is None:
                continue
            if chunk_start is None:
                chunk_start = ws
            current_chunk_words.append(wt)
            if (we - chunk_start) >= chunk_len:
                chunk_text = " ".join(current_chunk_words).strip()
                if chunk_text:
                    chunks.append({
                        "text": chunk_text,
                        "start": round(chunk_start, 2),
                        "end": round(we, 2)
                    })
                current_chunk_words = []
                chunk_start = None

    if current_chunk_words and chunk_start is not None:
        chunk_text = " ".join(current_chunk_words).strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "start": round(chunk_start, 2),
                "end": round(deduped_segments[-1]["end"], 2)
            })

    # If segments didn't have words, use segment bounds
    if not chunks:
        for s in deduped_segments:
            chunks.append({
                "text": s["text"],
                "start": round(s["start"], 2),
                "end": round(s["end"], 2)
            })

    # Skip consecutive duplicate chunks
    final_chunks = []
    prev_chunk_txt = ""
    for c in chunks:
        if c["text"] == prev_chunk_txt:
            continue
        final_chunks.append(c)
        prev_chunk_txt = c["text"]

    processed = {
        "id": vid,
        "title": title,
        "speaker": speaker,
        "category": category,
        "date": date,
        "url": url,
        "m3u8": m3u8,
        "thumbnail": thumbnail,
        "language": lang,
        "chunks": final_chunks
    }

    proc_out = f"processed_transcripts/{vid}_transcript.json"
    with open(proc_out, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=4, ensure_ascii=False)
    print(f"Saved cleaned processed transcript with {len(final_chunks)} chunks to {proc_out}")

print("\nAll videos re-transcribed and cleaned successfully!")
