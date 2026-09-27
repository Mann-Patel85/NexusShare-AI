import asyncio
import time
import socket
from typing import List, Dict, Any, Set
from fastapi import WebSocket, WebSocketDisconnect
import psutil


class NetworkWebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.peer_info: Dict[WebSocket, Dict[str, Any]] = {}
        self.last_net_io = None
        self.last_time = time.time()
        self._background_task = None

    async def connect(self, websocket: WebSocket, client_ip: str, user_agent: str):
        await websocket.accept()
        self.active_connections.add(websocket)
        self.peer_info[websocket] = {
            "ip": client_ip,
            "user_agent": user_agent,
            "connected_at": time.strftime("%H:%M:%S"),
            "connected_timestamp": time.time()
        }

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.peer_info:
            del self.peer_info[websocket]

    async def broadcast(self, message: Dict[str, Any]):
        disconnected = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    def get_network_metrics(self) -> Dict[str, Any]:
        current_time = time.time()
        time_diff = max(current_time - self.last_time, 0.5)

        net_io = psutil.net_io_counters()

        if self.last_net_io is None:
            bytes_sent_per_sec = 0.0
            bytes_recv_per_sec = 0.0
        else:
            bytes_sent_per_sec = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
            bytes_recv_per_sec = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff

        self.last_net_io = net_io
        self.last_time = current_time

        recv_kb = bytes_recv_per_sec / 1024.0
        sent_kb = bytes_sent_per_sec / 1024.0

        if recv_kb >= 1024:
            download_speed_str = f"{recv_kb / 1024.0:.2f} MB/s"
        else:
            download_speed_str = f"{recv_kb:.1f} KB/s"

        if sent_kb >= 1024:
            upload_speed_str = f"{sent_kb / 1024.0:.2f} MB/s"
        else:
            upload_speed_str = f"{sent_kb:.1f} KB/s"

        peers_list = []
        for conn, info in self.peer_info.items():
            peers_list.append({
                "ip": info["ip"],
                "user_agent": info["user_agent"],
                "connected_at": info["connected_at"],
                "uptime_seconds": int(time.time() - info["connected_timestamp"])
            })

        return {
            "type": "network_telemetry",
            "download_speed": download_speed_str,
            "upload_speed": upload_speed_str,
            "download_kbps": round(recv_kb, 1),
            "upload_kbps": round(sent_kb, 1),
            "total_sent_mb": round(net_io.bytes_sent / (1024 * 1024), 1),
            "total_recv_mb": round(net_io.bytes_recv / (1024 * 1024), 1),
            "cpu_usage_pct": psutil.cpu_percent(interval=None),
            "ram_usage_pct": psutil.virtual_memory().percent,
            "connected_peers_count": len(self.active_connections),
            "peers": peers_list
        }


ws_manager = NetworkWebSocketManager()
