import serial
import time
from ultralytics import YOLO
import torch
import cv2
import numpy as np
import matplotlib.path as mlpPath

# Inicializar puerto serial
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)  # Espera a que el Arduino se reinicie
except Exception as e:
    print("Error al abrir el puerto serial:", e)
    arduino = None

# Verificar si CUDA está disponible
print("")
print("")
print('Disponibilidad de CUDA con torch: ', torch.cuda.is_available())
print('Disponibilidad de CUDA con cv2: ', cv2.cuda.getCudaEnabledDeviceCount() > 0)
print("")
print("")

# Cargar el modelo YOLO
model = YOLO("yolov8n.pt")

video_path = '0'  # o tu archivo .mp4
#video_path = '/home/nano/Desktop/util/yolo/citec017.mp4'

car_class_id = 2

tracker_config = {
    'tracker': "bytetrack.yaml",
    'show': False,
    'save': False,
    'save_txt': False,
    'imgsz': 640,
    'conf': 0.4,
    'iou': 0.5,
    'agnostic_nms': True,
    'device': '0',
    'stream': True
}

#zone = np.array([
#    [609, 435],
#    [612, 605],
#    [925, 621],
#    [916, 432],
#    [604, 420]
#])

zone = np.array([[205, 185],
[185, 585],
[1052, 594],
[1015, 181],
[219, 176]])

def get_bboxes(det: object):
    if len(det) == 0:
        return None
    xyxy = det.xyxy[0].cpu().numpy()
    class_id = int(det.cls[0].cpu().numpy())
    if class_id == car_class_id:
        return xyxy.astype(int)
    return None

def get_center(bbox):
    if bbox is None:
        return None, None
    center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
    return center

def is_valid_detection(xc, yc):
    return mlpPath.Path(zone).contains_point((xc,yc))

def get_id(det: object):
    if det.id is None:
        return None
    return int(det.id[0].cpu().numpy())

tracked_ids = []
last_sent = time.time()  # tiempo de última vez que se envió por serial

try:
    for result in model.track(source=video_path, **tracker_config):
        frame = result.orig_img
        cv2.polylines(frame, pts=[zone], isClosed=True, color=(255, 0, 0), thickness=2)
        
        detections = 0
        frame_ids = []

        for det in result.boxes:
            bboxes = get_bboxes(det)
            if bboxes is not None:
                xc, yc = get_center(bboxes)
                if is_valid_detection(xc, yc):
                    detections += 1

                    obj_id = get_id(det)
                    if obj_id is not None and obj_id not in frame_ids:
                        frame_ids.append(obj_id)

                cv2.rectangle(frame, (int(bboxes[0]), int(bboxes[1])), (int(bboxes[2]), int(bboxes[3])), (0, 255, 0), 2)
                cv2.circle(frame, center=(xc, yc), radius=5, color=(0, 0, 255), thickness=2)

        print("Cars detected: ", detections)
        print("Tracked IDs in this frame:", frame_ids)
        
        for obj_id in frame_ids:
            if obj_id not in tracked_ids:
                tracked_ids.append(obj_id)

        print("Total unique vehicles detected: ", len(tracked_ids))
        print("")

        # Enviar cada 10 segundos por puerto serie
        if time.time() - last_sent > 60:
            if arduino and arduino.is_open:
                mensaje = f"Total vehiculos detectados: {len(tracked_ids)}\n"
                arduino.write(mensaje.encode())
                print(f"Enviado por serial: {mensaje.strip()}")
            last_sent = time.time()

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrumpido por el usuario")

finally:
    if arduino and arduino.is_open:
        arduino.close()
        print("Puerto serial cerrado correctamente")
    cv2.destroyAllWindows()

