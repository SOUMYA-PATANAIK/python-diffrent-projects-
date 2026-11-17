import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    text = ""

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                h, w, _ = img.shape
                lm_list.append((int(lm.x * w), int(lm.y * h)))

            # Points
            thumb = lm_list[4]
            index = lm_list[8]
            middle = lm_list[12]
            wrist = lm_list[0]

            # 👍 THUMB UP → YES
            if thumb[1] < index[1] and thumb[1] < middle[1]:
                text = "YES 👍"

            elif index[1] < wrist[1] and middle[1] < wrist[1] and lm_list[8][1] < lm_list[12][1]:
                text = "PEACE ✌️"

                
            # ✋ OPEN HAND → HELLO
            elif index[1] < wrist[1] and middle[1] < wrist[1]:
                text = "HELLO ✋"
            

            # ✊ FIST → NO
            elif index[1] > wrist[1] and middle[1] > wrist[1]:
                text = "NO ✊"

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    cv2.putText(img, text, (50,100),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 3)

    cv2.imshow("Sign Language", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()