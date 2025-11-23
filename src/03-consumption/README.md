# Capa 3: Consumo y Ejecución (El Ejecutor)

Esta capa contiene la lógica de negocio del sistema. Los "Consumidores" (Lambdas) leen de los buffers (SQS), ejecutan el envío a través de proveedores externos (SES/SNS) y garantizan la trazabilidad.

## Arquitectura de Consumo

### 1. Pattern: Competing Consumers
Se implementaron funciones AWS Lambda disparadas por eventos SQS (`SQS Trigger`).
* **Batch Size:** 10 mensajes por invocación para eficiencia.
* **Report Batch Item Failures:** Habilitado para asegurar que si un mensaje falla en un lote, solo ese mensaje retorna a la cola (evitando re-procesamiento innecesario de mensajes exitosos).

### 2. Canales Implementados

| Canal | Estado | Proveedor | Detalles de Implementación |
| :--- | :--- | :--- | :--- |
| **EMAIL** | **Producción** | Amazon SES | Envío real a correos verificados. Manejo de errores de SES. |
| **SMS** | **Mock (Simulado)** | Amazon SNS | Lógica completa implementada pero envío final "mockeado" debido a restricciones de Sandbox en cuenta nueva. Registra estado `SENT_MOCK`. |
| **PUSH** | **Mock (Simulado)** | N/A | Simulación de envío a FCM/APNs. Registra token de dispositivo y estado `SENT_MOCK_PUSH`. |

### 3. Persistencia y Auditoría
Se utiliza **Amazon DynamoDB** como fuente única de verdad para el estado de las notificaciones.
* **Tabla:** `Project_Notifications_System_Audit`
* **Estrategia:** Cada Lambda escribe un registro inmutable tras el intento de envío.
* **Streams:** Se habilitó *DynamoDB Streams (New Image)* para permitir que futuros componentes de analítica consuman estos registros en tiempo real sin impactar el rendimiento de la escritura.

## Manejo de Errores
Se implementó bloques `try/catch` granulares por mensaje.
1. **Error de Datos (Validación):** Se registra en logs y se descarta (no se reintenta).
2. **Error Transitorio (Red/Servicio):** Se marca el ID del mensaje en `batchItemFailures` para que SQS aplique su política de reintentos (Redrive Policy) y, eventualmente, lo mueva a la DLQ.
