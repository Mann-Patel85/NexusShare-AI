import os
import base64
import numpy as np
from typing import Dict, Any, Optional, Tuple

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


MAGIC_HEADER = "NEXUS_STEGO_V1::"


class SteganographyEngine:
    def __init__(self):
        pass

    def encode_text_into_image(self, base64_cover_img: str, secret_payload: str) -> Dict[str, Any]:
        if not OPENCV_AVAILABLE:
            return {"success": False, "message": "OpenCV is not available."}

        try:
            if "," in base64_cover_img:
                base64_cover_img = base64_cover_img.split(",")[1]

            img_bytes = base64.b64decode(base64_cover_img)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return {"success": False, "message": "Invalid cover image data."}

            full_payload = MAGIC_HEADER + secret_payload + "::END"
            payload_bytes = full_payload.encode('utf-8')
            
            binary_secret = ''.join(format(b, '08b') for b in payload_bytes)
            secret_len = len(binary_secret)

            h, w, c = img.shape
            max_capacity = h * w * c

            if secret_len > max_capacity:
                return {
                    "success": False,
                    "message": f"Payload too large ({secret_len} bits) for image capacity ({max_capacity} bits)."
                }

            flat_img = img.flatten()
            for i in range(secret_len):
                bit = int(binary_secret[i])
                flat_img[i] = (flat_img[i] & 0xFE) | bit

            stego_img = flat_img.reshape((h, w, c))

            _, buffer = cv2.imencode('.png', stego_img)
            stego_base64 = "data:image/png;base64," + base64.b64encode(buffer).decode('utf-8')

            return {
                "success": True,
                "stego_image_base64": stego_base64,
                "bits_embedded": secret_len,
                "message": "Secret payload encrypted and hidden inside cover image successfully!"
            }

        except Exception as e:
            print(f"Steganography encode error: {e}")
            return {"success": False, "message": f"Encoding error: {str(e)}"}

    def decode_text_from_image(self, base64_stego_img: str) -> Dict[str, Any]:
        if not OPENCV_AVAILABLE:
            return {"success": False, "message": "OpenCV is not available."}

        try:
            if "," in base64_stego_img:
                base64_stego_img = base64_stego_img.split(",")[1]

            img_bytes = base64.b64decode(base64_stego_img)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return {"success": False, "message": "Invalid stego image data."}

            flat_img = img.flatten()
            
            bits = [str(flat_img[i] & 1) for i in range(min(len(flat_img), 50000))]
            binary_str = "".join(bits)

            bytes_list = []
            for i in range(0, len(binary_str) - 7, 8):
                byte = int(binary_str[i:i+8], 2)
                bytes_list.append(byte)
                
                decoded_so_far = bytes(bytes_list).decode('utf-8', errors='ignore')
                if "::END" in decoded_so_far:
                    break

            decoded_str = bytes(bytes_list).decode('utf-8', errors='ignore')

            if MAGIC_HEADER in decoded_str:
                secret_payload = decoded_str.split(MAGIC_HEADER)[1].split("::END")[0]
                return {
                    "success": True,
                    "secret_payload": secret_payload,
                    "message": "Steganographic secret decrypted successfully!"
                }
            else:
                return {
                    "success": False,
                    "message": "No steganographic secret found in this image."
                }

        except Exception as e:
            print(f"Steganography decode error: {e}")
            return {"success": False, "message": f"Decoding error: {str(e)}"}


stego_engine = SteganographyEngine()
