"""
Strukturalne logowanie dla wszystkich serwisów
"""
import structlog
import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format: str = "json",
    service_name: Optional[str] = None
) -> None:
    """
    Konfiguracja structlog dla całego serwisu
    
    Args:
        level: DEBUG, INFO, WARNING, ERROR
        format: 'json' lub 'console'
        service_name: Nazwa serwisu (np. 'collector')
    """
    
    # Procesory wspólne dla wszystkich formatów
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if service_name:
        shared_processors.append(
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            )
        )
    
    # Wybór formatu
    if format == "json":
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:  # console
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    # Konfiguracja structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Konfiguracja standardowego loggera
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    # Dodaj service_name do kontekstu
    if service_name:
        structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Pobierz logger dla modułu
    
    Args:
        name: Nazwa loggera (domyślnie __name__ wywołującego)
    """
    return structlog.get_logger(name)
