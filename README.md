# ⚡ NexusShare AI
> **An Intelligent, Zero-Cloud Local Network File Sharing, AI Analytics & Biometric Security Platform.**

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-green.svg)
![React](https://img.shields.io/badge/React-19.0-61dafb.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-5.0-red.svg)
![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-1.9-orange.svg)
![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-purple.svg)

---

## 🌟 Overview & Key Vision

**NexusShare AI** transforms any standard local Wi-Fi or Ethernet network into a zero-cloud intelligent intranet. It allows users to rapidly share files peer-to-peer without third-party cloud infrastructure. 

The platform features machine learning for automated document classification, OpenCV computer vision for facial biometric download protection, real-time WebSocket network bandwidth telemetry, steganography image encryption, self-destructing ghost shares, and zero-cloud document Q&A.

---

## 🔥 8 Core Flagship Features

### 1. 🤖 ML Document Auto-Classifier & Topic Tagging
- **Text Extraction**: Parses text content from `.pdf` (using `pypdf`), `.docx` (using `python-docx`), `.txt`, `.md`, and source code files.
- **ML Engine**: Trained TF-IDF + `SGDClassifier` model across 7 document domains:
  - *Finance & Business*, *Legal & Contracts*, *Technology & Code*, *Medical & Healthcare*, *Academic & Research*, *Marketing & Sales*, *Personal & HR*.
- **Dynamic Tagging**: Extracts top N-gram key phrases as glowing tag badges (`#Invoice`, `#FastAPI`, `#Agreement`, `#Tax2026`).
- **AI Inspection Drawer**: View document text summaries, multi-domain probability breakdowns, and add custom tags.

### 2. 👁️ OpenCV Facial Biometric Download Security
- **OpenCV Computer Vision**: Processes live camera frames using `cv2.CascadeClassifier` (Haar Cascades) and extracts normalized 128-dimensional spatial histogram feature vectors.
- **Profile Enrolment**: Saves master biometric identity embeddings into `backend/app/data/biometric_profile.json`.
- **Match Authorization**: Computes Cosine Similarity between live webcam snapshots and registered profiles (>72% match threshold) to issue single-use short-lived download tokens.
- **Webcam Scanner Modal**: Includes target face bounding box guide, laser scanning beam animation, and live confidence score readouts.

### 3. ⚡ Real-Time Network WebSockets Telemetry
- **WebSocket Endpoint**: `/ws/network` streaming real-time network telemetry every second.
- **Speed & Resource Meters**: `psutil` network IO polling for live Download/Upload speeds (KB/s, MB/s), CPU %, and RAM %.
- **Connected Peer Map**: Tracks connected local Wi-Fi peer IP addresses, client browsers, and uptime.
- **Instant Event Dispatch**: Automatically dispatches WebSocket events on file uploads/deletions, keeping all connected devices in sync.

### 4. 💬 Zero-Cloud Local AI Document Q&A
- **Semantic Vector Search**: Splits document text into sentence-aware chunks and indexes them using TF-IDF vector search.
- **Document Q&A Assistant**: Ask questions directly to any uploaded PDF/Doc (e.g., *"What is the total payment due?"* or *"Summarize the payment terms"*).
- **100% Privacy**: Operates entirely offline without sending document contents to third-party LLM APIs.

### 5. 🔐 OpenCV Image Steganography Vault
- **Payload Embedding**: Encrypts and hides secret document or text payloads inside cover images (`.png` / `.jpg`) using OpenCV Least Significant Bit (LSB) steganography.
- **Decryption**: Recipients can extract and decrypt hidden payloads directly inside the app.

### 6. 📡 Intranet Peer Radar & Direct AirDrop Push
- **Visual Radar**: Interactive animated radar display showing active intranet peer nodes.
- **P2P AirDrop Push**: Click any peer node on the radar to send an instant file transfer prompt directly to their screen over WebSockets.

### 7. 🔥 Self-Destructing "Ghost Shares"
- **Automated Shredder**: Mark files as Ghost Shares to automatically zero-fill and shred them from disk after 1 download or upon TTL timer expiration.
- **Live WebSocket Notifications**: Broadcasts real-time alerts when ghost files expire.

### 8. 🧹 AI Smart Storage Deduplication
- **Duplicate Scanner**: Calculates SHA-256 hashes and content similarity across stored files.
- **Space Reclaimer**: Identifies redundant duplicate files, displays reclaimable storage space in MB/GB, and provides 1-click automated cleanup.

---

