import chromadb
import json
import os
import re
import urllib.request
import urllib.parse
import tensorflow_text
import tensorflow_hub as hub

os.environ["TFHUB_CACHE_DIR"] = "/db/src/tfhub_cache"

STOP_WORDS = {
    "a", "about", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "how", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
    "was", "what", "when", "where", "who", "will", "with", "und", "der", "die", "das"
}

TRANSLATION_CACHE = {}

KNOWN_TRANSLATIONS = {
    "மனശാസ്ത്രம்": "psychology",
    "மநசாஸ்திரம்": "psychology",
    "മനശാസ്ത്രം": "psychology",
    "मनोविज्ञान": "psychology",
    "sozialwissenschaften": "social sciences",
    "കമ്പ്യൂട്ടർ സയൻസ്": "computer science",
    "கணினி அறிவியல்": "computer science",
    "कंप्यूटर साइंस": "computer science",
    "informatik": "computer science",
    "പൈത്തൺ": "Python",
    "பைதான்": "Python",
    "पायथन": "Python",
    "ഗുണനം": "multiplication",
    "பெருக்கல்": "multiplication",
    "गुणा": "multiplication",
    "നാണയങ്ങൾ": "coins",
    "நாணயங்கள்": "coins",
    "सिक्के": "coins",
    "ചൈനയിലെ വന്മതിൽ": "Great Wall of China",
    "சீனப் பெருஞ்சுவர்": "Great Wall of China",
    "चीन की महान दीवार": "Great Wall of China",
    "बीजगणित": "algebra",
    "ബീജഗണിതം": "algebra",
    "இயற்கணிதம்": "algebra",
}

def translate_query(q):
    if not q or len(q.strip()) < 2:
        return q, "en"
    q_clean = q.strip()
    q_key = q_clean.lower()
    if q_key in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[q_key]
    if q_key in KNOWN_TRANSLATIONS:
        res = (KNOWN_TRANSLATIONS[q_key], "auto")
        TRANSLATION_CACHE[q_key] = res
        return res
    endpoints = [
        ("https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q=", lambda d: "".join([p[0] for p in d[0] if p[0]]), lambda d: d[2] if len(d) > 2 else "en"),
        ("https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=auto&tl=en&q=", lambda d: d[0] if isinstance(d, list) and d else str(d), lambda d: "en")
    ]
    for url_prefix, parse_text, parse_lang in endpoints:
        try:
            url = url_prefix + urllib.parse.quote(q_clean)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=3) as r:
                res = json.loads(r.read().decode("utf-8"))
                translated = parse_text(res)
                detected_lang = parse_lang(res)
                result = (translated.strip(), detected_lang)
                TRANSLATION_CACHE[q_key] = result
                return result
        except Exception:
            continue
    return q, "en"

class USEEmbeddingFunction:
    def __init__(self):
        # Load the USE Large model
        self.model_url = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
        self.embed = hub.load(self.model_url)

    def __call__(self, input: list[str]) -> list[list[float]]:
        # Generate embeddings for the input texts
        return self.embed(input).numpy()

def get_embedding_function():
    use_embedding_function = USEEmbeddingFunction()
    return use_embedding_function

client = chromadb.HttpClient(host="chromadb", port=8000)

use_ef = get_embedding_function()

collection_name = "w4a-v2"
collection = client.get_or_create_collection(name=collection_name, embedding_function=use_ef)

def querry_text(text, n_results):
    try:
        count = collection.count()
        if count == 0:
            return {"ids": [[]], "metadatas": [[]], "documents": [[]], "distances": [[]]}
        n_results = min(n_results, count)
        q = [text] if isinstance(text, str) else list(text)
        result = collection.query(
            query_texts=q,
            n_results=n_results
        )
        return result
    except Exception as e:
        print(f"Error querying chroma: {e}")
        return {"ids": [[]], "metadatas": [[]], "documents": [[]], "distances": [[]]}

def get_querry_result(text):
    formatted_result = []
    n_results = 50
    result = querry_text(text, n_results)
    if not result or not result.get("ids") or len(result["ids"][0]) == 0:
        return formatted_result
    
    seen_ids = set()
    total_queries = len(result["ids"])
    for q_idx in range(total_queries):
        length = len(result["ids"][q_idx])
        distances = result.get("distances", [[]])[q_idx] if ("distances" in result and result["distances"] and len(result["distances"]) > q_idx) else [1.0] * length
        for i in range(length):
            doc_id = result["ids"][q_idx][i]
            dist_val = float(distances[i]) if i < len(distances) else 1.0
            if doc_id in seen_ids:
                # Update with minimum distance if seen
                for existing in formatted_result:
                    if existing["ids"] == doc_id:
                        if dist_val < existing["distance"]:
                            existing["distance"] = dist_val
                        break
                continue
            seen_ids.add(doc_id)
            entry = {
                "resultNr": len(formatted_result) + 1,
                "ids": doc_id,
                "metadatas": result["metadatas"][q_idx][i],
                "documents": result["documents"][q_idx][i],
                "distance": dist_val,
            }
            formatted_result.append(entry)
    return formatted_result

def format_result(result, qtext="", translated_q=""):
    path_to_subtittles = "/transcription/subtitles"
    result_json = {
        "videos": []
    }
    if not result:
        return json.dumps(result_json, ensure_ascii=False, indent=4)

    query_lower = (qtext or "").lower().strip()
    trans_lower = (translated_q or "").lower().strip()

    tokens = [w for w in re.findall(r'\w+', query_lower) if len(w) >= 2]
    trans_tokens = [w for w in re.findall(r'\w+', trans_lower) if len(w) >= 2]

    combined_tokens = list(dict.fromkeys(tokens + trans_tokens))
    meaningful_tokens = [w for w in combined_tokens if w not in STOP_WORDS]
    match_tokens = meaningful_tokens if meaningful_tokens else combined_tokens

    videos = {}
    for entry in result:
        meta = entry["metadatas"]
        video_id = meta["video_id"]
        raw_text = meta.get("raw_text") or entry["documents"]
        dist = entry.get("distance", 1.0)

        chunk_sim = max(0.0, 2.0 - dist)
        chunk_item = {
            "text": raw_text,
            "start": meta.get("start", 0.0),
            "end": meta.get("end", 0.0),
            "distance": dist,
            "chunk_sim": chunk_sim
        }

        if video_id not in videos:
            cat_val = meta.get("category", "")
            if isinstance(cat_val, list):
                categories = cat_val
                cat_str = " ".join([str(x) for x in cat_val])
            else:
                cat_str = str(cat_val)
                categories = [cat_str.split("\n")]

            ger_sub = f"{path_to_subtittles}/{video_id}_subtitles_de.srt"
            eng_sub = f"{path_to_subtittles}/{video_id}_subtitles.srt"
            videos[video_id] = {
                "video_id": video_id,
                "title": meta.get("title", ""),
                "speaker": meta.get("speaker", ""),
                "date": meta.get("date", ""),
                "language": meta.get("language", "en"),
                "ger_sub": ger_sub,
                "eng_sub": eng_sub,
                "category": categories,
                "category_str": cat_str,
                "m3u8_url": meta.get("m3u8_url", ""),
                "thumbnail_url": meta.get("thumbnail_url", ""),
                "chunks": [chunk_item]
            }
        else:
            videos[video_id]["chunks"].append(chunk_item)

    for video in videos.values():
        v_title = video["title"].lower()
        v_cat = video["category_str"].lower()

        best_chunk_sim = max([c["chunk_sim"] for c in video["chunks"]]) if video["chunks"] else 0.0
        kw_boost = 0.0

        # 1. Verbatim user query matches (highest priority)
        if query_lower and len(query_lower) >= 3:
            if query_lower in v_title:
                kw_boost += 8.0
            elif query_lower in v_cat:
                kw_boost += 4.0

        # 2. Translated cross-lingual query matches
        if trans_lower and len(trans_lower) >= 3 and trans_lower != query_lower:
            if trans_lower in v_title:
                kw_boost += 5.0
            elif trans_lower in v_cat:
                kw_boost += 2.5

        # 3. Token-level matches
        for t in match_tokens:
            is_orig_token = t in tokens
            title_boost = 4.0 if is_orig_token else 2.5
            cat_boost = 2.0 if is_orig_token else 1.2
            chunk_boost = 1.0 if is_orig_token else 0.6

            if t in v_title:
                kw_boost += title_boost
            elif t in v_cat:
                kw_boost += cat_boost

            if (t == "psychology" and "psychologie" in v_cat) or (t == "psychologie" and "psychology" in v_title):
                kw_boost += title_boost

            for c in video["chunks"]:
                if t in c["text"].lower():
                    kw_boost += chunk_boost
                    break

        video["_score"] = best_chunk_sim + kw_boost

    sorted_videos = sorted(videos.values(), key=lambda v: v["_score"], reverse=True)

    for vrank, video in enumerate(sorted_videos, 1):
        video["rank"] = str(vrank)

        def chunk_sort_key(c):
            kw_match = any(t in c["text"].lower() for t in match_tokens) if match_tokens else False
            return (0 if kw_match else 1, c["distance"])

        sorted_chunks = sorted(video["chunks"], key=chunk_sort_key)[:10]
        for crank, c in enumerate(sorted_chunks, 1):
            c["chunk_rank"] = str(crank)
            del c["distance"]
            del c["chunk_sim"]

        video["chunks"] = sorted_chunks
        del video["_score"]
        if "category_str" in video:
            del video["category_str"]

    result_json["videos"] = sorted_videos
    return json.dumps(result_json, ensure_ascii=False, indent=4)

def process_query(qtext):
    translated_q, _ = translate_query(qtext)
    if translated_q and translated_q.lower() != qtext.lower():
        q_inputs = [translated_q, qtext]
    else:
        q_inputs = qtext
    query = get_querry_result(q_inputs)
    return format_result(query, qtext=qtext, translated_q=translated_q)