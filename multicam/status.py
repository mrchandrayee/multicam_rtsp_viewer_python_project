import json, threading, time
from urllib.request import Request, urlopen
from urllib.error import URLError

class StatusReporter:
    """Optional heartbeat to an existing device-management API."""
    def __init__(self,url="",api_key="",interval=30):
        self.url=url; self.api_key=api_key; self.interval=interval
        self.stop_event=threading.Event(); self.thread=None

    def send(self,payload):
        if not self.url: return
        data=json.dumps(payload).encode()
        headers={"Content-Type":"application/json"}
        if self.api_key: headers["Authorization"]=f"Bearer {self.api_key}"
        req=Request(self.url,data=data,headers=headers,method="POST")
        try:
            with urlopen(req,timeout=5) as response:
                print(f"[API] heartbeat status={response.status}")
        except (URLError,TimeoutError) as exc:
            print(f"[API] heartbeat failed: {exc}")

    def start(self,workers):
        if not self.url: return
        def loop():
            while not self.stop_event.is_set():
                self.send({"event":"camera_status","cameras":[
                    {"name":w.config.name,"active":w.connected,"frames":w.frame_count,
                     "recording":w.recording,"error":w.last_error} for w in workers]})
                self.stop_event.wait(self.interval)
        self.thread=threading.Thread(target=loop,daemon=True); self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread: self.thread.join(timeout=2)
