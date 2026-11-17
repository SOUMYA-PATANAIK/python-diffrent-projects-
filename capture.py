import cv2

cap = cv2.VideoCapture(0)

count = 0

while True:
    ret, frame = cap.read()

    cv2.imshow("Capture Image", frame)

    key = cv2.waitKey(1)

    # Press 's' to save
    if key == ord('s'):
        cv2.imwrite(f"soumya_{count}.jpg", frame)
        print("Image saved 😎")
        count += 1

    # ESC to exit
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()