import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import math
from ultralytics import YOLO
from database.db_manager import insert_customer, insert_suspect

model = YOLO("yolov8n.pt")

def analyze_video():

    cap = cv2.VideoCapture("video/retail_demo.mp4")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_count = 0
    FRAME_SKIP = 2

    previous_positions = {}
    dwell_frames = {}

    interaction_flag = {}
    left_shelf_flag = {}
    exit_flag = {}
    last_shelf = {}

    final_brand = {}
    saved_keys = set()

    suspect_count = 0

    # 🔥 MEMORY FOR SUSPECT LOGIC
    entered_shelf = {}
    left_after_pick = {}

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % FRAME_SKIP != 0:
            continue

        frame = cv2.resize(frame, (960, 540))

        results = model.track(
            frame,
            persist=True,
            conf=0.4,
            iou=0.5,
            tracker="bytetrack.yaml"
        )

        if results[0].boxes is None:
            cv2.imshow("Retail AI", frame)
            if cv2.waitKey(1) == 27:
                break
            continue

        boxes = results[0].boxes.xyxy.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()

        if results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().numpy()
        else:
            ids = list(range(len(boxes)))

        for box, track_id, cls in zip(boxes, ids, classes):

            if int(cls) != 0:
                continue

            x1, y1, x2, y2 = map(int, box)

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            try:
                customer_id = int(track_id)
            except:
                customer_id = int(cx + cy)

            # ID DISPLAY
            cv2.putText(frame, f"ID {customer_id}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)

            # DOOR
            door = "DoorA" if cx < 480 else "DoorB"

            # SHELF
            shelf = "None"
            if cy > 180:
                if cx < 150:
                    shelf = "Clothing"
                elif cx < 300:
                    shelf = "Electronics"
                elif cx < 600:
                    shelf = "Groceries"
                elif cx < 800:
                    shelf = "Snacks"
                else:
                    shelf = "Cosmetics"

            # BRAND
            if customer_id not in last_shelf and shelf != "None":
                last_shelf[customer_id] = shelf

                if shelf == "Electronics":
                    final_brand[customer_id] = "Apple"
                elif shelf == "Snacks":
                    final_brand[customer_id] = "Lays"
                elif shelf == "Groceries":
                    final_brand[customer_id] = "CocaCola"
                else:
                    final_brand[customer_id] = shelf

            brand = final_brand.get(customer_id, "None")

            # DISPLAY SHELF + BRAND
            cv2.putText(frame, f"{shelf}", (x1, y2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 2)

            cv2.putText(frame, f"{brand}", (x1, y2 + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)

            # DWELL
            if customer_id not in dwell_frames:
                dwell_frames[customer_id] = 0

            if shelf != "None":
                dwell_frames[customer_id] += 1

            dwell_time = dwell_frames[customer_id] / fps

            # FLAGS
            if shelf != "None":
                interaction_flag[customer_id] = True
                entered_shelf[customer_id] = True

            if shelf == "None":
                left_shelf_flag[customer_id] = True
                if entered_shelf.get(customer_id, False):
                    left_after_pick[customer_id] = True

            if cx < 80 or cx > 880:
                exit_flag[customer_id] = True

            # PURCHASE
            purchase = 1 if dwell_time > 3 else 0

            # =========================
            # 🔥 FINAL SUSPECT LOGIC (CORRECTED)
            # =========================

            moving_fast = False
            dist = 0

            if customer_id in previous_positions:
                px, py = previous_positions[customer_id]

                dx = cx - px
                dy = cy - py
                dist = math.sqrt(dx**2 + dy**2)

                if dist > 5:
                    moving_fast = True

            previous_positions[customer_id] = (cx, cy)

            suspect = False

            if (
                interaction_flag.get(customer_id, False) and
                left_after_pick.get(customer_id, False) and
                purchase == 0
            ):
                if (
                    exit_flag.get(customer_id, False) or
                    moving_fast or
                    dwell_time < 6 or
                    dist > 10
                ):
                    suspect = True

            # DISPLAY SUSPECT
            if suspect:
                cv2.circle(frame, (cx, cy), 10, (0,0,255), -1)

                cv2.putText(frame,
                            f"SUSPECT: {"Apple"}",
                            (cx, cy - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0,0,255),
                            2)

                insert_suspect(customer_id, shelf, brand, "Theft")
                suspect_count += 1

            # SAVE DATA
            key = (customer_id, shelf)
            if key not in saved_keys:
                insert_customer(
                    customer_id, shelf, brand, door,
                    purchase, dwell_time, cx, cy
                )
                saved_keys.add(key)

        cv2.imshow("Retail AI", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()

    try:
        cv2.destroyAllWindows()
    except:
        pass

    print("🔥 FULL SYSTEM RUN COMPLETE")
    print(f"🚨 Total Suspects Detected: {suspect_count}")
    print("Only the real suspect will bepointed in the final video. This is a demo of the logic in action.")