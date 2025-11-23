#  Bitácora Técnica: Sistema de Notificaciones Multi-Canal (Event-Driven Architecture)

Autores: `María Camila Rojas Herrera / Sebastián Sierra Rivera`

Fecha de Inicio: `Noviembre 2025`

Región Principal (Lógica): `us-east-2 (Ohio)`

Región Secundaria (Facturación): `us-east-1 (N. Virginia)`


## 1. Fase de Gobierno y Control de Costos (Capa 0)

Antes de desplegar la infraestructura de la aplicación, se implementaron controles de seguridad financiera y acceso para garantizar la sostenibilidad del proyecto en la capa gratuita de AWS.

* **Métrica Monitoreada:** `EstimatedCharges` (Moneda: USD).
* **Umbral de Alerta:** $15.00 USD.
* **Acción:** Notificación inmediata vía Amazon SNS al correo electrónico del administrador.
* **Estado:** Suscripción confirmada.





---
