import os
import json
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def transcribe_video(video_path, client):
    """Transcreve vídeo diretamente usando Groq"""
    with open(video_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3"
        )
    return transcription.text

def process_videos():
    """Processa todos os vídeos e gera transcrições"""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    videos_dir = Path("videos")
    transcriptions = {}
    
    for creator_dir in videos_dir.iterdir():
        if creator_dir.is_dir():
            creator = creator_dir.name
            transcriptions[creator] = []
            
            for video_file in creator_dir.glob("*.mp4"):
                print(f"Processando: {video_file}")
                
                try:
                    text = transcribe_video(video_file, client)
                    transcriptions[creator].append({
                        "video": video_file.name,
                        "transcription": text
                    })
                    print(f"✓ Concluído: {video_file.name}")
                except Exception as e:
                    print(f"✗ Erro em {video_file.name}: {e}")
    
    with open("transcriptions.json", "w", encoding="utf-8") as f:
        json.dump(transcriptions, f, ensure_ascii=False, indent=2)
    
    print("\nTranscrições salvas em transcriptions.json")

if __name__ == "__main__":
    process_videos()
