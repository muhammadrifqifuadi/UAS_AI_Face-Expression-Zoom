import cv2
import numpy as np
import pyvirtualcam
from pyvirtualcam import PixelFormat
import time
import sys
import os
import mss
import pygetwindow as gw
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from keras.models import load_model
from src.logger import log_expression
from src.alerts import check_confusion_alert

zoom_path = r"C:\Users\MSI GF63\AppData\Roaming\Zoom\bin\Zoom.exe"
try:
    os.startfile(zoom_path)
    print("📞 Membuka Zoom...")
    time.sleep(5)
except Exception as e:
    print(f"⚠️ Gagal membuka Zoom: {e}")

model = load_model('Model/expression_model.h5')
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
confused_labels = ['Angry', 'Fear', 'Sad']

color_map = {
    'Angry': (0, 0, 255),
    'Disgust': (0, 255, 0),
    'Fear': (0, 255, 255),
    'Happy': (255, 255, 0),
    'Sad': (255, 0, 0),
    'Surprise': (255, 0, 255),
    'Neutral': (200, 200, 200)
}

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

zoom_window = None
for w in gw.getWindowsWithTitle('Zoom'):
    if w.visible and w.width > 100 and w.height > 100:
        zoom_window = w
        break

if zoom_window:
    monitor = {
        "top": zoom_window.top,
        "left": zoom_window.left,
        "width": zoom_window.width,
        "height": zoom_window.height
    }
    print(f"🖥️ Deteksi Zoom window: {monitor}")
else:
    monitor = {"top": 100, "left": 100, "width": 1280, "height": 720}
    print("⚠️ Zoom window tidak ditemukan, pakai area default.")

# Mulai virtual camera
with mss.mss() as sct:
    with pyvirtualcam.Camera(width=monitor["width"], height=monitor["height"], fps=30, fmt=PixelFormat.BGR) as cam:
        print(f'✅ Virtual camera aktif: {cam.device}')
        last_alert_time = 0
        alert_cooldown = 10
        try:
            while True:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                detected_expressions = []

                for (x, y, w, h) in faces:
                    face = gray[y:y + h, x:x + w]
                    face = cv2.resize(face, (48, 48))
                    face = face / 255.0
                    face = np.expand_dims(face, axis=-1)
                    face = np.expand_dims(face, axis=0)

                    prediction = model.predict(face, verbose=0)
                    emotion = emotion_labels[np.argmax(prediction)]
                    detected_expressions.append(emotion)

                    color = color_map.get(emotion, (255, 255, 255))
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                log_expression(detected_expressions)

                if time.time() - last_alert_time > alert_cooldown:
                    if check_confusion_alert(detected_expressions):
                        print("⚠️ Banyak siswa terlihat bingung!")
                        last_alert_time = time.time()

                frame = cv2.flip(frame, 1)
                cam.send(frame)
                cam.sleep_until_next_frame()

        except KeyboardInterrupt:
            print("berhenti")
        except Exception as e:
            print(f"💥 Terjadi error: {e}")
        finally:
            cv2.destroyAllWindows()
            print("👋 Virtual camera dimatikan.")
