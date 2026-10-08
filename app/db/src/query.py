import chromadb
import json
import os
import tensorflow_text
import tensorflow_hub as hub

os.environ["TFHUB_CACHE_DIR"] = "/db/src/tfhub_cache"

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
collection = client.get_collection(name=collection_name, embedding_function=use_ef)

def querry_text(text,n_results):
    result = collection.query(
        query_texts=text,
        n_results=n_results
    )
    return result

def get_querry_result(text):
    formatted_result = []
    n_results = 50
    result = querry_text(text, n_results)
    length = len(result["ids"][0])
    for i in range(length):
        nr = i+1
        entry = {
            "resultNr": nr,
            "ids": result["ids"][0][i],
            "metadatas": result["metadatas"][0][i],
            "documents": result["documents"][0][i],

        }
        formatted_result.append(entry)
    return formatted_result

def format_result(result):
    path_to_subtittles = "/transcription/subtitles"
    result_json = {
        "videos": []
    }    
    videos = {}
    vrank = 1
    crank = 0
    for entry in result:
        crank += 1
        video_id = entry["metadatas"]["video_id"]
        ger_sub = f"{path_to_subtittles}/{video_id}_subtitles_de.srt"
        eng_sub = f"{path_to_subtittles}/{video_id}_subtitles.srt"
        if not entry["metadatas"]["video_id"] in videos:
            categories = []
            categories.append(entry["metadatas"]["category"].split("\n"))
            video = {
                "rank" : f"{vrank}",
                "video_id": entry["metadatas"]["video_id"],
                "title": entry["metadatas"]["title"],
                "speaker": entry["metadatas"]["speaker"],
                "date": entry["metadatas"]["date"],
                "ger_sub": ger_sub,
                "eng_sub": eng_sub,
                "category": categories,
                "m3u8_url": entry["metadatas"]["m3u8_url"],
                "thumbnail_url": entry["metadatas"]["thumbnail_url"],
                "chunks": [{"text": entry["documents"],
                             "start": entry["metadatas"]["start"],
                               "end": entry["metadatas"]["end"],
                               "chunk_rank": f"{crank}"}]
            }
            videos[entry["metadatas"]["video_id"]] = video
            vrank += 1
        else:
            if len(video["chunks"]) >= 10:
                continue
            video = videos[entry["metadatas"]["video_id"]]
            video["chunks"].append({"text": entry["documents"],
                                    "start": entry["metadatas"]["start"],
                                    "end": entry["metadatas"]["end"],
                                    "chunk_rank": f"{crank}"})
        result_json["videos"].append(video)
    
    result_json["videos"] = list(videos.values())
    return json.dumps(result_json, ensure_ascii=False, indent=4)

def process_query(qtext):
    query = get_querry_result(qtext)
    return format_result(query)