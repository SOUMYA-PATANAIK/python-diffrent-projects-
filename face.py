import cv2
import datetime

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 
'haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Camera error")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces with confidence
    faces, rejectLevels, weights = face_cascade.detectMultiScale3(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        outputRejectLevels=True
    )

    count = len(faces)

    # 🟢 Face Count
    cv2.putText(frame, f"Faces: {count}", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    # 🔴 Alert System
    if count > 0:
        cv2.putText(frame, "ALERT: Face Detected!", (10,70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    else:
        cv2.putText(frame, "No Face", (10,70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

    # ⏱️ Time Display
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, current_time, (10,110),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)

    # Draw faces
    for i, (x, y, w, h) in enumerate(faces):

        # Confidence %
        confidence = int(weights[i] * 100)
        if confidence > 100:
            confidence = 100

        # Face box
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

        # Label
        cv2.putText(frame, "Human Detected", (x, y-30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # Confidence text
        cv2.putText(frame, f"{confidence}%", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.imshow("Smart Face Monitoring System", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()