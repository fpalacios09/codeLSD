import serial
import time

try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)

    while True:
        arduino.write(b'Hola Arduino\n')
        print("Mensaje enviado a Arduino")
        time.sleep(1)

except KeyboardInterrupt:
    print("Interrumpido por el usuario")

finally:
    if arduino.is_open:
        arduino.close()
        print("Puerto cerrado correctamente")

