# Arquitectura propuesta para desacoplamiento y resiliencia del sistema

Región de operación: us-east-2 (Ohio).

1.  **`NotificacionesDLQ`:** Dead Letter Queue para manejo de errores.
2.  **`EmailQueue`:** Cola estándar para correos (vinculada a la DLQ).
3.  **`SMSQueue`:** Cola estándar para SMS (vinculada a la DLQ).
4.  **`PushQueue`:** Cola estándar para notificaciones Push (vinculada a la DLQ).

*Configuración de Redrive Policy:* `Maximum Receives = 3`.

<img width="1650" height="323" alt="image" src="https://github.com/user-attachments/assets/40a2691e-0126-4901-93a3-39968b3e055d" />
