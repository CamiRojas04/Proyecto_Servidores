# Capa 2: Enrutamiento y Buffer (EventBridge + SQS)

Esta capa es responsable de la **inteligencia de distribución** y la **resiliencia** del sistema. Garantiza que cada mensaje llegue al procesador correcto y que no se pierdan datos ante picos de tráfico.

## Componentes

### 1. Amazon EventBridge (El Router)
Actúa como el bus de eventos central. Utiliza reglas basadas en el contenido del mensaje (`type`) para dirigir el tráfico.
* **Bus:** `default`
* **Reglas:** 3 reglas activas (Email, SMS, Push).
* **Transformación:** Se aplica un *Input Transformer* para limpiar el JSON antes de la entrega, eliminando los metadatos de AWS ("envelope") y entregando solo el payload útil.

### 2. Amazon SQS (El Buffer)
Cada canal tiene su propia cola dedicada, lo que permite que los consumidores escalen de forma independiente (Pattern: *Queue-Based Load Leveling*).

| Canal | Cola Principal | Configuración de Seguridad |
| :--- | :--- | :--- |
| **EMAIL** | `Email_Queue` | Encriptación SSE-SQS + Política de Acceso Estricta |
| **SMS** | `SMSQueue` | Encriptación SSE-SQS + Política de Acceso Estricta |
| **PUSH** | `PushQueue` | Encriptación SSE-SQS + Política de Acceso Estricta |

### 3. Dead Letter Queue (DLQ)
* **Cola:** `NotificacionesDLQ`
* **Función:** Captura mensajes que no pudieron ser procesados tras 3 intentos fallidos o errores de enrutamiento en EventBridge.
* **Uso en Desarrollo:** Fue fundamental para diagnosticar errores de formato JSON (`INVALID_JSON`) durante la integración.

## Estrategia de Seguridad
1. **Encriptación en Reposo:** Se migró de KMS a **SSE-SQS** para facilitar la integración transparente con EventBridge sin comprometer la seguridad de los datos.
2. **Principio de Mínimo Privilegio:** Las políticas de acceso de SQS (`AccessPolicy`) solo permiten la escritura (`sqs:SendMessage`) al servicio `events.amazonaws.com` y únicamente si la petición proviene de la regla ARN específica de este proyecto.
