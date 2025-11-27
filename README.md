# Proyecto_Servidores
Creación de un sistema de notificaciones multicanal utilizando una arquitectura dirigida por eventos

# Pendiente
Describe el Objetivo Principal (ser una plataforma resiliente y desacoplada).
Incluye la descripción de las Tres Capas (Ingestión, Enrutamiento/Buffer, Consumo) y la función de cada componente (API Gateway, EventBridge, SQS, SES, SNS, DynamoDB).
Haz un Commit: Guarda este archivo con un mensaje de commit claro, como: feat: Documentación inicial de la arquitectura y componentes (Capa 1, 2 y 3).

#Objetivo Principal:
El propósito fundamental de este proyecto es desarrollar una plataforma de notificaciones que soporte múltiples canales (Email, SMS, Push) a través de un diseño Serverless de AWS basado en el patrón de Arquitectura Dirigida por Eventos (EDA). El objetivo central se basa en dos pilares de la arquitectura de AWS:

- Desacoplamiento Completo: Garantizar que los componentes de envío no tengan dependencia directa con el componente que genera la        solicitud.

- Resiliencia y Escalabilidad: Asegurar que el sistema pueda manejar picos de tráfico y que el fallo de un servicio externo (ej. SES o   un proveedor de SMS) no cause la pérdida de mensajes ni la saturación de los componentes anteriores. Esto se logra mediante el uso     de colas SQS como búferes de mensajes.

# Descripción de la arquitectura y capas del proyecto:

La arquitectura se divide en un flujo lineal de tres capas que transforman una solicitud HTTP en una notificación entregada y registrada.

1. Capa de Ingestión y Producción:
   Esta capa es la entrada pública del sistema y es responsable de la validación inicial y la emisión del evento.

   <img width="521" height="400" alt="image" src="https://github.com/user-attachments/assets/de3a2863-a8bc-4f01-ab11-c387b5bfd8f4" />
