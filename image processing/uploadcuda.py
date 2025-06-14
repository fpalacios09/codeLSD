import cv2
import cv2.cuda

img = cv2.imread("autos.png", cv2.IMREAD_GRAYSCALE)
src = cv2.cuda_GpuMat()
src.upload(img)
 
clahe = cv2.cuda.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
dst = clahe.apply(src, cv2.cuda_Stream.Null())
 
result = dst.download()
 
cv2.imshow("result", result)
cv2.waitKey(0)