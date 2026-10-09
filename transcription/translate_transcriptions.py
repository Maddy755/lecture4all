import json
import os
import sys
import torch
from transformers import MarianMTModel, MarianTokenizer, AutoModelForSeq2SeqLM, AutoTokenizer

"""
Author: w4a-backend
Description: Translates processed English transcripts into Tamil, Malayalam, and Hindi.
             Reads from ./processed_transcripts and writes per-language JSON files to
             ./translated_transcriptions/<lang>/<id>_transcript.json

Usage: python translate_transcriptions.py <start_index> <end_index>
"""

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

TARGET_LANGUAGES = [
    ("ta", "facebook/nllb-200-distilled-600M", "nllb", None, "tam_Taml"),
    ("ml", "facebook/nllb-200-distilled-600M", "nllb", None, "mal_Mlym"),
    ("hi", "facebook/nllb-200-distilled-600M", "nllb", None, "hin_Deva"),
]

WHISPER_TO_NLLB = {
    "en": "eng_Latn", "de": "deu_Latn", "fr": "fra_Latn", "es": "spa_Latn",
    "it": "ita_Latn", "pt": "por_Latn", "ru": "rus_Cyrl", "zh": "zho_Hans",
    "ja": "jpn_Jpan", "ko": "kor_Hang", "hi": "hin_Deva", "ta": "tam_Taml",
    "ml": "mal_Mlym", "ar": "arb_Arab", "tr": "tur_Latn", "nl": "nld_Latn"
}

processed_dir = "./processed_transcripts"
output_base_dir = "./translated_transcriptions"


def load_model(model_name, model_type):
    print(f"Loading model {model_name} ({model_type}) on {DEVICE}...")
    if model_type == "nllb":
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(DEVICE)
    else:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name).to(DEVICE)
    return tokenizer, model


def translate_batch(texts, tokenizer, model, model_type="marian", src_lang=None, tgt_lang=None, batch_size=4):
    """Translate a list of strings, returning a list of translated strings."""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            if model_type == "nllb":
                tokenizer.src_lang = src_lang
                inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=256).to(DEVICE)
                tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_lang)
                with torch.no_grad():
                    translated = model.generate(**inputs, forced_bos_token_id=tgt_lang_id, num_beams=2)
            else:
                inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=256).to(DEVICE)
                with torch.no_grad():
                    translated = model.generate(**inputs, num_beams=2)
            decoded = tokenizer.batch_decode(translated, skip_special_tokens=True)
        except RuntimeError:
            print(f"  OOM on batch {i//batch_size}, falling back to CPU one-by-one...")
            if DEVICE == "cuda":
                torch.cuda.empty_cache()
            decoded = []
            model.to("cpu")
            for text in batch:
                if model_type == "nllb":
                    tokenizer.src_lang = src_lang
                    inp = tokenizer([text], return_tensors="pt", truncation=True, max_length=256)
                    tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_lang)
                    with torch.no_grad():
                        out = model.generate(**inp, forced_bos_token_id=tgt_lang_id, num_beams=2)
                else:
                    inp = tokenizer([text], return_tensors="pt", truncation=True, max_length=256)
                    with torch.no_grad():
                        out = model.generate(**inp, num_beams=2)
                decoded.append(tokenizer.decode(out[0], skip_special_tokens=True))
            model.to(DEVICE)
        results.extend(decoded)
    return results


def translate_transcript(transcript_id, tokenizer, model, lang_code, model_type="marian", src_lang=None, tgt_lang=None):
    filename = f"{transcript_id}_transcript.json"
    input_path = os.path.join(processed_dir, filename)

    if not os.path.exists(input_path):
        print(f"Processed transcript not found: {input_path}. Skipping...")
        return

    lang_dir = os.path.join(output_base_dir, lang_code)
    os.makedirs(lang_dir, exist_ok=True)
    output_path = os.path.join(lang_dir, filename)

    if os.path.exists(output_path):
        print(f"Already exists, skipping: {output_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        processed = json.load(f)

    detected_lang = processed.get("language", "en")

    if detected_lang == lang_code:
        print(f"Skipping translation for {filename}; source is already in target language ({lang_code})")
        return

    if model_type == "marian" and detected_lang != "en":
        print(f"Skipping marian translation for {filename}; source is not English ({detected_lang})")
        return

    if model_type == "nllb":
        src_lang = WHISPER_TO_NLLB.get(detected_lang, "eng_Latn")

    chunks = processed.get("chunks", [])
    if not chunks:
        print(f"No chunks found in {input_path}. Skipping...")
        return

    texts = [c["text"] for c in chunks]
    print(f"  Translating {len(texts)} chunks for id={transcript_id} -> {lang_code}")
    translated_texts = translate_batch(texts, tokenizer, model, model_type, src_lang, tgt_lang)

    translated_chunks = [
        {"text": t, "start": c["start"], "end": c["end"]}
        for t, c in zip(translated_texts, chunks)
    ]

    output = dict(processed)
    output["chunks"] = translated_chunks
    output["translation_language"] = lang_code

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    print(f"  Saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translate_transcriptions.py <start_index> <end_index>")
        print("   or: python translate_transcriptions.py all")
        sys.exit(1)

    if sys.argv[1] == "all":
        ids = []
        if os.path.exists(processed_dir):
            for f in sorted(os.listdir(processed_dir)):
                if f.endswith("_transcript.json"):
                    ids.append(f[:-16])
        if not ids:
            print(f"No processed transcripts found in {processed_dir}.")
            sys.exit(0)
    elif len(sys.argv) >= 3:
        try:
            start_index = int(sys.argv[1])
            end_index = int(sys.argv[2])
            ids = list(range(start_index, end_index + 1))
        except ValueError:
            ids = sys.argv[1:]
    else:
        ids = [sys.argv[1]]

    current_model_key = None
    tokenizer, model = None, None

    for lang_code, model_name, model_type, src_lang, tgt_lang in TARGET_LANGUAGES:
        print(f"\n=== Translating to '{lang_code}' using {model_name} ===")
        model_key = (model_name, model_type)
        if model_key != current_model_key:
            if model is not None:
                del model
                if DEVICE == "cuda":
                    torch.cuda.empty_cache()
            tokenizer, model = load_model(model_name, model_type)
            current_model_key = model_key

        for transcript_id in ids:
            print(f"Processing id={transcript_id}")
            translate_transcript(transcript_id, tokenizer, model, lang_code, model_type, src_lang, tgt_lang)

    if model is not None:
        del model
        if DEVICE == "cuda":
            torch.cuda.empty_cache()

    print("\nAll translations done!")
