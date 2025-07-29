import json
import os
from datetime import datetime

def load_json(path, default=None):
    """Carga un archivo JSON y devuelve su contenido."""
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠ Error leyendo {path}: {e}")
        return default if default is not None else {}

def save_json(path, data):
    """Guarda un diccionario o lista en un archivo JSON."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠ Error guardando {path}: {e}")

def log(message, level="INFO"):
    """Log simple con timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level.upper()}] {message}")
