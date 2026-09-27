import React, { useState, useEffect, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  HardDrive,
  Search,
  Download,
  Trash2,
  Copy,
  Check,
  RefreshCw,
  Wifi,
  Shield,
  Tag,
  Image as ImageIcon,
  Video as VideoIcon,
  Music as MusicIcon,
  Archive as ArchiveIcon,
  Code as CodeIcon,
  File as GenericFileIcon,
  Share2,
  Lock,
  Unlock,
  Camera,
  UserCheck,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Users,
  Cpu,
  Eye,
  X,
  Sparkles,
  Zap,
  MessageSquare,
  Flame,
  Radio,
  EyeOff,
  Database,
  Send,
  HelpCircle,
  Key
} from 'lucide-react';

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`;

const WS_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'ws://localhost:8000'
  : `ws://${window.location.hostname}:8000`;

export default function App() {
  // Main Data States
  const [files, setFiles] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  // Upload States
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [statusMsg, setStatusMsg] = useState('');

  // Search & Filter
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCat, setSelectedCat] = useState('all');
  const [copiedIp, setCopiedIp] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  // AI ML Document Analysis Drawer
  const [selectedMlFile, setSelectedMlFile] = useState(null);
  const [mlDetails, setMlDetails] = useState(null);
  const [newTagInput, setNewTagInput] = useState('');

  // Biometric Facial Security Modal
  const [cameraModalOpen, setCameraModalOpen] = useState(false);
  const [cameraMode, setCameraMode] = useState('verify');
  const [targetDownloadFile, setTargetDownloadFile] = useState(null);
  const [verifyingFace, setVerifyingFace] = useState(false);
  const [faceResult, setFaceResult] = useState(null);

  // WebSockets & Telemetry
  const [wsConnected, setWsConnected] = useState(false);
  const [telemetry, setTelemetry] = useState({
    download_speed: '0.0 KB/s',
    upload_speed: '0.0 KB/s',
    download_kbps: 0,
    upload_kbps: 0,
    total_sent_mb: 0,
    total_recv_mb: 0,
    cpu_usage_pct: 0,
    ram_usage_pct: 0,
    connected_peers_count: 0,
    peers: []
  });

  // Unique Feature 1: Zero-Cloud AI Document Q&A
  const [qaModalOpen, setQaModalOpen] = useState(false);
  const [qaFile, setQaFile] = useState(null);
  const [qaInput, setQaInput] = useState('');
  const [qaHistory, setQaHistory] = useState([]);
  const [qaLoading, setQaLoading] = useState(false);

  // Unique Feature 2: OpenCV Steganography Vault
  const [stegoModalOpen, setStegoModalOpen] = useState(false);
  const [stegoMode, setStegoMode] = useState('encode'); // 'encode' or 'decode'
  const [stegoCoverImg, setStegoCoverImg] = useState(null);
  const [stegoSecretText, setStegoSecretText] = useState('');
  const [stegoResult, setStegoResult] = useState(null);

  // Unique Feature 5: Storage Deduplication
  const [dedupScan, setDedupScan] = useState(null);
  const [cleaningDedup, setCleaningDedup] = useState(false);

  const fileInputRef = useRef(null);
  const stegoFileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);

  // Fetch Core Data
  const fetchFiles = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/files`);
      const data = await res.json();
      setFiles(data.files_details || []);
    } catch (err) {
      console.error('Failed to fetch files:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/analytics`);
      const data = await res.json();
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    }
  };

  const fetchSystemInfo = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/info`);
      const data = await res.json();
      setSystemInfo(data);
    } catch (err) {
      console.error('Failed to fetch system info:', err);
    }
  };

  const fetchDedupScan = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/analytics/deduplication`);
      const data = await res.json();
      setDedupScan(data);
    } catch (err) {
      console.error('Failed to fetch dedup scan:', err);
    }
  };

  useEffect(() => {
    fetchFiles();
    fetchAnalytics();
    fetchSystemInfo();
    fetchDedupScan();

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`${WS_BASE}/ws/network`);
        wsRef.current = ws;

        ws.onopen = () => setWsConnected(true);
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'network_telemetry') {
              setTelemetry(data);
            } else if (['file_uploaded', 'file_deleted', 'file_updated', 'ghost_expired'].includes(data.type)) {
              fetchFiles();
              fetchAnalytics();
              fetchDedupScan();
              if (data.message) setStatusMsg(data.message);
            }
          } catch (e) {
            console.error('WS parse error', e);
          }
        };

        ws.onclose = () => {
          setWsConnected(false);
          setTimeout(connectWebSocket, 3000);
        };
      } catch (err) {
        console.error('WebSocket setup error:', err);
      }
    };

    connectWebSocket();
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, []);

  // Upload File Handler
  const handleUpload = async (file) => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(20);
    setStatusMsg(`Analyzing & Auto-Tagging ${file.name}...`);

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadProgress(60);
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        setUploadProgress(100);
        const data = await res.json();
        setStatusMsg(`Success: ${data.filename} auto-tagged as #${data.predicted_category}!`);
        setTimeout(() => setUploadProgress(0), 1200);
        fetchFiles();
        fetchAnalytics();
        fetchDedupScan();
      }
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) return;

    try {
      const res = await fetch(`${API_BASE}/api/files/${encodeURIComponent(filename)}`, { method: 'DELETE' });
      if (res.ok) {
        setStatusMsg(`Deleted ${filename}`);
        fetchFiles();
        fetchAnalytics();
        fetchDedupScan();
      }
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  const handleToggleBiometric = async (filename) => {
    try {
      const res = await fetch(`${API_BASE}/api/files/${encodeURIComponent(filename)}/toggle-biometric`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setStatusMsg(data.message);
        fetchFiles();
      }
    } catch (err) {
      console.error('Toggle biometric error:', err);
    }
  };

  // Feature 4: Toggle Ghost Share Self-Destruct Mode
  const handleToggleGhostShare = async (filename) => {
    try {
      const res = await fetch(`${API_BASE}/api/files/${encodeURIComponent(filename)}/toggle-ghost`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_downloads: 1, ttl_seconds: 300 }),
      });
      if (res.ok) {
        const data = await res.json();
        setStatusMsg(data.message || 'Ghost Share toggled');
        fetchFiles();
      }
    } catch (err) {
      console.error('Toggle Ghost Share error:', err);
    }
  };

  // Feature 1: Ask Question about Document
  const handleAskDocumentQuestion = async () => {
    if (!qaInput.trim() || !qaFile) return;
    const qText = qaInput.trim();
    setQaInput('');

    setQaHistory(prev => [...prev, { sender: 'user', text: qText }]);
    setQaLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/files/${encodeURIComponent(qaFile)}/qa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: qText }),
      });
      const data = await res.json();
      setQaHistory(prev => [
        ...prev,
        { sender: 'bot', text: data.answer, confidence: data.confidence_percentage, snippets: data.relevant_snippets }
      ]);
    } catch (err) {
      console.error('QA Error:', err);
      setQaHistory(prev => [...prev, { sender: 'bot', text: 'Error searching document content.' }]);
    } finally {
      setQaLoading(false);
    }
  };

  // Feature 2: Steganography Encode / Decode
  const handleRunSteganography = async () => {
    if (!stegoCoverImg) return;
    setStegoResult(null);

    try {
      if (stegoMode === 'encode') {
        const res = await fetch(`${API_BASE}/api/steganography/encode`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: stegoCoverImg, secret: stegoSecretText }),
        });
        const data = await res.json();
        setStegoResult(data);
      } else {
        const res = await fetch(`${API_BASE}/api/steganography/decode`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: stegoCoverImg }),
        });
        const data = await res.json();
        setStegoResult(data);
      }
    } catch (err) {
      console.error('Stego Error:', err);
      setStegoResult({ success: false, message: 'Steganography request failed.' });
    }
  };

  // Feature 3: AirDrop File Push to Peer Radar Node
  const handlePushFileToPeer = async (peerIp, filename) => {
    try {
      const res = await fetch(`${API_BASE}/api/peers/push-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_ip: peerIp, filename: filename }),
      });
      const data = await res.json();
      setStatusMsg(`P2P AirDrop push sent to peer ${peerIp}!`);
    } catch (err) {
      console.error('AirDrop error:', err);
    }
  };

  // Feature 5: Clean Storage Deduplicates
  const handleCleanDuplicates = async () => {
    setCleaningDedup(true);
    try {
      const res = await fetch(`${API_BASE}/api/analytics/deduplicate-clean`, { method: 'POST' });
      const data = await res.json();
      setStatusMsg(`Freed ${data.space_freed} by removing ${data.cleaned_count} duplicate files!`);
      fetchFiles();
      fetchAnalytics();
      fetchDedupScan();
    } catch (err) {
      console.error('Deduplicate clean error:', err);
    } finally {
      setCleaningDedup(false);
    }
  };

  // Download Handler with Biometric Protection check
  const handleInitiateDownload = (file) => {
    if (file.biometric_protected) {
      setTargetDownloadFile(file.name);
      setCameraMode('verify');
      setFaceResult(null);
      setCameraModalOpen(true);
    } else {
      window.location.href = `${API_BASE}${file.download_url}`;
    }
  };

  // Camera Webcam logic
  useEffect(() => {
    let stream = null;
    if (cameraModalOpen) {
      navigator.mediaDevices?.getUserMedia({ video: { width: 640, height: 480 } })
        .then((s) => {
          stream = s;
          if (videoRef.current) videoRef.current.srcObject = s;
        })
        .catch((err) => {
          setFaceResult({ success: false, message: 'Camera access denied or unavailable.' });
        });
    }
    return () => { if (stream) stream.getTracks().forEach((t) => t.stop()); };
  }, [cameraModalOpen]);

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return null;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.85);
  };

  const handleRunBiometricAction = async () => {
    const base64Img = captureFrame();
    if (!base64Img) return;

    setVerifyingFace(true);
    setFaceResult(null);

    try {
      if (cameraMode === 'register') {
        const res = await fetch(`${API_BASE}/api/biometric/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: base64Img, user_name: 'Master User' }),
        });
        const data = await res.json();
        setFaceResult(data);
        if (data.success) fetchSystemInfo();
      } else {
        const res = await fetch(`${API_BASE}/api/biometric/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: base64Img, filename: targetDownloadFile }),
        });
        const data = await res.json();
        setFaceResult(data);

        if (data.verified && data.download_token) {
          setTimeout(() => {
            setCameraModalOpen(false);
            window.location.href = `${API_BASE}/api/download/${encodeURIComponent(targetDownloadFile)}?token=${data.download_token}`;
          }, 1200);
        }
      }
    } catch (err) {
      console.error('Biometric API error:', err);
    } finally {
      setVerifyingFace(false);
    }
  };

  const copyLocalUrl = () => {
    if (systemInfo?.local_url) {
      navigator.clipboard.writeText(systemInfo.local_url);
      setCopiedIp(true);
      setTimeout(() => setCopiedIp(false), 2000);
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'image': return <ImageIcon className="w-4 h-4 text-purple-400" />;
      case 'video': return <VideoIcon className="w-4 h-4 text-rose-400" />;
      case 'audio': return <MusicIcon className="w-4 h-4 text-amber-400" />;
      case 'archive': return <ArchiveIcon className="w-4 h-4 text-teal-400" />;
      case 'code': return <CodeIcon className="w-4 h-4 text-emerald-400" />;
      case 'document': return <FileText className="w-4 h-4 text-blue-400" />;
      default: return <GenericFileIcon className="w-4 h-4 text-slate-400" />;
    }
  };

  const filteredFiles = files.filter(f => {
    const matchesSearch = f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (f.tags && f.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase())));
    const matchesCategory = selectedCat === 'all' || f.category === selectedCat || f.predicted_category === selectedCat;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="app-container">
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Header Bar */}
      <header className="glass-card app-header">
        <div className="brand-title">
          <Share2 className="w-8 h-8 text-blue-400" />
          <span>NexusShare AI</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div className="ws-status-indicator">
            <div className={`pulse-ws-dot ${wsConnected ? '' : 'offline'}`} style={{ background: wsConnected ? '#10b981' : '#f43f5e' }} />
            <span>{wsConnected ? 'WebSocket Live Telemetry' : 'Connecting WS...'}</span>
          </div>

          <div className="network-badge">
            <Wifi size={16} />
            <span>Intranet Online</span>
          </div>

          {systemInfo && (
            <div className="ip-sharing-pill">
              <span>Share: <strong>{systemInfo.local_url}</strong></span>
              <button className="btn-copy" onClick={copyLocalUrl} title="Copy intranet share link">
                {copiedIp ? <Check size={14} /> : <Copy size={14} />}
                <span>{copiedIp ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Grid Dashboard */}
      <div className="dashboard-grid">
        {/* Left Column: Dropzone & File List */}
        <div>
          <div
            className={`glass-card drop-zone ${isDragOver ? 'active' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(e) => { e.preventDefault(); setIsDragOver(false); e.dataTransfer.files?.[0] && handleUpload(e.dataTransfer.files[0]); }}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
            />

            <div className="drop-icon-glow">
              <UploadCloud size={32} />
            </div>

            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
              <span>Drag & Drop Network Files</span>
              <Sparkles className="w-4 h-4 text-purple-400" />
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Automatic ML text classification, Q&A indexing, and topic auto-tagging
            </p>

            {uploading && (
              <div className="progress-bar-container">
                <div className="progress-bar-fill" style={{ width: `${uploadProgress}%` }} />
              </div>
            )}

            {statusMsg && (
              <p style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: '#60a5fa' }}>
                {statusMsg}
              </p>
            )}
          </div>

          {/* Search Toolbar */}
          <div className="toolbar" style={{ marginTop: '2rem' }}>
            <div className="search-wrapper">
              <Search className="search-icon" size={18} />
              <input
                type="text"
                className="search-input"
                placeholder="Search files by name, AI tags, or category..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <button
              className="btn-icon"
              onClick={() => { fetchFiles(); fetchAnalytics(); fetchDedupScan(); }}
              title="Refresh files"
            >
              <RefreshCw size={18} />
            </button>
          </div>

          {/* Category Filter Pills */}
          <div className="category-pills">
            {['all', 'document', 'image', 'video', 'audio', 'archive', 'code', 'other'].map((cat) => (
              <button
                key={cat}
                className={`cat-pill ${selectedCat === cat ? 'active' : ''}`}
                onClick={() => setSelectedCat(cat)}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            ))}
          </div>

          {/* File Explorer Table */}
          <div className="glass-card file-list-container" style={{ marginTop: '1.5rem' }}>
            {loading ? (
              <div className="empty-state">
                <RefreshCw size={24} className="animate-spin" style={{ margin: '0 auto 1rem' }} />
                <p>Scanning network files & indexing AI metadata...</p>
              </div>
            ) : filteredFiles.length === 0 ? (
              <div className="empty-state">
                <GenericFileIcon size={40} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
                <p>No files match your search query.</p>
              </div>
            ) : (
              <table className="file-table">
                <thead>
                  <tr>
                    <th>File & AI Tags</th>
                    <th>ML Domain</th>
                    <th>Size</th>
                    <th>Security</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFiles.map((file) => (
                    <tr key={file.name}>
                      <td>
                        <div className="file-name-cell" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.25rem' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            {getCategoryIcon(file.category)}
                            <span style={{ fontWeight: 600 }} title={file.name}>{file.name}</span>
                            {file.is_ghost_share && (
                              <span className="badge-ghost" title="Ghost Share: Auto-destructs after download">
                                <Flame size={12} />
                                <span>Ghost</span>
                              </span>
                            )}
                          </div>

                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.2rem', marginTop: '0.2rem' }}>
                            {file.tags && file.tags.map((tag, idx) => (
                              <span key={idx} className="ai-tag-pill">#{tag}</span>
                            ))}
                          </div>
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                          <span className={`badge-cat badge-${file.category}`}>
                            {file.predicted_category || file.category}
                          </span>
                          <span className="confidence-badge">
                            <Sparkles size={10} />
                            <span>{file.confidence_pct || '85.0%'}</span>
                          </span>
                        </div>
                      </td>
                      <td>{file.formatted_size}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.35rem' }}>
                          <button
                            className={`btn-lock ${file.biometric_protected ? 'locked' : 'unlocked'}`}
                            onClick={() => handleToggleBiometric(file.name)}
                            title={file.biometric_protected ? 'Facial Biometric Verification ENABLED' : 'Enable Facial Biometric Lock'}
                          >
                            {file.biometric_protected ? <Lock size={14} /> : <Unlock size={14} />}
                          </button>

                          <button
                            className={`btn-lock ${file.is_ghost_share ? 'locked' : 'unlocked'}`}
                            style={{ borderColor: file.is_ghost_share ? '#f43f5e' : '' }}
                            onClick={() => handleToggleGhostShare(file.name)}
                            title={file.is_ghost_share ? 'Self-Destruct Ghost Share ACTIVE' : 'Enable Ghost Share Self-Destruct'}
                          >
                            <Flame size={14} className={file.is_ghost_share ? 'text-rose-400' : ''} />
                          </button>
                        </div>
                      </td>
                      <td>
                        <div className="action-btns" style={{ justifyContent: 'flex-end' }}>
                          {/* Feature 1: Ask AI Question Button */}
                          <button
                            className="btn-icon text-purple-400"
                            onClick={() => {
                              setQaFile(file.name);
                              setQaHistory([]);
                              setQaModalOpen(true);
                            }}
                            title="Zero-Cloud AI Document Q&A"
                          >
                            <MessageSquare size={16} />
                          </button>

                          <button
                            className="btn-icon"
                            onClick={() => {
                              setSelectedMlFile(file.name);
                              fetch(`${API_BASE}/api/files/${encodeURIComponent(file.name)}/details`)
                                .then(r => r.json()).then(setMlDetails);
                            }}
                            title="Inspect ML Details"
                          >
                            <Eye size={16} />
                          </button>

                          <button
                            className="btn-icon"
                            onClick={() => handleInitiateDownload(file)}
                            title={file.biometric_protected ? 'Facial Verification Required' : 'Download file'}
                          >
                            <Download size={16} />
                          </button>

                          <button
                            className="btn-icon delete"
                            onClick={() => handleDelete(file.name)}
                            title="Delete file"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Right Column: Unique Flagship Features Dashboard */}
        <div className="stats-panel">
          {/* Feature 3: Intranet Peer Radar & AirDrop Direct Push */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '1rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Radio size={18} className="text-sky-400" />
                <span>Intranet Peer Radar</span>
              </span>
              <span style={{ fontSize: '0.75rem', color: '#38bdf8' }}>{telemetry.connected_peers_count} Peers</span>
            </h4>

            {/* Visual Radar Scanner */}
            <div className="peer-radar-container">
              <div className="radar-circle c1" />
              <div className="radar-circle c2" />
              <div className="radar-circle c3" />
              <div className="radar-sweep" />

              {/* Render Connected Nodes on Radar */}
              {telemetry.peers && telemetry.peers.map((peer, idx) => {
                const angle = (idx + 1) * (360 / (telemetry.peers.length || 1));
                const rad = (angle * Math.PI) / 180;
                const topVal = 50 + 35 * Math.sin(rad);
                const leftVal = 50 + 35 * Math.cos(rad);
                return (
                  <div
                    key={idx}
                    className="radar-node"
                    style={{ top: `${topVal}%`, left: `${leftVal}%` }}
                    title={`Peer Node: ${peer.ip} | Click to AirDrop Push`}
                    onClick={() => {
                      if (files.length > 0) {
                        handlePushFileToPeer(peer.ip, files[0].name);
                      }
                    }}
                  />
                );
              })}
            </div>

            {/* Speed Telemetry Meter */}
            <div className="speed-meter-grid">
              <div className="speed-card">
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Download</div>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: '#34d399' }}>{telemetry.download_speed}</div>
              </div>

              <div className="speed-card">
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Upload</div>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: '#60a5fa' }}>{telemetry.upload_speed}</div>
              </div>
            </div>
          </div>

          {/* Feature 2: OpenCV Steganography Vault */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', fontSize: '1rem' }}>
              <EyeOff size={18} className="text-purple-400" />
              <span>OpenCV Steganography Vault</span>
            </h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
              Hide confidential document payload inside cover image pixels.
            </p>

            <button
              className="cat-pill active"
              style={{ width: '100%', padding: '0.55rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
              onClick={() => { setStegoResult(null); setStegoModalOpen(true); }}
            >
              <Key size={15} />
              <span>Open Steganography Vault</span>
            </button>
          </div>

          {/* Feature 5: AI Smart Storage Deduplication */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem', fontSize: '1rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <HardDrive size={18} className="text-emerald-400" />
                <span>Storage Deduplication</span>
              </span>
              <span style={{ fontSize: '0.8rem', color: '#34d399' }}>{dedupScan?.formatted_reclaimable || '0 B'}</span>
            </h4>

            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
              {dedupScan?.duplicate_count > 0 ? (
                <span style={{ color: '#fb7185' }}>
                  Found {dedupScan.duplicate_count} duplicate group(s). Free up {dedupScan.formatted_reclaimable}!
                </span>
              ) : (
                <span>No duplicate files detected. Intranet storage optimized.</span>
              )}
            </div>

            {dedupScan?.duplicate_count > 0 && (
              <button
                className="cat-pill active"
                style={{ width: '100%', padding: '0.55rem', background: 'linear-gradient(90deg, #10b981, #059669)', border: 'none' }}
                onClick={handleCleanDuplicates}
                disabled={cleaningDedup}
              >
                {cleaningDedup ? 'Cleaning Storage...' : `Smart Deduplicate & Free ${dedupScan.formatted_reclaimable}`}
              </button>
            )}
          </div>

          {/* OpenCV Facial Biometric Status */}
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', fontSize: '1rem' }}>
              <Shield size={18} className="text-rose-400" />
              <span>Biometric Facial Engine</span>
            </h4>

            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
              {systemInfo?.biometric_registered ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#34d399' }}>
                  <UserCheck size={16} />
                  <span>Master Profile Enrolled ({systemInfo.biometric_user})</span>
                </div>
              ) : (
                <span style={{ color: '#fb7185' }}>No facial profile enrolled. Click below to register face.</span>
              )}
            </div>

            <button
              className="cat-pill active"
              style={{ width: '100%', padding: '0.55rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
              onClick={() => { setCameraMode('register'); setFaceResult(null); setCameraModalOpen(true); }}
            >
              <Camera size={15} />
              <span>{systemInfo?.biometric_registered ? 'Update Facial Snapshot' : 'Enroll Facial ID'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* MODAL 1: Zero-Cloud AI Document Q&A Modal */}
      {qaModalOpen && (
        <div className="modal-overlay" onClick={() => setQaModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setQaModalOpen(false)}
              style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
            >
              <X size={20} />
            </button>

            <h3 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <MessageSquare className="text-purple-400" size={20} />
              <span>Zero-Cloud AI Document Assistant</span>
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Ask questions about <strong style={{ color: 'var(--text-primary)' }}>{qaFile}</strong>
            </p>

            <div className="qa-chat-box">
              {qaHistory.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem 1rem', fontSize: '0.85rem' }}>
                  <HelpCircle size={28} style={{ margin: '0 auto 0.5rem', opacity: 0.5 }} />
                  <p>Ask anything about this document! (e.g., "Summarize payment terms", "What is the total due?")</p>
                </div>
              ) : (
                qaHistory.map((m, idx) => (
                  <div key={idx} className={`qa-msg ${m.sender}`}>
                    <div>{m.text}</div>
                    {m.confidence && (
                      <div style={{ fontSize: '0.7rem', color: '#6ee7b7', marginTop: '0.35rem' }}>
                        Match Confidence: {m.confidence}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                placeholder="Ask a question about document content..."
                className="search-input"
                value={qaInput}
                onChange={(e) => setQaInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAskDocumentQuestion()}
              />
              <button className="cat-pill active" style={{ padding: '0.6rem 1.25rem' }} onClick={handleAskDocumentQuestion} disabled={qaLoading}>
                {qaLoading ? 'Searching...' : <Send size={16} />}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: OpenCV Steganography Vault Modal */}
      {stegoModalOpen && (
        <div className="modal-overlay" onClick={() => setStegoModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setStegoModalOpen(false)}
              style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
            >
              <X size={20} />
            </button>

            <h3 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <EyeOff className="text-purple-400" size={20} />
              <span>OpenCV Steganography Image Vault</span>
            </h3>

            <div className="category-pills" style={{ margin: '1rem 0' }}>
              <button className={`cat-pill ${stegoMode === 'encode' ? 'active' : ''}`} onClick={() => setStegoMode('encode')}>
                Hide Secret Payload (Encode)
              </button>
              <button className={`cat-pill ${stegoMode === 'decode' ? 'active' : ''}`} onClick={() => setStegoMode('decode')}>
                Extract Secret Payload (Decode)
              </button>
            </div>

            <input
              type="file"
              accept="image/*"
              ref={stegoFileInputRef}
              style={{ display: 'none' }}
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) {
                  const reader = new FileReader();
                  reader.onload = (ev) => setStegoCoverImg(ev.target.result);
                  reader.readAsDataURL(f);
                }
              }}
            />

            <button
              className="cat-pill"
              style={{ width: '100%', padding: '0.75rem', marginBottom: '1rem', borderStyle: 'dashed' }}
              onClick={() => stegoFileInputRef.current?.click()}
            >
              {stegoCoverImg ? 'Image Selected!' : 'Select Image File (.png / .jpg)'}
            </button>

            {stegoMode === 'encode' && (
              <textarea
                placeholder="Enter confidential secret payload text to hide inside image..."
                className="search-input"
                style={{ height: '80px', padding: '0.75rem', marginBottom: '1rem', resize: 'none' }}
                value={stegoSecretText}
                onChange={(e) => setStegoSecretText(e.target.value)}
              />
            )}

            {stegoResult && (
              <div style={{ padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem', background: stegoResult.success ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)', color: stegoResult.success ? '#6ee7b7' : '#fca5a5' }}>
                {stegoResult.message}
                {stegoResult.secret_payload && (
                  <div style={{ marginTop: '0.5rem', fontWeight: 600, background: '#020617', padding: '0.5rem', borderRadius: '4px' }}>
                    Decrypted Payload: "{stegoResult.secret_payload}"
                  </div>
                )}
                {stegoResult.stego_image_base64 && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <a href={stegoResult.stego_image_base64} download="stego_vault_image.png" className="btn-icon" style={{ textDecoration: 'none', display: 'inline-flex', gap: '0.4rem' }}>
                      <Download size={14} />
                      <span>Download Stego Image</span>
                    </a>
                  </div>
                )}
              </div>
            )}

            <button className="cat-pill active" style={{ width: '100%', padding: '0.75rem' }} onClick={handleRunSteganography}>
              {stegoMode === 'encode' ? 'Encrypt & Embed into Image' : 'Extract Hidden Payload'}
            </button>
          </div>
        </div>
      )}

      {/* MODAL 3: OpenCV Camera Verification Modal */}
      {cameraModalOpen && (
        <div className="modal-overlay" onClick={() => setCameraModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setCameraModalOpen(false)}
              style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
            >
              <X size={20} />
            </button>

            <h3 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Camera className="text-blue-400" size={20} />
              <span>{cameraMode === 'register' ? 'Enroll Master Facial ID' : `Biometric Verification: ${targetDownloadFile}`}</span>
            </h3>

            <div className="camera-container">
              <video ref={videoRef} autoPlay playsInline muted className="camera-video" />
              <div className={`face-guide-box ${verifyingFace ? 'scanning' : faceResult?.verified ? 'success' : faceResult?.success === false ? 'error' : ''}`} />
              <div className="scan-beam" />
            </div>

            {faceResult && (
              <div style={{ padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem', background: faceResult.verified || faceResult.success ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)', color: faceResult.verified || faceResult.success ? '#6ee7b7' : '#fca5a5' }}>
                {faceResult.message}
              </div>
            )}

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button className="btn-icon" style={{ padding: '0.6rem 1rem' }} onClick={() => setCameraModalOpen(false)}>
                Cancel
              </button>
              <button className="cat-pill active" style={{ padding: '0.6rem 1.25rem' }} onClick={handleRunBiometricAction} disabled={verifyingFace}>
                {verifyingFace ? 'Scanning Face...' : cameraMode === 'register' ? 'Capture Facial Profile' : 'Verify & Authorize'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 4: AI Document ML Details Inspection Modal */}
      {selectedMlFile && mlDetails && (
        <div className="modal-overlay" onClick={() => setSelectedMlFile(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setSelectedMlFile(null)}
              style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
            >
              <X size={20} />
            </button>

            <h3 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles className="text-purple-400" size={20} />
              <span>AI ML Document Analysis</span>
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Filename: <strong style={{ color: 'var(--text-primary)' }}>{mlDetails.filename}</strong>
            </p>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--glass-border)', padding: '1rem', borderRadius: '10px', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Predicted ML Category:</span>
                <span className="badge-cat badge-document" style={{ fontSize: '0.85rem' }}>
                  {mlDetails.predicted_category}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>ML Model Confidence:</span>
                <strong style={{ color: '#34d399' }}>{mlDetails.confidence_percentage}</strong>
              </div>
            </div>

            {mlDetails.summary && (
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>
                  Text Snippet & Summary:
                </label>
                <div style={{ background: '#020617', padding: '0.75rem', borderRadius: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)', maxHeight: '100px', overflowY: 'auto' }}>
                  "{mlDetails.summary}"
                </div>
              </div>
            )}

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.4rem' }}>
                Active AI Tags:
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginBottom: '0.75rem' }}>
                {mlDetails.tags && mlDetails.tags.map((t, idx) => (
                  <span key={idx} className="ai-tag-pill">#{t}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
