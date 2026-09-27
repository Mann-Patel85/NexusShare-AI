import os
import shutil
import time
import asyncio
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Request, File, UploadFile, HTTPException, Query, WebSocket, WebSocketDisconnect, Body
from fastapi.responses import HTMLResponse, FileResponse

from app.core.config import (
    SHARED_DIR,
    FRONTEND_DIST,
    get_local_ip,
    format_file_size,
    get_file_category
)
from app.services.document_classifier import (
    classifier_engine,
    get_file_metadata,
    update_file_metadata,
    delete_file_metadata,
    load_all_metadata
)
from app.services.biometric_security import (
    biometric_engine,
    load_biometric_profile,
    validate_download_token
)
from app.services.websocket_manager import ws_manager
from app.services.document_qa import qa_engine
from app.services.steganography import stego_engine
from app.services.ghost_share import ghost_engine
from app.services.storage_dedup import dedup_engine

router = APIRouter()


# --- WEBSOCKET REAL-TIME NETWORK MONITORING ---

@router.websocket("/ws/network")
async def websocket_network_endpoint(websocket: WebSocket):
    client_ip = websocket.client.host if websocket.client else "127.0.0.1"
    user_agent = websocket.headers.get("user-agent", "Unknown Client")
    await ws_manager.connect(websocket, client_ip, user_agent)
    try:
        while True:
            expired = ghost_engine.cleanup_expired_ghosts(SHARED_DIR)
            if expired:
                for ef in expired:
                    await ws_manager.broadcast({
                        "type": "ghost_expired",
                        "filename": ef,
                        "message": f"Ghost Share '{ef}' has expired and was shredded."
                    })

            metrics = ws_manager.get_network_metrics()
            await websocket.send_json(metrics)
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


# --- SYSTEM INFO & FILE EXPLORER ---

@router.get("/api/info")
def get_system_info():
    local_ip = get_local_ip()
    bio_profile = load_biometric_profile()
    return {
        "app_name": "NexusShare AI",
        "version": "2.2.0",
        "local_ip": local_ip,
        "local_url": f"http://{local_ip}:8000",
        "shared_dir": os.path.abspath(SHARED_DIR),
        "biometric_registered": bio_profile.get("registered", False),
        "biometric_user": bio_profile.get("user_name", "Admin")
    }


@router.get("/api/files")
@router.get("/files")
def list_files(search: Optional[str] = Query(None)):
    if not os.path.exists(SHARED_DIR):
        os.makedirs(SHARED_DIR, exist_ok=True)
        return {"available_files": [], "files_details": [], "message": "Folder initialized."}

    filenames = os.listdir(SHARED_DIR)
    details = []

    for name in filenames:
        if search and search.lower() not in name.lower():
            continue

        filepath = os.path.join(SHARED_DIR, name)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            meta = get_file_metadata(name)
            
            details.append({
                "name": name,
                "size_bytes": stat.st_size,
                "formatted_size": format_file_size(stat.st_size),
                "modified_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                "category": get_file_category(name),
                "predicted_category": meta.get("predicted_category", "General"),
                "confidence_pct": f"{round(meta.get('confidence', 0.0) * 100, 1)}%",
                "tags": meta.get("tags", []),
                "summary": meta.get("summary", ""),
                "biometric_protected": meta.get("biometric_protected", False),
                "is_ghost_share": meta.get("is_ghost_share", False),
                "download_url": f"/api/download/{name}"
            })

    details.sort(key=lambda x: x["modified_time"], reverse=True)

    return {
        "available_files": [d["name"] for d in details],
        "files_details": details,
        "total_files": len(details)
    }


# --- UPLOAD & AI DOCUMENT CLASSIFICATION ---

@router.post("/api/upload")
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(SHARED_DIR, exist_ok=True)
    file_location = os.path.join(SHARED_DIR, file.filename)
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    stat = os.stat(file_location)
    classification = classifier_engine.classify(file_location, file.filename)
    
    update_file_metadata(file.filename, {
        "predicted_category": classification["predicted_category"],
        "confidence": classification["confidence"],
        "tags": classification["tags"],
        "summary": classification["summary"],
        "domain_scores": classification["domain_scores"],
        "biometric_protected": False,
        "is_ghost_share": False
    })

    asyncio.create_task(ws_manager.broadcast({
        "type": "file_uploaded",
        "filename": file.filename,
        "category": classification["predicted_category"],
        "tags": classification["tags"]
    }))

    return {
        "filename": file.filename,
        "size_bytes": stat.st_size,
        "formatted_size": format_file_size(stat.st_size),
        "predicted_category": classification["predicted_category"],
        "confidence_percentage": classification["confidence_percentage"],
        "tags": classification["tags"],
        "summary": classification["summary"],
        "message": "File uploaded and AI auto-tagged successfully!"
    }


@router.get("/api/files/{filename:path}/details")
def get_file_ml_details(filename: str):
    file_path = os.path.join(SHARED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    meta = get_file_metadata(filename)
    if not meta.get("domain_scores"):
        classification = classifier_engine.classify(file_path, filename)
        update_file_metadata(filename, classification)
        meta = get_file_metadata(filename)

    return {
        "filename": filename,
        "predicted_category": meta.get("predicted_category"),
        "confidence": meta.get("confidence"),
        "confidence_percentage": f"{round(meta.get('confidence', 0.0) * 100, 1)}%",
        "tags": meta.get("tags", []),
        "summary": meta.get("summary", ""),
        "domain_scores": meta.get("domain_scores", {}),
        "biometric_protected": meta.get("biometric_protected", False)
    }


@router.post("/api/files/{filename:path}/update-tags")
async def update_tags(filename: str, payload: Dict[str, Any] = Body(...)):
    new_tags = payload.get("tags", [])
    update_file_metadata(filename, {"tags": new_tags})
    
    asyncio.create_task(ws_manager.broadcast({
        "type": "file_updated",
        "filename": filename,
        "tags": new_tags
    }))
    return {"filename": filename, "tags": new_tags, "message": "Tags updated successfully."}


# --- ZERO-CLOUD AI DOCUMENT Q&A ---

@router.post("/api/files/{filename:path}/qa")
def ask_document_question(filename: str, payload: Dict[str, Any] = Body(...)):
    file_path = os.path.join(SHARED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    question = payload.get("question", "")
    if not question.strip():
        raise HTTPException(status_code=400, detail="Missing question text")

    result = qa_engine.answer_question(file_path, filename, question)
    return result


# --- OPENCV STEGANOGRAPHY VAULT ---

@router.post("/api/steganography/encode")
def encode_steganography(payload: Dict[str, Any] = Body(...)):
    cover_image = payload.get("image")
    secret_text = payload.get("secret")
    if not cover_image or not secret_text:
        raise HTTPException(status_code=400, detail="Missing image or secret payload")

    result = stego_engine.encode_text_into_image(cover_image, secret_text)
    return result


@router.post("/api/steganography/decode")
def decode_steganography(payload: Dict[str, Any] = Body(...)):
    stego_image = payload.get("image")
    if not stego_image:
        raise HTTPException(status_code=400, detail="Missing stego image data")

    result = stego_engine.decode_text_from_image(stego_image)
    return result


# --- INTRANET PEER RADAR AIRDROP PUSH ---

@router.post("/api/peers/push-file")
async def push_file_to_peer(payload: Dict[str, Any] = Body(...)):
    target_ip = payload.get("target_ip")
    filename = payload.get("filename")
    sender_ip = get_local_ip()

    await ws_manager.broadcast({
        "type": "p2p_file_push",
        "sender_ip": sender_ip,
        "target_ip": target_ip,
        "filename": filename,
        "message": f"Peer {sender_ip} wants to send you '{filename}'."
    })
    return {"status": "success", "message": f"P2P Push sent to {target_ip}"}


# --- SELF-DESTRUCTING GHOST SHARES ---

@router.post("/api/files/{filename:path}/toggle-ghost")
async def toggle_ghost_share(filename: str, payload: Dict[str, Any] = Body(...)):
    ttl_seconds = payload.get("ttl_seconds", 300)
    max_downloads = payload.get("max_downloads", 1)

    meta = get_file_metadata(filename)
    current_ghost = meta.get("is_ghost_share", False)

    if current_ghost:
        update_file_metadata(filename, {"is_ghost_share": False})
        asyncio.create_task(ws_manager.broadcast({"type": "file_updated", "filename": filename}))
        return {"filename": filename, "is_ghost_share": False, "message": "Ghost Share disabled."}
    else:
        res = ghost_engine.enable_ghost_share(filename, max_downloads, ttl_seconds)
        asyncio.create_task(ws_manager.broadcast({"type": "file_updated", "filename": filename}))
        return res


# --- AI SMART STORAGE DEDUPLICATION ---

@router.get("/api/analytics/deduplication")
def scan_deduplication():
    return dedup_engine.scan_for_duplicates(SHARED_DIR)


@router.post("/api/analytics/deduplicate-clean")
async def clean_deduplicates():
    scan_res = dedup_engine.scan_for_duplicates(SHARED_DIR)
    cleaned_files = []

    for group in scan_res.get("duplicate_groups", []):
        for dup in group["duplicates"]:
            path = dup["path"]
            if os.path.exists(path):
                os.remove(path)
                delete_file_metadata(dup["filename"])
                cleaned_files.append(dup["filename"])

    asyncio.create_task(ws_manager.broadcast({"type": "file_deleted", "message": "Cleaned duplicate files"}))
    return {
        "cleaned_count": len(cleaned_files),
        "cleaned_files": cleaned_files,
        "space_freed": scan_res.get("formatted_reclaimable", "0 B")
    }


# --- BIOMETRIC SECURITY ENDPOINTS ---

@router.get("/api/biometric/status")
def get_biometric_status():
    profile = load_biometric_profile()
    return {
        "registered": profile.get("registered", False),
        "user_name": profile.get("user_name", "Admin"),
        "registered_at": profile.get("registered_at")
    }


@router.post("/api/biometric/register")
def register_face(payload: Dict[str, Any] = Body(...)):
    base64_img = payload.get("image")
    user_name = payload.get("user_name", "Admin Master")
    if not base64_img:
        raise HTTPException(status_code=400, detail="Missing webcam image snapshot")

    result = biometric_engine.register_master_face(base64_img, user_name)
    return result


@router.post("/api/biometric/verify")
def verify_face_download(payload: Dict[str, Any] = Body(...)):
    base64_img = payload.get("image")
    filename = payload.get("filename")
    if not base64_img or not filename:
        raise HTTPException(status_code=400, detail="Missing image or filename")

    result = biometric_engine.verify_face_access(base64_img, filename)
    return result


@router.post("/api/files/{filename:path}/toggle-biometric")
async def toggle_biometric_protection(filename: str):
    meta = get_file_metadata(filename)
    new_state = not meta.get("biometric_protected", False)
    update_file_metadata(filename, {"biometric_protected": new_state})
    
    asyncio.create_task(ws_manager.broadcast({
        "type": "file_updated",
        "filename": filename,
        "biometric_protected": new_state
    }))

    return {
        "filename": filename,
        "biometric_protected": new_state,
        "message": f"Biometric security {'enabled' if new_state else 'disabled'} for {filename}."
    }


# --- FILE DOWNLOAD & DELETE ENDPOINTS ---

@router.get("/api/download/{filename:path}")
@router.get("/download/{filename:path}")
async def download_file(filename: str, token: Optional[str] = Query(None)):
    file_path = os.path.join(SHARED_DIR, filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    meta = get_file_metadata(filename)
    if meta.get("biometric_protected", False):
        if not validate_download_token(filename, token):
            raise HTTPException(
                status_code=403,
                detail="Biometric facial verification required to access this protected file."
            )

    response = FileResponse(path=file_path, filename=filename)

    shredded = ghost_engine.check_and_handle_download_destruct(filename, SHARED_DIR)
    if shredded:
        asyncio.create_task(ws_manager.broadcast({
            "type": "ghost_expired",
            "filename": filename,
            "message": f"Ghost Share '{filename}' was shredded immediately after download."
        }))

    return response


@router.delete("/api/files/{filename:path}")
async def delete_file(filename: str):
    file_path = os.path.join(SHARED_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        delete_file_metadata(filename)
        
        asyncio.create_task(ws_manager.broadcast({
            "type": "file_deleted",
            "filename": filename
        }))
        return {"filename": filename, "message": "File deleted successfully"}
    raise HTTPException(status_code=404, detail="File not found")


@router.get("/api/analytics")
def get_analytics():
    if not os.path.exists(SHARED_DIR):
        return {"total_files": 0, "total_bytes": 0, "formatted_total_space": "0 B"}
        
    total_bytes = 0
    total_files = 0
    categories = {}
    ai_categories = {}
    all_tags = {}

    all_meta = load_all_metadata()

    for name in os.listdir(SHARED_DIR):
        filepath = os.path.join(SHARED_DIR, name)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath)
            total_bytes += size
            total_files += 1
            cat = get_file_category(name)
            categories[cat] = categories.get(cat, 0) + 1
            
            meta = all_meta.get(name, {})
            pred_cat = meta.get("predicted_category", "General")
            ai_categories[pred_cat] = ai_categories.get(pred_cat, 0) + 1
            
            for t in meta.get("tags", []):
                all_tags[t] = all_tags.get(t, 0) + 1

    return {
        "total_files": total_files,
        "total_bytes": total_bytes,
        "formatted_total_space": format_file_size(total_bytes),
        "categories": categories,
        "ai_categories": ai_categories,
        "popular_tags": sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10],
        "server_ip": get_local_ip()
    }
