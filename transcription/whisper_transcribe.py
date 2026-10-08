import os
import sys
import whisper_timestamped
import json    

"""
Author: w4a-backend
Description: This script transcribes all videos in the video directory
"""

def loadModel(model_size="medium"):
    model = whisper_timestamped.load_model(model_size, device="cuda")
    return model

def transcribeVideo(model, videoPath):
    result = whisper_timestamped.transcribe(model, videoPath)
    return result

def saveTranscription(result, output_json):
    os.makedirs("transcriptions", exist_ok=True)
    output_path = os.path.join("transcriptions", output_json)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    videos_directory = "./videos"
    arguments = sys.argv
    if len(arguments) < 3:
        print("Usage: python whisper_transcribe.py <start_index> <end_index>")
        sys.exit(1)
    start_index = int(arguments[1])
    end_index = int(arguments[2])
    #video_files = [f for f in os.listdir(videos_directory) if f.endswith(".mp4")]
    #video_files.sort()
    #print(len(video_files))

    print("Loading whisper model...")
    model = loadModel()
    os.system('cls' if os.name == 'nt' else 'clear')

    for i in range(int(start_index), int(end_index) + 1):
        filename = f"{i}.mp4"
        video_path = os.path.join(videos_directory, filename)
        
        if not os.path.exists(video_path):
            print(f"Video {filename} does not exist. Checking for mp3...")
            filename = f"{i}.mp3"
            video_path = os.path.join(videos_directory, filename)
            if not os.path.exists(video_path):
                print(f"Audio {filename} does not exist. Skipping...")
                continue
        
        output_json = f"{i}_transcript.json"
        output_path = os.path.join("transcriptions", output_json)
        if os.path.exists(output_path):
            print(f"Transcription for {video_path} already exists. Skipping...")
            continue
        print(f"Transcribing {filename} from {start_index} to {end_index}")
        result = transcribeVideo(model, video_path)
        saveTranscription(result, output_json)
        
        print(f"Saved transcription for {filename}. Continuing...")
    print("All done!")
