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

## 🏗️ Modular Project Architecture

```
NexusShare-AI/
├── backend/                  # Production Modular FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py     # Central REST & WebSocket Endpoint Routes
│   │   ├── core/
│   │   │   └── config.py     # Path Constants, IP Discovery, & Utilities
│   │   ├── services/         # Decoupled Feature & Intelligence Engines
│   │   │   ├── document_classifier.py  # ML Text Classifier & Auto-Tagging
│   │   │   ├── biometric_security.py   # OpenCV Facial Recognition
│   │   │   ├── websocket_manager.py    # Live Telemetry & WebSockets
│   │   │   ├── document_qa.py         # Zero-Cloud AI Document Q&A
│   │   │   ├── steganography.py       # OpenCV Image Steganography Vault
│   │   │   ├── ghost_share.py         # Self-Destruct Ghost Shares
│   │   │   └── storage_dedup.py       # AI Smart Storage Deduplication
│   │   └── data/             # Persistent JSON Data Records
│   │       ├── file_metadata.json
│   │       ├── biometric_profile.json
│   │       └── ghost_shares.json
│   ├── main.py               # Main ASGI Server Entry Point
│   └── shared_files/         # Intranet File Storage Directory
│
├── frontend/                 # React 19 + Vite Single Page App
│   ├── src/
│   │   ├── App.jsx           # Glassmorphic UI Dashboard & Modals
│   │   └── index.css         # Dark Mode Glassmorphism & Animations
│   ├── dist/                 # Production Compiled Web Assets
│   └── package.json
│
├── venv/                     # Python Virtual Environment
├── README.md                 # Project Overview & Feature Guide
├── PROJECT_ANALYSIS.txt      # Architecture Reference & Analysis
└── .gitignore                # Version Control Exclusion Rules
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/info` | Returns local intranet IP, connection URL, and biometric status |
| `GET` | `/api/files` | Lists all shared network files with ML tags & security flags |
| `POST` | `/api/upload` | Uploads file, extracts text, and runs ML classification & auto-tagging |
| `POST` | `/api/files/{filename}/qa` | Zero-Cloud AI Q&A search over document content |
| `POST` | `/api/files/{filename}/toggle-biometric` | Toggles OpenCV facial recognition lock on file |
| `POST` | `/api/files/{filename}/toggle-ghost` | Toggles self-destruct Ghost Share rules |
| `POST` | `/api/biometric/register` | Enrolls master facial recognition snapshot |
| `POST` | `/api/biometric/verify` | Verifies camera snapshot and issues download token |
| `GET` | `/api/download/{filename}` | Secure file download endpoint |
| `POST` | `/api/steganography/encode` | Hides secret payload inside cover image pixels |
| `POST` | `/api/steganography/decode` | Extracts secret payload from stego image |
| `POST` | `/api/peers/push-file` | Sends P2P AirDrop push notification to intranet peer |
| `GET` | `/api/analytics/deduplication` | Scans for duplicate files and reclaimable space |
| `POST` | `/api/analytics/deduplicate-clean` | Cleans duplicate files and frees disk space |
| `WS` | `/ws/network` | Live WebSocket telemetry stream for bandwidth & peers |

---

## 🚀 How to Run

### 1. Start the Production Backend Server
```powershell
# Activate Virtual Environment (Windows PowerShell)
.\venv\Scripts\activate

# Start Server (from project root)
python backend/main.py
```
- Local Browser: `http://localhost:8000`
- Intranet Devices: `http://<your-local-ip>:8000`

### 2. Frontend Build (Optional for UI Editing)
```powershell
cd frontend
npm run build
```
Compiled static assets are automatically served by FastAPI at `http://localhost:8000`.
