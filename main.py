import argparse, signal
from multicam.config import load_config
from multicam.camera_worker import CameraWorker
from multicam.viewer import run_viewer
from multicam.status import StatusReporter

def main():
    parser=argparse.ArgumentParser(description="Multi-camera RTSP viewer and recorder")
    parser.add_argument("--config",default="config/cameras.json")
    parser.add_argument("--headless",action="store_true",help="Connect and record without display")
    args=parser.parse_args()
    cfg=load_config(args.config)
    workers=[CameraWorker(c,cfg.output_dir,cfg.reconnect_delay,cfg.recording_enabled)
             for c in cfg.cameras if c.enabled]
    if not workers: raise SystemExit("No enabled cameras in configuration.")
    reporter=StatusReporter(cfg.status_api_url,cfg.status_api_key)
    for w in workers: w.start()
    reporter.start(workers)
    try:
        if args.headless:
            import time
            from multicam.schedule import is_recording_time
            while True:
                active=is_recording_time(cfg.schedule)
                for w in workers: w.set_recording(active)
                time.sleep(1)
        else:
            run_viewer(workers,cfg.grid_cols,cfg.schedule)
    except KeyboardInterrupt:
        pass
    finally:
        reporter.stop()
        for w in workers: w.stop()

if __name__=="__main__": main()
