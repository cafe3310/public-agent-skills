#!/usr/bin/env python3
"""
Chat Screenrec Extractor - Calibration Web UI Server
Provides interactive frame sampling adjustment and ROI bounding box calibration.
"""

import argparse
import json
import mimetypes
import os
import subprocess
import sys
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.m4v', '.webm', '.avi', '.mkv'}

class CalibrationServer:
    def __init__(self, input_dir: str, port: int = 8765):
        self.input_dir = Path(input_dir).resolve()
        self.port = port
        self.cache_dir = self.input_dir / ".cache" / "preview"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.web_dir = Path(__file__).parent / "web"

    def get_video_files(self):
        videos = []
        if not self.input_dir.exists():
            return videos
        for root, _, files in os.walk(self.input_dir):
            # Skip cache and hidden dirs
            if "/." in root or "\\." in root:
                continue
            for file in sorted(files):
                ext = Path(file).suffix.lower()
                if ext in VIDEO_EXTENSIONS:
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(self.input_dir)
                    videos.append({
                        "name": file,
                        "rel_path": str(rel_path),
                        "full_path": str(full_path),
                        "size": full_path.stat().st_size
                    })
        return videos

    def get_video_metadata(self, rel_path: str):
        full_path = self.input_dir / rel_path
        if not full_path.exists():
            return None
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration,r_frame_rate,nb_frames",
            "-show_entries", "format=duration",
            "-of", "json",
            str(full_path)
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            stream = data.get("streams", [{}])[0]
            fmt = data.get("format", {})
            duration = float(fmt.get("duration") or stream.get("duration") or 0.0)
            width = int(stream.get("width") or 0)
            height = int(stream.get("height") or 0)
            fps_str = stream.get("r_frame_rate", "30/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                fps = float(num) / float(den) if float(den) > 0 else 30.0
            else:
                fps = float(fps_str)
            return {
                "duration": duration,
                "width": width,
                "height": height,
                "fps": round(fps, 2)
            }
        except Exception as e:
            print(f"Error probing video {rel_path}: {e}", file=sys.stderr)
            return {"duration": 0.0, "width": 0, "height": 0, "fps": 30.0}

    def extract_frame(self, rel_path: str, timestamp: float) -> Path:
        full_path = self.input_dir / rel_path
        if not full_path.exists():
            return None
        clean_name = rel_path.replace("/", "_").replace("\\", "_")
        cache_file = self.cache_dir / f"frame_{clean_name}_{timestamp:.2f}.jpg"
        if not cache_file.exists():
            # Extract frame at exact timestamp using ffmpeg -ss
            cmd = [
                "ffmpeg", "-y", "-ss", f"{timestamp:.3f}",
                "-i", str(full_path),
                "-frames:v", "1",
                "-q:v", "2",
                str(cache_file)
            ]
            subprocess.run(cmd, capture_output=True, check=False)
        return cache_file if cache_file.exists() else None

    def save_config(self, config_data: dict):
        config_path = self.input_dir / "roi_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return str(config_path)

    def load_config(self):
        config_path = self.input_dir / "roi_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

def make_handler(server_instance: CalibrationServer):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            path = parsed.path

            if path == "/api/videos":
                videos = server_instance.get_video_files()
                config = server_instance.load_config()
                self._send_json({"videos": videos, "saved_config": config})
                return

            elif path == "/api/video_info":
                video_rel = query.get("video", [None])[0]
                if not video_rel:
                    self._send_error(400, "Missing 'video' parameter")
                    return
                info = server_instance.get_video_metadata(video_rel)
                self._send_json(info or {})
                return

            elif path == "/api/frame":
                video_rel = query.get("video", [None])[0]
                time_str = query.get("time", ["0.0"])[0]
                try:
                    timestamp = float(time_str)
                except ValueError:
                    timestamp = 0.0

                if not video_rel:
                    self._send_error(400, "Missing 'video' parameter")
                    return

                frame_path = server_instance.extract_frame(video_rel, timestamp)
                if frame_path and frame_path.exists():
                    self.send_response(200)
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Cache-Control", "public, max-age=3600")
                    self.end_headers()
                    with open(frame_path, "rb") as f:
                        self.wfile.write(f.read())
                else:
                    self._send_error(404, "Frame extraction failed")
                return

            elif path == "/api/load_config":
                config = server_instance.load_config()
                self._send_json(config or {})
                return

            # Serve static assets from web/
            if path == "/":
                file_path = server_instance.web_dir / "index.html"
            else:
                rel = path.lstrip("/")
                file_path = server_instance.web_dir / rel

            if file_path.exists() and file_path.is_file():
                mime, _ = mimetypes.guess_type(str(file_path))
                self.send_response(200)
                self.send_header("Content-Type", mime or "text/plain")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._send_error(404, "Not Found")

        def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/api/save_config":
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length).decode('utf-8')
                try:
                    data = json.loads(body)
                    saved_path = server_instance.save_config(data)
                    self._send_json({"success": True, "saved_to": saved_path})
                except Exception as e:
                    self._send_json({"success": False, "error": str(e)}, status=500)
                return
            self._send_error(404, "Not Found")

        def _send_json(self, data: dict, status: int = 200):
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_error(self, status: int, message: str):
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))

    return Handler

def run(input_dir: str, port: int):
    server = CalibrationServer(input_dir=input_dir, port=port)
    handler = make_handler(server)
    httpd = HTTPServer(("0.0.0.0", port), handler)
    print(f"================================================================")
    print(f" Chat Screenrec Extractor - Calibration UI")
    print(f" Video Directory : {server.input_dir}")
    print(f" Local Web UI    : http://localhost:{port}")
    print(f"================================================================")
    print("Press Ctrl+C to stop server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        httpd.server_close()

def main():
    parser = argparse.ArgumentParser(description="Start Chat Screenrec Calibration Server")
    parser.add_argument("--input-dir", "-i", default=".", help="Directory containing screen recording videos")
    parser.add_argument("--port", "-p", type=int, default=8765, help="Port to run web server on (default: 8765)")
    args = parser.parse_args()
    run(args.input_dir, args.port)

if __name__ == "__main__":
    main()
