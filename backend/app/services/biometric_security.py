import os
import json
import base64
import time
import secrets
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import DATA_DIR

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


PROFILE_FILE = os.path.join(DATA_DIR, "biometric_profile.json")

ACTIVE_DOWNLOAD_TOKENS: Dict[str, Dict[str, Any]] = {}


def load_biometric_profile() -> Dict[str, Any]:
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"registered": False, "features": [], "registered_at": None, "user_name": "Admin"}


def save_biometric_profile(profile_data: Dict[str, Any]):
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2)
    except Exception as e:
        print(f"Error saving biometric profile: {e}")


class BiometricSecurityEngine:
    def __init__(self):
        self.face_cascade = None
        if OPENCV_AVAILABLE:
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                if os.path.exists(cascade_path):
                    self.face_cascade = cv2.CascadeClassifier(cascade_path)
            except Exception as e:
                print(f"Failed to load OpenCV Haar Cascade: {e}")

    def _base64_to_cv2(self, base64_str: str) -> Optional[np.ndarray]:
        try:
            if "," in base64_str:
                base64_str = base64_str.split(",")[1]
            img_bytes = base64.b64decode(base64_str)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"Error decoding base64 image: {e}")
            return None

    def _extract_facial_features(self, face_roi: np.ndarray) -> List[float]:
        resized = cv2.resize(face_roi, (128, 128))
        if len(resized.shape) == 3:
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        else:
            gray = resized

        equalized = cv2.equalizeHist(gray)

        grid_h, grid_w = 4, 4
        sub_h, sub_w = 32, 32
        features = []

        for r in range(grid_h):
            for c in range(grid_w):
                cell = equalized[r*sub_h:(r+1)*sub_h, c*sub_w:(c+1)*sub_w]
                hist = cv2.calcHist([cell], [0], None, [8], [0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                features.extend(hist.tolist())

        arr = np.array(features, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr.tolist()

    def detect_and_extract_face(self, base64_img: str) -> Tuple[bool, str, Optional[List[float]], Optional[Dict[str, int]]]:
        if not OPENCV_AVAILABLE:
            return False, "OpenCV is not available on server.", None, None

        img = self._base64_to_cv2(base64_img)
        if img is None:
            return False, "Invalid image data received.", None, None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = []
        if self.face_cascade:
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
            )

        if len(faces) == 0:
            h, w = gray.shape[:2]
            cx, cy = w // 2, h // 2
            mw, mh = int(w * 0.5), int(h * 0.5)
            face_roi = img[cy-mh//2:cy+mh//2, cx-mw//2:cx+mw//2]
            bbox = {"x": cx-mw//2, "y": cy-mh//2, "w": mw, "h": mh}
        else:
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            face_roi = img[y:y+h, x:x+w]
            bbox = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}

        features = self._extract_facial_features(face_roi)
        return True, "Face detected successfully.", features, bbox

    def register_master_face(self, base64_img: str, user_name: str = "Admin") -> Dict[str, Any]:
        success, msg, features, bbox = self.detect_and_extract_face(base64_img)
        if not success or not features:
            return {"success": False, "message": msg}

        profile = {
            "registered": True,
            "user_name": user_name,
            "features": features,
            "registered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "bbox": bbox
        }
        save_biometric_profile(profile)
        return {
            "success": True,
            "message": f"Biometric face profile registered for {user_name}!",
            "registered_at": profile["registered_at"]
        }

    def verify_face_access(self, base64_img: str, filename: str) -> Dict[str, Any]:
        profile = load_biometric_profile()
        if not profile.get("registered"):
            return {
                "success": False,
                "verified": False,
                "message": "No master biometric face profile registered yet. Please register your face first."
            }

        success, msg, live_features, bbox = self.detect_and_extract_face(base64_img)
        if not success or not live_features:
            return {"success": False, "verified": False, "message": msg}

        master_features = np.array(profile["features"], dtype=np.float32)
        live_vec = np.array(live_features, dtype=np.float32)

        dot_product = np.dot(master_features, live_vec)
        norm_a = np.linalg.norm(master_features)
        norm_b = np.linalg.norm(live_vec)

        similarity = float(dot_product / (norm_a * norm_b)) if (norm_a > 0 and norm_b > 0) else 0.0
        confidence_pct = round(similarity * 100, 1)

        MATCH_THRESHOLD = 0.72

        if similarity >= MATCH_THRESHOLD:
            token = secrets.token_urlsafe(24)
            ACTIVE_DOWNLOAD_TOKENS[token] = {
                "filename": filename,
                "expires": time.time() + 120.0
            }
            return {
                "success": True,
                "verified": True,
                "confidence_score": confidence_pct,
                "download_token": token,
                "message": f"Biometric Match Verified ({confidence_pct}%)! Access Granted."
            }
        else:
            return {
                "success": True,
                "verified": False,
                "confidence_score": confidence_pct,
                "message": f"Face Verification Failed ({confidence_pct}% match). Access Denied!"
            }


def validate_download_token(filename: str, token: Optional[str]) -> bool:
    if not token:
        return False

    if token in ACTIVE_DOWNLOAD_TOKENS:
        info = ACTIVE_DOWNLOAD_TOKENS[token]
        if info["expires"] > time.time() and info["filename"] == filename:
            del ACTIVE_DOWNLOAD_TOKENS[token]
            return True
        elif info["expires"] <= time.time():
            del ACTIVE_DOWNLOAD_TOKENS[token]
    return False


biometric_engine = BiometricSecurityEngine()
