
# Creación de la regla RoutingRule-Email-v2

<img width="1581" height="86" alt="image" src="https://github.com/user-attachments/assets/8453932b-c085-4a5b-b3b9-31e71f941eca" />



Se implementa un patrón de eventos personalizado:

<img width="1325" height="660" alt="image" src="https://github.com/user-attachments/assets/d12aa3bb-63d4-41ef-9b6a-10fd3345936e" />


Con el código JSON

{
  "source": ["com.proyecto.notificaciones"],
  "detail-type": ["NotificacionRequest"],
  "detail": {
    "type": ["PUSH"]
  }
}

<img width="1308" height="524" alt="image" src="https://github.com/user-attachments/assets/e172eb89-cf27-4412-aebd-06ef4756e8a1" />


Configuración de la entrada de destino como transformador de entrada y uso de cola Notificaciones_DLQ para mensajes fallidos.

<img width="1290" height="575" alt="image" src="https://github.com/user-attachments/assets/772c9837-ac71-4891-b2b7-eee3864386b6" />

Además, se fijan los parámetros de ruta de entrada y plantilla del transformador:

<img width="789" height="743" alt="image" src="https://github.com/user-attachments/assets/680b8925-eb9b-4152-9b42-ea02ec9fcca1" />



