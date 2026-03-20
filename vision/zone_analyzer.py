import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cv2
from ultralytics import YOLO
from database.zone_db import insert_zone,init_zone_db

model = YOLO("yolov8n.pt")

def analyze_zones():
    init_zone_db()

    cap = cv2.VideoCapture("video/retail_demo.mp4")

    GRID_ROWS = 8
    GRID_COLS = 8

    dwell_frames = {}

    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (960, 540))

        results = model.track(frame, persist=True)

        if results[0].boxes is None:
            cv2.imshow("Zone Analytics", frame)
            if cv2.waitKey(1) == 27:
                break
            continue

        boxes = results[0].boxes.xyxy.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()

        ids = results[0].boxes.id.cpu().numpy() if results[0].boxes.id is not None else range(len(boxes))

        cell_w = 960 // GRID_COLS
        cell_h = 540 // GRID_ROWS

        for box, track_id, cls in zip(boxes, ids, classes):

            if int(cls) != 0:
                continue

            x1, y1, x2, y2 = map(int, box)

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            customer_id = int(track_id)

            # GRID
            col = min(cx // cell_w, GRID_COLS - 1)
            row = min(cy // cell_h, GRID_ROWS - 1)

            # DWELL
            if customer_id not in dwell_frames:
                dwell_frames[customer_id] = 0

            dwell_frames[customer_id] += 1
            dwell_time = dwell_frames[customer_id] / fps

            # DRAW
            cv2.rectangle(frame,
                          (col * cell_w, row * cell_h),
                          ((col + 1) * cell_w, (row + 1) * cell_h),
                          (255, 0, 0), 2)

            cv2.putText(frame, f"Z({row},{col})",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255,0,0), 2)

            # SAVE
            insert_zone(customer_id, row, col, dwell_time, cx, cy)

        cv2.imshow("Zone Analytics", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    print("🔥 ZONE ANALYSIS COMPLETE")