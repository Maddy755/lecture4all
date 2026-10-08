import whisper
import json

model = whisper.load_model("medium", device="cuda")

result = model.transcribe(
    "./videos/tamil_cs_test.wav"
)

print("Detected language:", result["language"])
print("\n--- TRANSCRIPTION ---")
print(result["text"])

with open(
    "./transcriptions/tamil_cs_test_transcript.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(result, f, ensure_ascii=False, indent=4)