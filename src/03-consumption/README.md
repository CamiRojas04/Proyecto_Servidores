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
* **Streams:** Se habilitó *DynamoDB Streams (New Image)* para permitir que futuros componentes de analítica consuman estos registros en tiempo real.

## Manejo de Errores
Se implementó bloques `try/catch` granulares por mensaje.
1. **Error de Datos (Validación):** Se registra en logs y se descarta.
2. **Error Transitorio (Red/Servicio):** Se marca el ID del mensaje en `batchItemFailures` para que SQS aplique su política de reintentos y, eventualmente, lo mueva a la DLQ.

---

## 📸 Evidencias Gráficas

### 1. Auditoría de Envío Exitoso (Canal Email)
Registro en DynamoDB confirmando el envío real de un correo electrónico a través de Amazon SES.
> **Estado:** `SENT`
>
> ![Auditoría Email](../../docs/layer-3/dynamodb-email-audit.png)

*(Nota: Corresponde a tu captura `image_b444b3.png`)*

### 2. Validación de Mocking (Canal SMS)
Evidencia de la estrategia de simulación para el canal SMS. El sistema procesó el evento pero registró el estado simulado debido a restricciones de Sandbox.
> **Estado:** `SENT_MOCK`
>
> ![Auditoría SMS Mock](../../docs/layer-3/dynamodb-sms-mock.png)

*(Nota: Corresponde a tu captura `image_2e789f.png`)*

### 3. Trazabilidad y Logs (CloudWatch)
Registro detallado de la ejecución de la Lambda, mostrando el procesamiento del evento y la captura de errores (durante la fase de depuración).
> **Detalle:** Logs de ejecución y excepciones controladas.
>
> ![Logs CloudWatch](../../docs/layer-3/lambda-cloudwatch-logs.jpg)
