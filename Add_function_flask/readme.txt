codigo para subir actualizaciones a un dispisitivo de forma remota
se utiliza una jetson nano como dispositivo para actualizar el script que corre
el codigo servidor.py corre en la jetson nano
asegurarse de instalar flask primero

los comandos a ejecutar en el equipo gestor de actualizaciones (rasp Pi en este caso)
se ven en el archivo commands.txt

los comandos se pueden ejecutar desde cualquier pc linux, sin instalar nada

antes de subir actualizaciones verificar la ip de la jetson

ambos equipos (gestor y cliente) deben estar en la misma red o usar vpn

para ejecutar los commands en el equipo gestor de actualizaciones, se debe estar
en el mismo directorio donde se ubican los scripts de actualizaciones
