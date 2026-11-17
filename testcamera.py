import cv2

print("STARTING CAMERA TEST...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera NOT opened")
else:
    print("✅ Camera opened")

while True:
    ret, frame = cap.read()

    if not ret:
        print("❌ Frame not received")
        break

    print("Frame running...")  # DEBUG LINE

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) == 27:
        print("ESC pressed, closing...")
        break

cap.release()
cv2.destroyAllWindows()