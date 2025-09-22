import json
from pathlib import Path
from typing import Optional, List, Dict

def load_transcriptions(file_path: str = "transcriptions.json") -> Dict:
    """
    Carrega o arquivo de transcrições JSON.
    
    Args:
        file_path: Caminho para o arquivo de transcrições
        
    Returns:
        Dicionário com as transcrições organizadas por criador
        
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado
        json.JSONDecodeError: Se o arquivo não for um JSON válido
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de transcrições não encontrado: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Erro ao decodificar JSON: {e}")

def format_transcriptions_to_markdown(transcriptions: List[Dict]) -> str:
    """
    Formata uma lista de transcrições para markdown.
    
    Args:
        transcriptions: Lista de dicionários com 'video' e 'transcription'
        
    Returns:
        String formatada em markdown
    """
    if not transcriptions:
        return "Nenhuma transcrição encontrada."
    
    formatted_parts = []
    for i, transcript in enumerate(transcriptions, 1):
        formatted_parts.append(f"Transcript {i}")
        formatted_parts.append(transcript['transcription'].strip())
        formatted_parts.append("")  # Linha em branco entre transcrições
    
    # Remove a última linha em branco
    if formatted_parts and formatted_parts[-1] == "":
        formatted_parts.pop()
    
    return "\n".join(formatted_parts)

def get_creator_transcriptions(creator_name: str, transcriptions_file: str = "transcriptions.json") -> str:
    """
    Função principal para extrair transcrições de um criador específico.
    
    Esta função é projetada para ser usada por agentes de IA.
    
    Args:
        creator_name: Nome do criador (ex: 'jeffnippard', 'kallaway', 'rourkeheath')
        transcriptions_file: Caminho para o arquivo de transcrições
        
    Returns:
        String formatada em markdown com todas as transcrições do criador
        
    Example:
        >>> transcripts = get_creator_transcriptions("jeffnippard")
        >>> print(transcripts)
        Transcript 1
        All right, this is my leg workout based on science...
        
        Transcript 2
        Losing muscle could cost you your life...
    """
    try:
        # Carrega as transcrições
        all_transcriptions = load_transcriptions(transcriptions_file)
        
        # Busca o criador (case-insensitive)
        creator_key = None
        for key in all_transcriptions.keys():
            if key.lower() == creator_name.lower():
                creator_key = key
                break
        
        if creator_key is None:
            available_creators = list(all_transcriptions.keys())
            return f"Criador '{creator_name}' não encontrado. Criadores disponíveis: {', '.join(available_creators)}"
        
        # Obtém as transcrições do criador
        creator_transcriptions = all_transcriptions[creator_key]
        
        # Formata para markdown
        return format_transcriptions_to_markdown(creator_transcriptions)
        
    except Exception as e:
        return f"Erro ao processar transcrições: {str(e)}"

def list_available_creators(transcriptions_file: str = "transcriptions.json") -> List[str]:
    """
    Lista todos os criadores disponíveis no arquivo de transcrições.
    
    Args:
        transcriptions_file: Caminho para o arquivo de transcrições
        
    Returns:
        Lista com nomes dos criadores disponíveis
    """
    try:
        all_transcriptions = load_transcriptions(transcriptions_file)
        return list(all_transcriptions.keys())
    except Exception as e:
        print(f"Erro ao listar criadores: {e}")
        return []

# Função de conveniência para agentes de IA
def get_transcripts(creator: str) -> str:
    """
    Função simplificada para agentes de IA obterem transcrições.
    
    Args:
        creator: Nome do criador
        
    Returns:
        Transcrições formatadas em markdown
    """
    return get_creator_transcriptions(creator)
