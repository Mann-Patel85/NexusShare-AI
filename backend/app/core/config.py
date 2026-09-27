import os
import socket

# Base Directory paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_DIR = os.path.join(BACKEND_DIR, "app")
DATA_DIR = os.path.join(APP_DIR, "data")
SHARED_DIR = os.path.join(BACKEND_DIR, "shared_files")
ROOT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SHARED_DIR, exist_ok=True)


def get_local_ip() -> str:
    """Retrieve host primary local Wi-Fi/Ethernet IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable units."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {units[i]}"


def get_file_category(filename: str) -> str:
    """Categorize file type by extension for UI icons & badges."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"]:
        return "image"
    elif ext in [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"]:
        return "document"
    elif ext in [".mp4", ".mkv", ".mov", ".avi", ".webm"]:
        return "video"
    elif ext in [".mp3", ".wav", ".ogg", ".flac", ".m4a"]:
        return "audio"
    elif ext in [".zip", ".tar", ".gz", ".7z", ".rar"]:
        return "archive"
    elif ext in [".py", ".js", ".ts", ".html", ".css", ".json", ".cpp", ".c", ".java"]:
        return "code"
    return "other"
