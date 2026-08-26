import logging
from pathlib import Path
from antonino_tuttofare import config

def get_logger(name: str) -> logging.Logger:
    """
    Returns a pre-configured logger instance with file rotation 
    to prevent disk space exhaustion on embedded devices like Raspberry Pi.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times if get_logger is called repeatedly
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # Ensure log directory exists inside DATA_DIR (e.g., ~/.local/share/antonino_tuttofare/logs/)
    log_dir = config.DATA_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"
    
    # Formatter: timestamp - module name - severity - message
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler (writes to disk)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=2 * 1024 * 1024, backupCount=3  # Max 2MB per file, keeps last 3 backups
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO) # Salva da INFO in su su file
    
    # Console handler (writes to terminal if run manually)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG) # Mostra tutto a terminale
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger