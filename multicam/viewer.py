import cv2, numpy as np, time
from .schedule import is_recording_time

def make_tile(worker, size=(640,360)):
    frame=worker.snapshot()
    w,h=size
    if frame is None:
        tile=np.zeros((h,w,3),dtype=np.uint8)
        cv2.putText(tile,f"{worker.config.name}: NO SIGNAL",(20,h//2),
                    cv2.FONT_HERSHEY_SIMPLEX,.8,(0,0,255),2)
    else:
        tile=cv2.resize(frame,(w,h))
        state="LIVE" if worker.connected else "RECONNECTING"
        color=(0,220,0) if worker.connected else (0,0,255)
        cv2.putText(tile,f"{worker.config.name} | {state}",(12,28),
                    cv2.FONT_HERSHEY_SIMPLEX,.65,color,2)
        if worker.recording:
            cv2.circle(tile,(w-25,25),8,(0,0,255),-1)
            cv2.putText(tile,"REC",(w-75,31),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255),2)
    return tile

def run_viewer(workers, cols=2, schedule=None):
    rows=max(1,(len(workers)+cols-1)//cols)
    tile_w,tile_h=640,360
    print("Viewer started. Press Q or ESC to quit.")
    try:
        while True:
            rec=is_recording_time(schedule)
            for worker in workers: worker.set_recording(rec)
            tiles=[make_tile(w,(tile_w,tile_h)) for w in workers]
            while len(tiles)<rows*cols:
                tiles.append(np.zeros((tile_h,tile_w,3),dtype=np.uint8))
            grid=np.vstack([np.hstack(tiles[r*cols:(r+1)*cols]) for r in range(rows)])
            cv2.imshow("AI Box - Multi Camera Viewer",grid)
            key=cv2.waitKey(1)&0xFF
            if key in (ord("q"),27): break
    finally:
        cv2.destroyAllWindows()
