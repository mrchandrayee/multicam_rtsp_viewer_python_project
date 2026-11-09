import cv2, threading, time
from datetime import datetime
from pathlib import Path

class CameraWorker:
    """Owns one RTSP capture and optional per-camera recorder."""
    def __init__(self, config, output_dir, reconnect_delay=3.0, recording_enabled=True):
        self.config=config; self.output_dir=Path(output_dir)
        self.reconnect_delay=reconnect_delay; self.recording_enabled=recording_enabled
        self.cap=None; self.writer=None; self.frame=None
        self.lock=threading.Lock(); self.stop_event=threading.Event()
        self.thread=None; self.connected=False; self.last_error=""
        self.frame_count=0; self.last_frame_at=0.0; self.recording=False

    def start(self):
        self.thread=threading.Thread(target=self._run,name=f"camera-{self.config.name}",daemon=True)
        self.thread.start()

    def _open(self):
        # OpenCV uses FFmpeg/GStreamer backend depending on the local build.
        cap=cv2.VideoCapture(self.config.url,cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE,2)
        return cap if cap.isOpened() else None

    def _close_writer(self):
        if self.writer is not None:
            self.writer.release(); self.writer=None
        self.recording=False

    def set_recording(self, enabled):
        if not enabled:
            self._close_writer(); return
        if not self.recording_enabled or self.writer is not None or self.frame is None: return
        h,w=self.frame.shape[:2]
        folder=self.output_dir/self.config.name
        folder.mkdir(parents=True,exist_ok=True)
        stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        path=folder/f"{stamp}.mp4"
        writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*"mp4v"),
                               max(1,self.config.fps),(w,h))
        if writer.isOpened():
            self.writer=writer; self.recording=True
            print(f"[REC] {self.config.name}: {path}")
        else:
            writer.release(); self.last_error="Could not open VideoWriter"

    def _run(self):
        while not self.stop_event.is_set():
            if self.cap is None or not self.cap.isOpened():
                self.connected=False
                self.cap=self._open()
                if self.cap is None:
                    self.last_error="RTSP connection failed"
                    self.stop_event.wait(self.reconnect_delay); continue
                self.connected=True; self.last_error=""
                print(f"[CAM] Connected: {self.config.name}")
            ok,frame=self.cap.read()
            if not ok or frame is None:
                self.connected=False
                self.last_error="Stream read failed; reconnecting"
                self.cap.release(); self.cap=None
                self._close_writer()
                self.stop_event.wait(self.reconnect_delay); continue
            with self.lock:
                self.frame=frame
                self.frame_count+=1
                self.last_frame_at=time.time()
                if self.writer is not None:
                    self.writer.write(frame)
        if self.cap is not None: self.cap.release()
        self._close_writer()

    def snapshot(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def stop(self):
        self.stop_event.set()
        if self.thread: self.thread.join(timeout=5)
