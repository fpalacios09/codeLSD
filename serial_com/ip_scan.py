import scapy.all as scapy
import time

def escanear_red(rango_ip):
    """
    Función para escanear la red y encontrar dispositivos activos.
    :param rango_ip: Rango de IPs a escanear (ej. "192.168.20.1/24")
    :return: lista de dispositivos activos
    """
    # Generar una solicitud ARP para el rango de IPs
    solicitud_arp = scapy.ARP(pdst=rango_ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    paquete = broadcast/solicitud_arp
    
    # Enviar los paquetes ARP y obtener las respuestas
    respuestas = scapy.srp(paquete, timeout=1, verbose=False)[0]
    
    dispositivos = []
    
    # Procesar las respuestas y almacenar las direcciones IP y MAC
    for respuesta in respuestas:
        dispositivo = {
            "ip": respuesta[1].psrc,
            "mac": respuesta[1].hwsrc
        }
        dispositivos.append(dispositivo)
    
    return dispositivos

def imprimir_dispositivos(dispositivos):
    """
    Imprime la lista de dispositivos conectados a la red.
    """
    print("Dispositivos activos en la red:")
    for dispositivo in dispositivos:
        print(f"IP: {dispositivo['ip']} - MAC: {dispositivo['mac']}")

# Rango de IP a escanear (ajusta el rango según tu red)
rango_ip = "192.168.20.1/24"

while True:
    # Realizar el escaneo de la red
    dispositivos = escanear_red(rango_ip)
    
    # Imprimir los dispositivos encontrados
    imprimir_dispositivos(dispositivos)
    
    # Esperar 5 segundos antes de volver a escanear
    time.sleep(5)

