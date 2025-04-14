from ultralytics import YOLO
import torch
import cv2
import numpy as np
import matplotlib.path as mlpPath

# Verificar si CUDA está disponible
print("")
print("")
print('Disponibilidad de CUDA con torch: ', torch.cuda.is_available())
print('Disponibilidad de CUDA con cv2: ', cv2.cuda.getCudaEnabledDeviceCount() > 0)
print("")
print("")

# Cargar el modelo YOLO
model = YOLO("yolov8n.pt")  # Cambia a otro modelo si es necesario (yolov8m.pt, yolov8l.pt)

# Ruta del video de entrada (puede ser '0' para cámara en vivo o ruta de un video .mp4)
#video_path = "rtsp://admin:E10ADC3949BA59ABBE56E057F20F883E@192.168.20.251:554/mpeg4"
video_path = '0'
#video_path = '/home/nano/Desktop/util/yolo/citec017.mp4'

# ID de la clase para automóviles (en el conjunto de datos COCO, los automóviles tienen ID 2)
car_class_id = 2

# Configuración del tracker
tracker_config = {
    'tracker': "bytetrack.yaml",  # Usa 'botsort.yaml' o 'bytetrack.yaml'
    'show': False,                 # Mostrar resultados en tiempo real
    'save': False,                 # No guardar resultados
    'save_txt': False,             # No guardar detecciones en archivos .txt
    'imgsz': 640,                  # Tamaño de la imagen
    'conf': 0.4,                   # Umbral de confianza
    'iou': 0.5,                    # Umbral de IOU para el tracking
    'agnostic_nms': True,          # NMS agnóstico de clase
    'device': '0',                 # Usar la GPU
    'stream': True                 # Usar streaming en tiempo real
}

zone = np.array([
    [609, 435],
    [612, 605],
    [925, 621],
    [916, 432],
    [604, 420]
])





def get_bboxes(det: object):
    # Verificar si hay detecciones
    if len(det) == 0:
        return None  # Si no hay detecciones, retornar None

    # Obtener las coordenadas del tensor
    xyxy = det.xyxy[0].cpu().numpy()
    class_id = int(det.cls[0].cpu().numpy())

    # Si la clase es un automóvil (ID 2 en COCO)
    if class_id == car_class_id:
        return xyxy.astype(int)  # Retornar las coordenadas como enteros

    return None  # Si no es un automóvil, retornar None

def get_center(bbox):
    if bbox is None:
        return None, None  # Si no hay bbox, retornar None, None
    center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
    return center

def is_valid_detection(xc, yc):
    return mlpPath.Path(zone).contains_point((xc,yc))

def get_id(det: object):
    # Verificar si el ID está presente en la detección
    if det.id is None:
        return None  # Si no hay ID, retornar None
    return int(det.id[0].cpu().numpy())
    

tracked_ids = []  # Lista para almacenar los IDs de objetos detectados

# Realizar el seguimiento de objetos en el video
for result in model.track(source=video_path, **tracker_config):  # Iterar sobre los resultados de cada fotograma
    frame = result.orig_img  # Imagen original del frame
    cv2.polylines(frame, pts=[zone], isClosed=True, color=(255, 0, 0), thickness=2)
    
    detections = 0
    frame_ids = []  # Lista para almacenar los IDs en este fotograma

    for det in result.boxes:  # Las detecciones están en result.boxes
        bboxes = get_bboxes(det)
        
        # Verificar si bboxes no es None
        if bboxes is not None:
            xc, yc = get_center(bboxes)
            if is_valid_detection(xc, yc):
                detections += 1

                obj_id = get_id(det)
                if obj_id is not None and obj_id not in frame_ids:
                    frame_ids.append(obj_id)  # Agregar el ID de este fotograma solo si no está duplicado

            # Dibujar la caja delimitadora
            cv2.rectangle(frame, (int(bboxes[0]), int(bboxes[1])), (int(bboxes[2]), int(bboxes[3])), (0, 255, 0), 2)
            cv2.circle(frame, center=(xc, yc), radius=5, color=(0, 0, 255), thickness=2)

    # Mostrar los resultados de los IDs rastreados en el fotograma actual
    print("Cars detected: ", detections)
    print("Tracked IDs in this frame:", frame_ids)  # Mostrar los IDs para este fotograma
    
    # Agregar solo los IDs que aún no están en tracked_ids
    for obj_id in frame_ids:
        if obj_id not in tracked_ids:
            tracked_ids.append(obj_id)  # Agregar el ID solo si no está duplicado

    #print("Tracked IDs (global):", tracked_ids)  # Mostrar todos los IDs rastreados hasta ahora
    print("Total unique vehicles detected: ", len(tracked_ids))
    print("")
    
    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Permitir salir con 'q'
        break

cv2.destroyAllWindows()

