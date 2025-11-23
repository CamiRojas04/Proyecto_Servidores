# Creación de la regla RoutingRule-SMS

<img width="1585" height="78" alt="image" src="https://github.com/user-attachments/assets/a37c0a28-c867-4539-8756-897ec1dfd905" />

Se implementa un patrón de eventos personalizado:

{
  "source": ["com.proyecto.notificaciones"],
  "detail-type": ["NotificacionRequest"],
  "detail": {
    "type": ["SMS"]
  }
}

<img width="1296" height="536" alt="image" src="https://github.com/user-attachments/assets/7973d4f6-f8fa-4a6e-848e-df27ac8d47b9" />

Configuración de la entrada de destino como transformador de entrada y uso de cola Notificaciones_DLQ para mensajes fallidos.

<img width="1290" height="575" alt="image" src="https://github.com/user-attachments/assets/772c9837-ac71-4891-b2b7-eee3864386b6" />

Además, se fijan los parámetros de ruta de entrada y plantilla del transformador:

<img width="820" height="879" alt="image" src="https://github.com/user-attachments/assets/00e47994-f632-46f2-aced-452342d97e62" />



