import cv2
import mediapipe as mp
import numpy as np

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# Canvas
canvas = np.ones((480, 640, 3), dtype=np.uint8) * 255

prev_x, prev_y = None, None

alpha = 0.3
smooth_x, smooth_y = 0, 0

mode = "IDLE"   # IMPORTANT FIX (start safe)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            lm_list = []
            h, w, _ = img.shape

            for lm in handLms.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

            # Key points
            thumb = lm_list[4]
            index = lm_list[8]
            middle = lm_list[12]

            # ---------------- MODE DETECTION (FIXED) ----------------

            index_up = lm_list[8][1] < lm_list[6][1]
            middle_up = lm_list[12][1] < lm_list[10][1]
            ring_up = lm_list[16][1] < lm_list[14][1]
            pinky_up = lm_list[20][1] < lm_list[18][1]

            thumb_up = lm_list[4][1] < lm_list[3][1]

            # 🧽 ERASE MODE
            if thumb_up and not index_up:
                mode = "ERASE"

            # ✍️ DRAW MODE (ONLY index finger up)
            elif index_up and not middle_up and not ring_up and not pinky_up:
                mode = "DRAW"

            # 💤 IDLE MODE
            else:
                mode = "IDLE"

            # reset when idle
            if mode == "IDLE":
                prev_x, prev_y = None, None
                smooth_x, smooth_y = 0, 0

            # ---------------- DRAW MODE ----------------
            if mode == "DRAW":

                if smooth_x == 0 and smooth_y == 0:
                    smooth_x, smooth_y = index

                smooth_x = int(alpha * index[0] + (1 - alpha) * smooth_x)
                smooth_y = int(alpha * index[1] + (1 - alpha) * smooth_y)

                if prev_x is None:
                    prev_x, prev_y = smooth_x, smooth_y

                cv2.line(canvas,
                         (prev_x, prev_y),
                         (smooth_x, smooth_y),
                         (255, 0, 0),
                         5)

                prev_x, prev_y = smooth_x, smooth_y

                cv2.circle(img, index, 10, (0, 255, 0), -1)

            # ---------------- ERASE MODE ----------------
            elif mode == "ERASE":

                eraser_size = 25

                cv2.circle(canvas,
                           index,
                           eraser_size,
                           (255, 255, 255),
                           -1)

                cv2.circle(img, index, eraser_size, (0, 0, 255), 2)

                prev_x, prev_y = None, None

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    # ---------------- UI ----------------
    cv2.putText(img, f"MODE: {mode}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 3)

    output = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)

    cv2.imshow("AI Paint App", output)
    cv2.imshow("Canvas", canvas)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()