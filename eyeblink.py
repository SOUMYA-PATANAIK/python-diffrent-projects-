import cv2
import mediapipe as mp
import numpy as np
import screen_brightness_control as sbc

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh()

cap = cv2.VideoCapture(0)

# EAR calculation
def eye_aspect_ratio(landmarks, eye_points):
    p1 = np.array(landmarks[eye_points[0]])
    p2 = np.array(landmarks[eye_points[1]])
    p3 = np.array(landmarks[eye_points[2]])
    p4 = np.array(landmarks[eye_points[3]])
    p5 = np.array(landmarks[eye_points[4]])
    p6 = np.array(landmarks[eye_points[5]])

    vertical = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    horizontal = np.linalg.norm(p1 - p4)

    return vertical / (2.0 * horizontal)

LEFT_EYE = [33, 160, 158, 133, 153, 144]

blink_counter = 0
closed_frames = 0

brightness = 50
sbc.set_brightness(brightness)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            h, w, _ = img.shape
            landmarks = []

            for lm in face_landmarks.landmark:
                landmarks.append((int(lm.x * w), int(lm.y * h)))

            ear = eye_aspect_ratio(landmarks, LEFT_EYE)

            # 👁 EYE CLOSED
            if ear < 0.2:
                blink_counter += 1
                closed_frames += 1

            else:
                # 👁➡👀 BLINK DETECT (quick close-open)
                if 2 < blink_counter < 6:
                    brightness = min(100, brightness + 10)
                    sbc.set_brightness(brightness)

                blink_counter = 0
                closed_frames = 0

            # 😴 LONG CLOSE → DECREASE BRIGHTNESS
            if closed_frames > 10:
                brightness = max(10, brightness - 2)
                sbc.set_brightness(brightness)

            # 👀 OPEN → DO NOTHING (stable)

            # Display
            cv2.putText(img, f"Brightness: {brightness}",
                        (20,50), cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

            cv2.putText(img, f"EAR: {round(ear,2)}",
                        (20,100), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)

    cv2.imshow("Eye Brightness Control", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()