"""
Audio transcription using Whisper
"""
from pathlib import Path
from typing import Optional
from faster_whisper import WhisperModel
from shared.logging import get_logger

logger = get_logger(__name__)


class Transcriber:
    """Wrapper dla faster-whisper"""
    
    def __init__(
        self,
        model_size: str = "medium",
        device: str = "auto",
        compute_type: str = "float16"
    ):
        """
        Args:
            model_size: tiny, base, small, medium, large
            device: auto, cpu, cuda
            compute_type: float16, int8, float32
        """
        logger.info(
            "transcriber_initializing",
            model=model_size,
            device=device
        )
        
        # Adjust compute_type based on deviceavailability if needed, 
        # normally faster-whisper handles "auto" device intelligently.
        # But compute_type might need fallback to "int8" or "float32" on CPU.
        
        if device == "cpu" and compute_type == "float16":
             # float16 is not supported on CPU
             compute_type = "int8"

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        
        logger.info("transcriber_ready")
    
    def transcribe(
        self,
        audio_path: Path,
        language: str = "pl"
    ) -> Optional[str]:
        """
        Transkrybuj plik audio
        
        Args:
            audio_path: Ścieżka do pliku audio
            language: Kod języka (pl, en, auto)
        
        Returns:
            Pełna transkrypcja jako string
        """
        try:
            logger.info(
                "transcription_started",
                file=audio_path.name,
                language=language
            )
            
            # Transkrypcja
            # language=None means auto-detect
            segments, info = self.model.transcribe(
                str(audio_path),
                language=None if language == "auto" else language,
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection
            )
            
            # Połącz segmenty w pełny tekst
            # Note: segments is a generator, so we iterate list comprehension
            full_text = " ".join([segment.text for segment in segments])
            
            logger.info(
                "transcription_completed",
                file=audio_path.name,
                detected_language=info.language,
                duration_seconds=info.duration,
                text_length=len(full_text)
            )
            
            return full_text
            
        except Exception as e:
            logger.error(
                "transcription_failed",
                file=audio_path.name,
                error=str(e)
            )
            return None
