import whisper

model = whisper.load_model("medium", device="cuda")

result = model.transcribe(
    "./videos/sa_vlkn_test.webm"
)

print("Detected language:", result["language"])
print("\n--- TRANSCRIPTION ---")
print(result["text"])