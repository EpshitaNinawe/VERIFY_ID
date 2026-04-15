import cv2
import mediapipe as mp
import numpy as np
import pytesseract
import re

#tesseract path(change it according to your path)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# mediapipe facemesh
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# =========================
# FACE UTILITIES
# =========================

def get_face_landmarks_and_bbox(image):
    h, w, _ = image.shape
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return None, None

    xs, ys, landmarks = [], [], []

    for lm in results.multi_face_landmarks[0].landmark:
        x, y = int(lm.x * w), int(lm.y * h)
        xs.append(x)
        ys.append(y)
        landmarks.extend([lm.x, lm.y, lm.z])

    return np.array(landmarks), (min(xs), min(ys), max(xs), max(ys))


def extract_face(image, bbox, margin=20):
    x1, y1, x2, y2 = bbox
    h, w, _ = image.shape

    x1 = max(0, x1 - margin)
    y1 = max(0, y1 - margin)
    x2 = min(w, x2 + margin)
    y2 = min(h, y2 + margin)

    return image[y1:y2, x1:x2]


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

#pan OCR check
def is_pan_card(image):
    image = cv2.resize(image, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    text = pytesseract.image_to_string(gray, config="--oem 3 --psm 6")
    text = text.upper()

    pan_regex = r"[A-Z]{5}\d{4}[A-Z]"

    if "INCOME TAX" in text or "GOVT OF INDIA" in text:
        return True

    return bool(re.search(pan_regex, text.replace(" ", "")))

#load uploaded document

uploaded_doc = cv2.imread("uploaded_document.jpg")
if uploaded_doc is None:
    raise Exception("Uploaded document image not found")

doc_landmarks, doc_bbox = get_face_landmarks_and_bbox(uploaded_doc)
if doc_landmarks is None:
    raise Exception("No face detected in uploaded document")

doc_face = extract_face(uploaded_doc, doc_bbox)
cv2.imwrite("document_face.jpg", doc_face)

print("Document face extracted")

# live camera
cap = cv2.VideoCapture(0)

state = "WAITING_FOR_PAN"
pan_landmarks = None

THRESHOLD = 0.70

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # live face
    live_landmarks, live_bbox = get_face_landmarks_and_bbox(frame)
    if live_bbox:
        live_face = extract_face(frame, live_bbox)
        cv2.imwrite("live_face.jpg", live_face)
        x1, y1, x2, y2 = live_bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # pan scan region
    px1, py1 = int(w * 0.2), int(h * 0.45)
    px2, py2 = int(w * 0.8), int(h * 0.85)
    pan_crop = frame[py1:py2, px1:px2]

    if state == "WAITING_FOR_PAN":
        cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 255, 255), 2)
        cv2.putText(frame, "Place PAN Card",
                    (px1, py1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        if is_pan_card(pan_crop):
            pan_landmarks, pan_bbox = get_face_landmarks_and_bbox(pan_crop)
            if pan_landmarks is not None:
                pan_face = extract_face(pan_crop, pan_bbox)
                cv2.imwrite("pan_face.jpg", pan_face)
                print("PAN face extracted")
                state = "COMPARING"

    elif state == "COMPARING":
        if live_landmarks is not None:
            sim_live_pan = cosine_similarity(live_landmarks, pan_landmarks)
            sim_live_doc = cosine_similarity(live_landmarks, doc_landmarks)
            sim_pan_doc = cosine_similarity(pan_landmarks, doc_landmarks)

            print(f"Live-PAN: {sim_live_pan:.2f}")
            print(f"Live-DOC: {sim_live_doc:.2f}")
            print(f"PAN-DOC : {sim_pan_doc:.2f}")

            if (
                sim_live_pan > THRESHOLD and
                sim_live_doc > THRESHOLD and
                sim_pan_doc > THRESHOLD
            ):
                cv2.putText(frame, "VALID",
                            (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.imshow("KYC Verification", frame)
                cv2.waitKey(2000)
                break
            else:
                cv2.putText(frame, "INVALID",
                            (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                cv2.imshow("KYC Verification", frame)
                cv2.waitKey(2000)
                state = "WAITING_FOR_PAN"

    cv2.putText(frame, f"STATE: {state}",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("KYC Verification", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()