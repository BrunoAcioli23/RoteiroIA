import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def split_video(video_path, chunk_duration=30):
    """Divide vídeo em chunks de duração especificada (em segundos)"""
    temp_dir = tempfile.mkdtemp()
    chunks = []
    
    try:
        # Obter duração do vídeo
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', str(video_path)
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        total_duration = float(result.stdout.strip())
        
        # Dividir em chunks
        chunk_count = int(total_duration / chunk_duration) + 1
        
        for i in range(chunk_count):
            start_time = i * chunk_duration
            output_path = Path(temp_dir) / f"chunk_{i:03d}.mp4"
            
            cmd = [
                'ffmpeg', '-i', str(video_path),
                '-ss', str(start_time), '-t', str(chunk_duration),
                '-c', 'copy', str(output_path), '-y'
            ]
            
            subprocess.run(cmd, capture_output=True)
            if output_path.exists():
                chunk_size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"      Chunk {i+1}: {chunk_size_mb:.1f}MB")
                chunks.append(output_path)
    
    except Exception as e:
        print(f"Erro ao dividir vídeo: {e}")
        # Limpar em caso de erro
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return []
    
    return chunks, temp_dir

def transcribe_video(video_path, client):
    """Transcreve vídeo diretamente usando Groq"""
    with open(video_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3"
        )
    return transcription.text

def transcribe_large_video(video_path, client, max_size_mb=15):
    """Transcreve vídeo grande dividindo em chunks se necessário"""
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    
    if file_size_mb <= max_size_mb:
        # Arquivo pequeno, transcrever diretamente
        return transcribe_video(video_path, client)
    
    print(f"  Arquivo grande ({file_size_mb:.1f}MB), dividindo em chunks...")
    
    # Dividir em chunks
    chunks, temp_dir = split_video(video_path)
    
    if not chunks:
        raise Exception("Não foi possível dividir o vídeo em chunks")
    
    try:
        # Transcrever cada chunk
        transcriptions = []
        for i, chunk_path in enumerate(chunks):
            print(f"    Processando chunk {i+1}/{len(chunks)}")
            chunk_text = transcribe_video(chunk_path, client)
            transcriptions.append(chunk_text)
        
        # Combinar transcrições
        full_transcription = " ".join(transcriptions)
        return full_transcription
    
    finally:
        # Limpar arquivos temporários
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

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
                    text = transcribe_large_video(video_file, client)
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
