# Creación de la regla RoutingRule-Email-v2

<img width="1580" height="69" alt="image" src="https://github.com/user-attachments/assets/3bf952cd-1491-4e6f-90d1-4b89267f5322" />


Se implementa un patrón de eventos personalizado:

<img width="1307" height="534" alt="image" src="https://github.com/user-attachments/assets/fe433455-3847-4e0f-9e39-8b524e9cba6e" />

Con el código JSON

{
  "source": ["com.proyecto.notificaciones"],
  "detail-type": ["NotificacionRequest"],
  "detail": {
    "type": ["EMAIL"]
  }
}

<img width="1281" height="520" alt="image" src="https://github.com/user-attachments/assets/04692d02-8ee9-4614-85ff-37532132231d" />

Configuración de la entrada de destino como transformador de entrada y uso de cola Notificaciones_DLQ para mensajes fallidos.

<img width="1290" height="575" alt="image" src="https://github.com/user-attachments/assets/772c9837-ac71-4891-b2b7-eee3864386b6" />

Además, se fijan los parámetros de ruta de entrada y plantilla del transformador:

<img width="822" height="895" alt="image" src="https://github.com/user-attachments/assets/37bf0a11-62de-4b9f-a2f5-c8730172aa3c" />



