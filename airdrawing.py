
import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime

# =====================================
# 1. APPLICATION SETTINGS
# =====================================

SCREEN_W = 1280
SCREEN_H = 720
TOOLBAR_H = 80

CANVAS_W = SCREEN_W
CANVAS_H = SCREEN_H - TOOLBAR_H

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# =====================================
# 2. COLORS
# =====================================

colors = {
    "BLACK": (0, 0, 0),
    "BLUE": (255, 0, 0),
    "RED": (0, 0, 255),
    "GREEN": (0, 255, 0),
    "YELLOW": (0, 255, 255),
    "PINK": (255, 0, 255),
    "CYAN": (255, 255, 0),
    "ORANGE": (0, 165, 255)
}

backgrounds = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "GREEN": (0, 100, 0)
}

current_color = colors["BLUE"]
current_bg = backgrounds["WHITE"]

brush_size = 5
tool = "PEN"

canvas = np.full(
    (CANVAS_H, CANVAS_W, 3),
    current_bg,
    dtype=np.uint8
)

# =====================================
# 3. UNDO / REDO
# =====================================

undo_stack = []
redo_stack = []

def save_history():

    undo_stack.append(canvas.copy())

    if len(undo_stack) > 30:
        undo_stack.pop(0)

    redo_stack.clear()


def undo():

    global canvas

    if undo_stack:
        redo_stack.append(canvas.copy())
        canvas = undo_stack.pop()


def redo():

    global canvas

    if redo_stack:
        undo_stack.append(canvas.copy())
        canvas = redo_stack.pop()


# =====================================
# 4. SAVE DRAWING
# =====================================

def save_drawing():

    folder = "Saved_Drawings"
    os.makedirs(folder, exist_ok=True)

    filename = datetime.now().strftime(
        "Drawing_%Y%m%d_%H%M%S.png"
    )

    path = os.path.join(folder, filename)

    cv2.imwrite(path, canvas)

    print("Drawing saved:", path)


# =====================================
# 5. TOOLBAR
# =====================================

buttons = [
    (10, 55, "UNDO", "UNDO"),
    (65, 110, "REDO", "REDO"),
    (120, 175, "PEN", "PEN"),
    (180, 245, "CIRCLE", "CIRCLE"),
    (250, 315, "RECT", "RECT"),
    (320, 390, "ERASE", "ERASE"),

    (400, 445, "BLK", "BLACK"),
    (450, 495, "BLUE", "BLUE"),
    (500, 545, "RED", "RED"),
    (550, 595, "GRN", "GREEN"),
    (600, 645, "YLW", "YELLOW"),
    (650, 695, "PNK", "PINK"),
    (700, 745, "CYN", "CYAN"),
    (750, 795, "ORG", "ORANGE"),

    (805, 845, "S", "SMALL"),
    (850, 890, "M", "MEDIUM"),
    (895, 935, "L", "LARGE"),

    (945, 990, "WHT", "WHITE"),
    (995, 1040, "DARK", "BG_BLACK"),
    (1045, 1090, "GRN", "BG_GREEN"),

    (1150, 1265, "SAVE", "SAVE")
]


# =====================================
# 6. MOUSE CONTROLS
# =====================================

def mouse_callback(event, x, y, flags, param):

    global current_color, current_bg
    global brush_size, tool, canvas

    if event == cv2.EVENT_LBUTTONDOWN:

        if y > TOOLBAR_H:
            return

        for x1, x2, label, action in buttons:

            if x1 <= x <= x2:

                if action == "UNDO":
                    undo()

                elif action == "REDO":
                    redo()

                elif action in ["PEN", "CIRCLE", "RECT", "ERASE"]:
                    tool = action

                elif action in colors:
                    current_color = colors[action]

                elif action == "SMALL":
                    brush_size = 3

                elif action == "MEDIUM":
                    brush_size = 7

                elif action == "LARGE":
                    brush_size = 12

                elif action == "WHITE":
                    save_history()
                    current_bg = backgrounds["WHITE"]
                    canvas[:] = current_bg

                elif action == "BG_BLACK":
                    save_history()
                    current_bg = backgrounds["BLACK"]
                    canvas[:] = current_bg

                elif action == "BG_GREEN":
                    save_history()
                    current_bg = backgrounds["GREEN"]
                    canvas[:] = current_bg

                elif action == "SAVE":
                    save_drawing()

                break


# =====================================
# 7. DRAW TOOLBAR
# =====================================

def draw_toolbar(frame):

    frame[:TOOLBAR_H] = (40, 40, 40)

    for x1, x2, label, action in buttons:

        active = False

        if action == tool:
            active = True

        if action == "SMALL" and brush_size == 3:
            active = True

        if action == "MEDIUM" and brush_size == 7:
            active = True

        if action == "LARGE" and brush_size == 12:
            active = True

        if action in colors and current_color == colors[action]:
            active = True

        if action == "WHITE" and current_bg == backgrounds["WHITE"]:
            active = True

        if action == "BG_BLACK" and current_bg == backgrounds["BLACK"]:
            active = True

        if action == "BG_GREEN" and current_bg == backgrounds["GREEN"]:
            active = True

        bg = (70, 130, 70) if active else (65, 65, 65)

        cv2.rectangle(
            frame,
            (x1, 15),
            (x2, 65),
            bg,
            cv2.FILLED
        )

        cv2.rectangle(
            frame,
            (x1, 15),
            (x2, 65),
            (180, 180, 180),
            1
        )

        cv2.putText(
            frame,
            label,
            (x1 + 4, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.43,
            (255, 255, 255),
            1
        )

    cv2.putText(
        frame,
        "AIR DRAWING STUDIO",
        (15, 705),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (100, 100, 100),
        1
    )


# =====================================
# 8. DRAWING VARIABLES
# =====================================

prev_x, prev_y = 0, 0

smooth_x, smooth_y = 0, 0

smooth_factor = 0.35

previous_gesture = "NONE"

stroke_active = False

shape_start = None
shape_end = None
shape_active = False

# =====================================
# 9. MAIN WINDOW
# =====================================

cv2.namedWindow(
    "Air Drawing Studio",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "Air Drawing Studio",
    SCREEN_W,
    SCREEN_H
)

cv2.setMouseCallback(
    "Air Drawing Studio",
    mouse_callback
)

print("AIR DRAWING STUDIO STARTED")
print("Index finger: Draw")
print("Index + Middle: Erase")
print("C: Clear")
print("Z: Undo")
print("Y: Redo")
print("S: Save")
print("ESC: Exit")


# =====================================
# 10. MAIN LOOP
# =====================================

while True:

    success, img = cap.read()

    if not success:
        print("Camera not detected!")
        break

    img = cv2.flip(img, 1)

    imgRGB = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(imgRGB)

    gesture = "NONE"

    # ---------------------------------
    # HAND DETECTION
    # ---------------------------------

    if results.multi_hand_landmarks:

        for handLms in results.multi_hand_landmarks:

            h, w, c = img.shape

            lm_list = []

            for lm in handLms.landmark:

                cx = int(lm.x * w)
                cy = int(lm.y * h)

                lm_list.append((cx, cy))

            # Finger positions
            x1, y1 = lm_list[8]
            x2, y2 = lm_list[12]

            index_up = y1 < lm_list[6][1]
            middle_up = y2 < lm_list[10][1]

            # Map camera coordinates to canvas
            draw_x = int(x1 * CANVAS_W / w)
            draw_y = int(y1 * CANVAS_H / h)

            # Gesture detection
            if index_up and middle_up:
                gesture = "ERASE"

            elif index_up and not middle_up:
                gesture = "DRAW"

            # ---------------------------------
            # SMOOTH MOVEMENT
            # ---------------------------------

            if gesture != "NONE":

                if smooth_x == 0 and smooth_y == 0:

                    smooth_x = draw_x
                    smooth_y = draw_y

                smooth_x = int(
                    smooth_factor * draw_x +
                    (1 - smooth_factor) * smooth_x
                )

                smooth_y = int(
                    smooth_factor * draw_y +
                    (1 - smooth_factor) * smooth_y
                )

            # ---------------------------------
            # FREEHAND DRAWING
            # ---------------------------------

            if gesture == "DRAW" and tool == "PEN":

                if not stroke_active:

                    save_history()
                    stroke_active = True

                start = (
                    (prev_x, prev_y)
                    if prev_x != 0 or prev_y != 0
                    else (smooth_x, smooth_y)
                )

                cv2.line(
                    canvas,
                    start,
                    (smooth_x, smooth_y),
                    current_color,
                    brush_size
                )

                cv2.circle(
                    img,
                    (x1, y1),
                    8,
                    (0, 255, 0),
                    cv2.FILLED
                )

            # ---------------------------------
            # ERASER
            # ---------------------------------

            elif gesture == "ERASE" or (
                gesture == "DRAW" and tool == "ERASE"
            ):

                if not stroke_active:

                    save_history()
                    stroke_active = True

                start = (
                    (prev_x, prev_y)
                    if prev_x != 0 or prev_y != 0
                    else (smooth_x, smooth_y)
                )

                cv2.line(
                    canvas,
                    start,
                    (smooth_x, smooth_y),
                    current_bg,
                    35
                )

                cv2.circle(
                    img,
                    (x1, y1),
                    15,
                    (0, 0, 255),
                    2
                )

            # ---------------------------------
            # CIRCLE / RECTANGLE
            # ---------------------------------

            elif gesture == "DRAW" and tool in ["CIRCLE", "RECT"]:

                if not shape_active:

                    save_history()

                    shape_start = (smooth_x, smooth_y)
                    shape_active = True

                shape_end = (smooth_x, smooth_y)

            # ---------------------------------
            # RELEASE GESTURE
            # ---------------------------------

            elif gesture == "NONE":

                if stroke_active:
                    stroke_active = False

                if shape_active:

                    x_start, y_start = shape_start
                    x_end, y_end = shape_end

                    if tool == "CIRCLE":

                        radius = int(
                            np.sqrt(
                                (x_end - x_start) ** 2 +
                                (y_end - y_start) ** 2
                            )
                        )

                        cv2.circle(
                            canvas,
                            shape_start,
                            radius,
                            current_color,
                            brush_size
                        )

                    elif tool == "RECT":

                        cv2.rectangle(
                            canvas,
                            shape_start,
                            shape_end,
                            current_color,
                            brush_size
                        )

                    shape_active = False
                    shape_start = None
                    shape_end = None

            # Reset previous coordinates
            if gesture == "NONE":

                prev_x, prev_y = 0, 0
                smooth_x, smooth_y = 0, 0

            else:

                prev_x, prev_y = smooth_x, smooth_y

            previous_gesture = gesture

            # Hand landmarks
            mp_draw.draw_landmarks(
                img,
                handLms,
                mp_hands.HAND_CONNECTIONS
            )

    # ---------------------------------
    # HAND NOT DETECTED
    # ---------------------------------

    else:

        stroke_active = False

        if shape_active and shape_start and shape_end:

            x_start, y_start = shape_start
            x_end, y_end = shape_end

            if tool == "CIRCLE":

                radius = int(
                    np.sqrt(
                        (x_end - x_start) ** 2 +
                        (y_end - y_start) ** 2
                    )
                )

                cv2.circle(
                    canvas,
                    shape_start,
                    radius,
                    current_color,
                    brush_size
                )

            elif tool == "RECT":

                cv2.rectangle(
                    canvas,
                    shape_start,
                    shape_end,
                    current_color,
                    brush_size
                )

        shape_active = False
        shape_start = None
        shape_end = None

        prev_x, prev_y = 0, 0
        smooth_x, smooth_y = 0, 0

        previous_gesture = "NONE"

    # =================================
    # 11. SHAPE PREVIEW
    # =================================

    display_canvas = canvas.copy()

    if shape_active and shape_start and shape_end:

        if tool == "CIRCLE":

            radius = int(
                np.sqrt(
                    (shape_end[0] - shape_start[0]) ** 2 +
                    (shape_end[1] - shape_start[1]) ** 2
                )
            )

            cv2.circle(
                display_canvas,
                shape_start,
                radius,
                current_color,
                brush_size
            )

        elif tool == "RECT":

            cv2.rectangle(
                display_canvas,
                shape_start,
                shape_end,
                current_color,
                brush_size
            )

    # =================================
    # 12. FINAL APPLICATION SCREEN
    # =================================

    frame = np.zeros(
        (SCREEN_H, SCREEN_W, 3),
        dtype=np.uint8
    )

    # Drawing canvas
    frame[TOOLBAR_H:, :] = display_canvas

    # Toolbar
    draw_toolbar(frame)

    # ---------------------------------
    # CAMERA INSIDE WHITE SCREEN
    # ---------------------------------

    cam_w = 280
    cam_h = 210

    camera_preview = cv2.resize(
        img,
        (cam_w, cam_h)
    )

    x_offset = SCREEN_W - cam_w - 20
    y_offset = TOOLBAR_H + 20

    # Embed camera in drawing board
    frame[
        y_offset:y_offset + cam_h,
        x_offset:x_offset + cam_w
    ] = camera_preview

    # Camera border
    cv2.rectangle(
        frame,
        (x_offset, y_offset),
        (x_offset + cam_w, y_offset + cam_h),
        (0, 0, 0),
        3
    )

    # Camera label
    cv2.putText(
        frame,
        "LIVE CAMERA",
        (x_offset + 5, y_offset - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 0),
        1
    )

    # Gesture information
    cv2.putText(
        frame,
        "GESTURE: " + gesture,
        (900, 705),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (100, 100, 100),
        1
    )

    # Show only ONE window
    cv2.imshow(
        "Air Drawing Studio",
        frame
    )

    # =================================
    # 13. KEYBOARD CONTROLS
    # =================================

    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break

    elif key == ord('c') or key == ord('C'):

        save_history()
        canvas[:] = current_bg

    elif key == ord('z') or key == ord('Z'):
        undo()

    elif key == ord('y') or key == ord('Y'):
        redo()

    elif key == ord('s') or key == ord('S'):
        save_drawing()


# =====================================
# 14. RELEASE RESOURCES
# =====================================

cap.release()
hands.close()
cv2.destroyAllWindows()

print("Air Drawing Studio Closed!")
