import os
import hashlib
from typing import Dict, List, Any
from app.core.config import format_file_size


class StorageDeduplicationEngine:
    def __init__(self):
        pass

    def _hash_file(self, filepath: str) -> str:
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def scan_for_duplicates(self, shared_dir: str) -> Dict[str, Any]:
        if not os.path.exists(shared_dir):
            return {"duplicate_groups": [], "reclaimable_bytes": 0, "formatted_reclaimable": "0 B"}

        hash_map: Dict[str, List[Dict[str, Any]]] = {}
        total_reclaimable = 0

        for name in os.listdir(shared_dir):
            filepath = os.path.join(shared_dir, name)
            if os.path.isfile(filepath):
                file_hash = self._hash_file(filepath)
                if not file_hash:
                    continue
                size = os.path.getsize(filepath)

                file_info = {
                    "filename": name,
                    "size_bytes": size,
                    "formatted_size": format_file_size(size),
                    "path": filepath
                }

                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(file_info)

        duplicate_groups = []
        for file_hash, group in hash_map.items():
            if len(group) > 1:
                group_reclaimable = sum(f["size_bytes"] for f in group[1:])
                total_reclaimable += group_reclaimable
                duplicate_groups.append({
                    "hash": file_hash,
                    "original": group[0],
                    "duplicates": group[1:],
                    "count": len(group),
                    "reclaimable_bytes": group_reclaimable,
                    "formatted_reclaimable": format_file_size(group_reclaimable)
                })

        return {
            "duplicate_groups": duplicate_groups,
            "reclaimable_bytes": total_reclaimable,
            "formatted_reclaimable": format_file_size(total_reclaimable),
            "duplicate_count": len(duplicate_groups)
        }


dedup_engine = StorageDeduplicationEngine()
