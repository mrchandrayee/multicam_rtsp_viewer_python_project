from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class CameraConfig:
    name: str
    url: str
    enabled: bool = True
    username: str = ""
    password: str = ""
    fps: int = 20
    width: int = 640
    height: int = 360

@dataclass
class AppConfig:
    cameras: list
    grid_cols: int = 2
    reconnect_delay: float = 3.0
    output_dir: str = "recordings"
    recording_enabled: bool = True
    schedule: dict | None = None
    status_api_url: str = ""
    status_api_key: str = ""

def load_config(path="config/cameras.json"):
    raw=json.loads(Path(path).read_text(encoding="utf-8"))
    cams=[CameraConfig(**item) for item in raw.get("cameras",[])]
    return AppConfig(cameras=cams,grid_cols=raw.get("grid_cols",2),
        reconnect_delay=raw.get("reconnect_delay",3.0),
        output_dir=raw.get("output_dir","recordings"),
        recording_enabled=raw.get("recording_enabled",True),
        schedule=raw.get("schedule"),
        status_api_url=raw.get("status_api_url",""),
        status_api_key=raw.get("status_api_key",""))
