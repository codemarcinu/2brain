"""
Narzędzia pomocnicze używane w wielu miejscach
"""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_task_id(prefix: str = "task") -> str:
    """
    Generuj unikalny ID zadania
    
    Args:
        prefix: Prefiks (np. 'yt', 'art', 'rec')
    
    Returns:
        ID w formacie: prefix_YYYYMMDD_HHMMSS_hash
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    random_hash = hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_hash}"


def sanitize_filename(text: str, max_length: int = 100) -> str:
    """
    Przekształć tekst na bezpieczną nazwę pliku
    
    Args:
        text: Oryginalny tekst
        max_length: Maksymalna długość nazwy
    
    Returns:
        Bezpieczna nazwa pliku
    """
    # Usuń niebezpieczne znaki
    safe = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_'))
    # Zamień spacje na podkreślenia
    safe = safe.replace(' ', '_')
    # Ogranicz długość
    return safe[:max_length].strip('_')


def ensure_path_exists(path: Path) -> Path:
    """
    Upewnij się że katalog istnieje (utwórz jeśli nie)
    
    Args:
        path: Ścieżka do katalogu
    
    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def calculate_file_hash(file_path: Path) -> str:
    """
    Oblicz MD5 hash pliku (do deduplikacji)
    
    Args:
        file_path: Ścieżka do pliku
    
    Returns:
        MD5 hash jako hex string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
