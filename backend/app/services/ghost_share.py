import os
import time
import json
import asyncio
from typing import Dict, Any, Optional, List
from app.core.config import DATA_DIR
from app.services.document_classifier import delete_file_metadata, get_file_metadata, update_file_metadata

GHOST_FILE = os.path.join(DATA_DIR, "ghost_shares.json")


def load_ghost_records() -> Dict[str, Dict[str, Any]]:
    if os.path.exists(GHOST_FILE):
        try:
            with open(GHOST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_ghost_records(data: Dict[str, Dict[str, Any]]):
    try:
        with open(GHOST_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving ghost records: {e}")


class GhostShareEngine:
    def __init__(self):
        pass

    def enable_ghost_share(self, filename: str, max_downloads: int = 1, ttl_seconds: Optional[int] = 300) -> Dict[str, Any]:
        records = load_ghost_records()
        expires_at = time.time() + ttl_seconds if ttl_seconds else None

        records[filename] = {
            "ghost_active": True,
            "max_downloads": max_downloads,
            "downloads_count": 0,
            "expires_at": expires_at,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_ghost_records(records)
        update_file_metadata(filename, {"is_ghost_share": True})

        return {
            "filename": filename,
            "ghost_active": True,
            "max_downloads": max_downloads,
            "ttl_seconds": ttl_seconds,
            "message": f"Ghost Share activated for {filename}! Will self-destruct after {max_downloads} download(s)."
        }

    def check_and_handle_download_destruct(self, filename: str, shared_dir: str) -> bool:
        records = load_ghost_records()
        if filename in records and records[filename].get("ghost_active"):
            rec = records[filename]
            rec["downloads_count"] += 1
            
            if rec["downloads_count"] >= rec["max_downloads"]:
                self._shred_file(filename, shared_dir)
                del records[filename]
                save_ghost_records(records)
                return True
            else:
                save_ghost_records(records)
        return False

    def _shred_file(self, filename: str, shared_dir: str):
        file_path = os.path.join(shared_dir, filename)
        try:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                with open(file_path, "wb") as f:
                    f.write(b'\x00' * min(size, 1024 * 1024))
                os.remove(file_path)
            delete_file_metadata(filename)
        except Exception as e:
            print(f"Error shredding ghost file {filename}: {e}")

    def cleanup_expired_ghosts(self, shared_dir: str) -> List[str]:
        records = load_ghost_records()
        now = time.time()
        expired_files = []

        for fn, rec in list(records.items()):
            if rec.get("expires_at") and now >= rec["expires_at"]:
                self._shred_file(fn, shared_dir)
                expired_files.append(fn)
                del records[fn]

        if expired_files:
            save_ghost_records(records)
        return expired_files


ghost_engine = GhostShareEngine()
