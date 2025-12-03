# Bitácora Técnica: Sistema de Notificaciones Multi-Canal (Event-Driven Architecture)

**Autor-1:** María Camila Rojas Herrera 

**Autor-2:** Sebastián Sierra Rivera

**Fecha de Inicio:** Noviembre 2025  

**Región Principal (Lógica):** `us-east-2` (Ohio)  

**Región Secundaria (Facturación):** `us-east-1` (N. Virginia)

---

## 1. Fase de Gobierno y Control de Costos (Capa 0)

Antes de desplegar la infraestructura de la aplicación, se implementaron controles de seguridad financiera y acceso para garantizar la sostenibilidad del proyecto en la capa gratuita de AWS.

### 1.1. Alarma de Facturación (FinOps)
Se configuró una alarma en **Amazon CloudWatch** para monitorear proactivamente los costos estimados de la cuenta.

* **Métrica:** `EstimatedCharges` (Moneda: USD).
* **Umbral:** ≥ $15.00 USD.
* **Acción:** Notificación inmediata vía Amazon SNS al correo electrónico del administrador.
* **Estado:** Suscripción confirmada.

> **Evidencia de Configuración:**
> Creación de la suscripción al tema SNS `AlarmaPresupuesto20USD`.

<img width="1603" height="503" alt="image" src="https://github.com/user-attachments/assets/3b9ccaf2-8c10-485f-b6f4-61c25c6994ca" />


### 1.2. Gestión de Identidad (IAM)
Se estableció un esquema de colaboración seguro utilizando el principio de mínimo privilegio.

* **Grupo IAM:** `Desarrolladores-Notificaciones-EDA`.
* **Políticas Adjuntas:** Acceso limitado a los servicios SQS, Lambda, DynamoDB y SES necesarios para el desarrollo.
* **Usuarios:** Creación de usuarios IAM individuales para evitar el uso de la cuenta raíz.

---

## 2. Capa 1: Ingestión Pública (El Frontend & API)

Se implementó la capa de entrada pública para exponer el sistema como un microservicio accesible vía HTTP.

### 2.1. Componentes de Ingestión
* **Amazon API Gateway (HTTP API):** Expone el endpoint `POST /send` y `GET /`.
* **Lambda Producer (`ProducerLambda`):**
    * **Rol IAM:** `ProducerRole` con permiso `events:PutEvents` restringido al bus `default`.
    * **Lógica:** Implementa un patrón dual (API Backend + Web Frontend).
 
#### Código Fuente del Productor (`ProducerLambda`)
El siguiente código implementa la lógica híbrida que sirve la interfaz web y procesa las notificaciones:

import json
import boto3
import time
import uuid
import os 

# Clientes AWS
events = boto3.client('events')
ses = boto3.client('ses')
sns = boto3.client('sns') # Necesario para la verificación de SMS

def lambda_handler(event, context):
    # Detectar método HTTP (compatible con API Gateway HTTP API y REST API)
    http_method = 'UNKNOWN'
    if 'requestContext' in event:
        if 'http' in event['requestContext']:
            http_method = event['requestContext']['http']['method']
        elif 'httpMethod' in event['requestContext']:
            http_method = event['requestContext']['httpMethod']
        elif 'httpMethod' in event:
            http_method = event['httpMethod']

    # ------------------------------------------------------------------
    # 1. FRONTEND: Interfaz Web con Flujo de 2 Pasos (GET)
    # ------------------------------------------------------------------
    if http_method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sistema EDA Multi-Canal</title>
                <style>
                    :root { --color-primary: #FF9900; --color-secondary: #232F3E; --color-success: #28a745; --color-bg: #f5f5f5; --color-card-bg: #ffffff; --color-text: #333333; }
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--color-bg); display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
                    .card { background: var(--color-card-bg); padding: 30px; border-radius: 8px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); width: 100%; max-width: 450px; box-sizing: border-box; }
                    .header { border-bottom: 2px solid var(--color-primary); padding-bottom: 10px; margin-bottom: 20px; }
                    h2 { color: var(--color-secondary); margin: 0 0 5px 0; font-weight: 600; }
                    .subtitle { color: var(--color-primary); font-size: 0.9em; font-weight: 500; }
                    .form-group { margin-bottom: 15px; }
                    label { display: block; text-align: left; margin-bottom: 5px; font-size: 0.9em; color: var(--color-text); font-weight: 600; }
                    input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; font-family: inherit; font-size: 1em; transition: border-color 0.3s; }
                    input:focus, select:focus, textarea:focus { border-color: var(--color-primary); outline: none; }
                    input:disabled { background-color: #e9ecef; cursor: not-allowed; opacity: 0.7; }
                    button { background-color: var(--color-secondary); color: white; border: none; padding: 12px; width: 100%; border-radius: 4px; cursor: pointer; font-size: 1em; font-weight: 600; margin-top: 15px; transition: background-color 0.3s; }
                    button:hover:not(:disabled) { background-color: #3f5166; }
                    button:disabled { background-color: #ccc; cursor: not-allowed; }
                    #response { margin-top: 20px; padding: 10px; border-radius: 4px; min-height: 20px; font-size: 0.95em; text-align: center; }
                    .tabs { display: flex; margin-bottom: 20px; border-bottom: 1px solid #ddd; }
                    .tab { flex: 1; padding: 10px; cursor: pointer; text-align: center; color: #666; font-weight: 600; }
                    .tab.active { border-bottom: 2px solid var(--color-primary); color: var(--color-primary); }
                    .tab-content { display: none; }
                    .tab-content.active { display: block; }
                    
                    /* Estilos para el paso 2 de SMS */
                    #otpSection { display: none; margin-top: 15px; padding-top: 15px; border-top: 1px dashed #ddd; }
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="header">
                        <h2>Sistema de Notificaciones Multi-Canal</h2>
                        <p class="subtitle">Arquitectura Dirigida por Eventos (EDA)</p>
                    </div>
                    
                    <div class="tabs">
                        <div class="tab active" onclick="switchTab('send')">Enviar</div>
                        <div class="tab" onclick="switchTab('verify')">Verificar</div>
                    </div>

                    <!-- PESTAÑA ENVIAR -->
                    <div id="send" class="tab-content active">
                        <form id="notifForm">
                            <div class="form-group">
                                <label for="channel">Canal:</label>
                                <select id="channel" onchange="toggleSubject()">
                                    <option value="EMAIL">Email (SES)</option>
                                    <option value="SMS">SMS (SNS)</option>
                                    <option value="PUSH">Push (Mock)</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="to">Destinatario:</label>
                                <input type="text" id="to" placeholder="Correo / Teléfono / Token" required>
                            </div>
                            <div class="form-group">
                                <label for="subject">Asunto (Solo Email):</label>
                                <input type="text" id="subject" placeholder="Asunto del correo">
                            </div>
                            <div class="form-group">
                                <label for="msg">Mensaje:</label>
                                <textarea id="msg" placeholder="Escribe el contenido..." rows="3" required></textarea>
                            </div>
                            <button type="submit">Enviar Notificación</button>
                        </form>
                    </div>

                    <!-- PESTAÑA VERIFICAR -->
                    <div id="verify" class="tab-content">
                        <p style="font-size:0.9em; color:#666;">Verifica identidades para salir del Sandbox.</p>
                        
                        <div class="form-group">
                            <label for="verifyType">Tipo:</label>
                            <select id="verifyType" onchange="toggleVerifyUI()">
                                <option value="EMAIL">Email Address</option>
                                <option value="SMS">Phone Number (SMS)</option>
                            </select>
                        </div>
                        
                        <form id="verifyForm">
                            <div class="form-group">
                                <label for="identityToVerify">Dato a Verificar:</label>
                                <input type="text" id="identityToVerify" placeholder="usuario@ejemplo.com" required>
                            </div>
                            
                            <button id="btnVerify" type="submit" style="background-color: #28a745;">Iniciar Verificación</button>
                            
                            <!-- SECCIÓN OCULTA PARA OTP (SMS) -->
                            <div id="otpSection">
                                <p style="font-size:0.9em; color:#d63384;"><b>¡Código enviado!</b> Revisa tu celular.</p>
                                <div class="form-group">
                                    <label for="otpCode">Código de Verificación (OTP):</label>
                                    <input type="text" id="otpCode" placeholder="123456">
                                </div>
                                <button id="btnConfirmOtp" type="button" style="background-color: #007bff;">Confirmar Código</button>
                            </div>
                        </form>
                    </div>
                    
                    <div id="response"></div>
                </div>

                <script>
                    function toggleSubject() {
                        const channel = document.getElementById('channel').value;
                        const subjectInput = document.getElementById('subject');
                        if (channel === 'EMAIL') {
                            subjectInput.disabled = false;
                            subjectInput.placeholder = "Asunto del correo";
                            subjectInput.parentElement.style.opacity = "1";
                        } else {
                            subjectInput.disabled = true;
                            subjectInput.value = "";
                            subjectInput.placeholder = "No aplica";
                            subjectInput.parentElement.style.opacity = "0.5";
                        }
                    }

                    function toggleVerifyUI() {
                        const type = document.getElementById('verifyType').value;
                        const input = document.getElementById('identityToVerify');
                        const otpSection = document.getElementById('otpSection');
                        
                        input.value = "";
                        otpSection.style.display = 'none';
                        document.getElementById('btnVerify').style.display = 'block';
                        
                        if (type === 'EMAIL') {
                            input.placeholder = "usuario@ejemplo.com";
                            input.type = "email";
                        } else {
                            input.placeholder = "+573001234567";
                            input.type = "tel";
                        }
                    }

                    function switchTab(tabId) {
                        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                        document.querySelector(`.tab[onclick="switchTab('${tabId}')"]`).classList.add('active');
                        document.getElementById(tabId).classList.add('active');
                        document.getElementById('response').innerText = '';
                        document.getElementById('response').style.backgroundColor = 'transparent';
                    }

                    // --- MANEJO DE VERIFICACIÓN (Lógica Compleja) ---
                    document.getElementById('verifyForm').addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const type = document.getElementById('verifyType').value;
                        const value = document.getElementById('identityToVerify').value;
                        
                        const btn = document.getElementById('btnVerify');
                        const respDiv = document.getElementById('response');

                        const data = {
                            action: type === 'EMAIL' ? 'VERIFY_EMAIL' : 'VERIFY_SMS_INIT',
                            value: value
                        };

                        await handleRequest(btn, respDiv, data, (result) => {
                            // Callback si es exitoso
                            if (type === 'SMS') {
                                // Si inició SMS correctamente, mostrar campo OTP
                                document.getElementById('otpSection').style.display = 'block';
                                btn.style.display = 'none'; // Ocultar botón de inicio
                                respDiv.innerText = ''; // Limpiar mensaje de éxito temporal
                                respDiv.style.backgroundColor = 'transparent';
                            }
                        });
                    });

                    // Botón Confirmar OTP
                    document.getElementById('btnConfirmOtp').addEventListener('click', async () => {
                        const btn = document.getElementById('btnConfirmOtp');
                        const respDiv = document.getElementById('response');
                        const phone = document.getElementById('identityToVerify').value;
                        const otp = document.getElementById('otpCode').value;

                        const data = {
                            action: 'VERIFY_SMS_CONFIRM',
                            phone: phone,
                            otp: otp
                        };

                        await handleRequest(btn, respDiv, data, () => {
                            // Resetear formulario al terminar
                            setTimeout(() => toggleVerifyUI(), 3000);
                        });
                    });

                    // --- MANEJO DE ENVÍO NORMAL ---
                    document.getElementById('notifForm').addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const btn = e.target.querySelector('button');
                        const respDiv = document.getElementById('response');
                        
                        const data = {
                            action: 'SEND',
                            channel: document.getElementById('channel').value,
                            to: document.getElementById('to').value,
                            subject: document.getElementById('subject').value, 
                            msg: document.getElementById('msg').value
                        };
                        handleRequest(btn, respDiv, data);
                    });

                    // --- FUNCIÓN GENÉRICA DE PETICIÓN ---
                    async function handleRequest(btn, respDiv, data, onSuccessCallback) {
                        const originalText = btn.innerText;
                        btn.disabled = true;
                        btn.innerText = '...';
                        respDiv.innerText = '';
                        respDiv.style.backgroundColor = 'transparent';

                        try {
                            // Usamos 'send' para que el navegador busque la ruta correcta en API Gateway
                            const res = await fetch('send', { 
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify(data)
                            });
                            
                            let result;
                            try { result = await res.json(); } catch(e) { result = { error: 'Error JSON' }; }
                            
                            if(res.ok) {
                                respDiv.style.backgroundColor = '#d4edda';
                                respDiv.style.color = 'var(--color-success)';
                                respDiv.innerHTML = '<b>✅ Éxito!</b><br>' + result.message;
                                if (onSuccessCallback) onSuccessCallback(result);
                            } else {
                                throw new Error(result.error || 'Error (' + res.status + ')');
                            }
                        } catch (err) {
                            respDiv.style.backgroundColor = '#f8d7da';
                            respDiv.style.color = '#721c24';
                            respDiv.innerText = '❌ ' + err.message;
                        } finally {
                            btn.disabled = false;
                            btn.innerText = originalText;
                        }
                    }
                </script>
            </body>
            </html>
            """ 
        }

    # ------------------------------------------------------------------
    # 2. BACKEND: Procesar Peticiones (POST)
    # ------------------------------------------------------------------
    print(f"Recibida solicitud {http_method}")
    
    try:
        # Parsear body
        payload = {}
        if 'body' in event:
            if event['body'] is not None:
                if isinstance(event['body'], str):
                    try:
                        payload = json.loads(event['body'])
                    except json.JSONDecodeError:
                        return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON body'})}
                else:
                    payload = event['body']
        
        # Router de Acciones
        action = payload.get('action', 'SEND') 

        # --- ACCIÓN: VERIFICAR EMAIL ---
        if action == 'VERIFY_EMAIL':
            email = payload.get('value')
            if not email: return {'statusCode': 400, 'body': json.dumps({'error': 'Falta email'})}
            ses.verify_email_identity(EmailAddress=email)
            return {'statusCode': 200, 'body': json.dumps({'message': f'Link enviado a {email}'})}

        # --- ACCIÓN: INICIAR VERIFICACIÓN SMS (Enviar OTP) ---
        if action == 'VERIFY_SMS_INIT':
            phone = payload.get('value')
            if not phone: return {'statusCode': 400, 'body': json.dumps({'error': 'Falta teléfono'})}
            # Llama a la API de Sandbox de SNS para enviar el código
            sns.create_sms_sandbox_phone_number(PhoneNumber=phone, LanguageCode='es-ES')
            return {'statusCode': 200, 'body': json.dumps({'message': 'OTP enviado al celular'})}

        # --- ACCIÓN: CONFIRMAR VERIFICACIÓN SMS (Validar OTP) ---
        if action == 'VERIFY_SMS_CONFIRM':
            phone = payload.get('phone')
            otp = payload.get('otp')
            if not phone or not otp: return {'statusCode': 400, 'body': json.dumps({'error': 'Falta teléfono u OTP'})}
            
            # Valida el código con AWS
            sns.verify_sms_sandbox_phone_number(PhoneNumber=phone, OneTimePassword=otp)
            return {'statusCode': 200, 'body': json.dumps({'message': '¡Teléfono verificado exitosamente!'})}

        # --- ACCIÓN: ENVIAR NOTIFICACIÓN (Flujo Principal) ---
        if action == 'SEND':
            if 'channel' not in payload or 'to' not in payload:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Faltan campos: channel y to'})}

            entry = {
                'Source': 'com.proyecto.notificaciones',
                'DetailType': 'NotificacionRequest',
                'Detail': json.dumps({
                    'type': payload['channel'].upper(),
                    'recipient_email': payload['to'],
                    'phone_number': payload['to'],
                    'device_token': payload['to'],
                    'subject': payload.get('subject', 'Notificación API'),
                    'message': payload.get('msg', 'Sin contenido'),
                    'id': str(uuid.uuid4())
                }),
                'EventBusName': 'default'
            }
            response = events.put_events(Entries=[entry])
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Encolado ID: ' + response['Entries'][0]['EventId'],
                    'id': response['Entries'][0]['EventId']
                })
            }
        
        return {'statusCode': 400, 'body': json.dumps({'error': 'Acción desconocida'})}

    except Exception as e:
        print(f"ERROR: {str(e)}")
        # Manejo de errores específicos de SNS (ej: código incorrecto)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

### 2.2. Interfaz Gráfica Embebida (Serverless Frontend)
Se desarrolló una **Single Page Application (SPA)** ligera servida directamente desde la Lambda mediante el método `GET`. Esto elimina la necesidad de hosting adicional (S3/CloudFront) para pruebas simples. Se adicionó una verificación automática desde la interfaz para facilitar este tipo de procesos, tanto de verificación de correo como de número de celular, y así tener un una interfaz mucho más interactiva y funcional.

> **Evidencia Final:** Interfaz web del proyecto funcionando y lista para enviar notificaciones a los 3 canales.
>
<img width="1296" height="610" alt="image" src="https://github.com/user-attachments/assets/cbf71cac-9db5-4377-8f59-07dde20ce35c" />
<img width="1307" height="603" alt="image" src="https://github.com/user-attachments/assets/4b56e3b1-0dc1-4ae8-b50a-b2e9f3733f13" />


### 2.3. Prueba de Sistema (End-to-End)
Se realizaron pruebas de envío desde la interfaz web y mediante comandos `cURL` en CloudShell, validando que el payload JSON se inyecta correctamente en EventBridge.

> **Evidencia:** Respuesta JSON exitosa del API Gateway (`200 OK`).
>
> ![Respuesta API Exitosa](./docs/layer-1/cloudshell-test.png)

---

## 3. Capa 2: Enrutamiento y Resiliencia (Buffer)

Se construyó la infraestructura de mensajería asíncrona para desacoplar los componentes y manejar picos de carga.

### 3.1. Colas SQS (Buffers)
Se aprovisionaron 4 colas estándar en la región `us-east-2`. Cada canal cuenta con su propia cola dedicada para garantizar aislamiento de fallos.

1.  **`Email_Queue`:** Buffer para notificaciones de correo electrónico.
2.  **`SMSQueue`:** Buffer para mensajes de texto.
3.  **`PushQueue`:** Buffer para notificaciones push móviles.
4.  **`NotificacionesDLQ`:** Dead Letter Queue centralizada.

* **Configuración de Resiliencia:** Se configuró una *Redrive Policy* en las tres colas principales con `Maximum Receives = 3`. Si un mensaje falla 3 veces, se mueve automáticamente a la DLQ para análisis forense.

### 3.2. Seguridad de Colas (Hardening) - **Reto Crítico**
Durante la integración, se enfrentaron problemas de permisos que impedían a EventBridge escribir en SQS.

* **Error Detectado:** EventBridge reportaba éxito, pero los mensajes no llegaban a la cola ni a la Lambda.
* **Causa Raíz 1 (Encriptación):** El cifrado predeterminado `SSE-KMS` bloqueaba a EventBridge porque este servicio no tenía permisos sobre la llave KMS.
    * **Solución:** Se cambió el cifrado a **`SSE-SQS`**, que es transparente para los servicios de AWS.
* **Causa Raíz 2 (Identidad):** La regla de EventBridge estaba configurada para usar un Rol IAM de Lambda (`EmailConsumerRole`), lo cual generaba un conflicto de identidad.
    * **Solución:** Se eliminó el rol de la regla y se delegó la autorización a la **Política de Acceso de la Cola**.

> **Evidencia Técnica:** Política de acceso JSON final configurada en la cola `Email_Queue`, permitiendo explícitamente al servicio `events.amazonaws.com` bajo la condición del ARN de la regla.
>
> ![Política de Acceso SQS](./docs/layer-2/sqs-access-policy.png)

### 3.3. Diagnóstico de Errores de Formato (`INVALID_JSON`)
Incluso con los permisos corregidos, los mensajes terminaban en la DLQ.

* **Evidencia Forense:** Al inspeccionar un mensaje en la DLQ, se encontró el atributo `ERROR_CODE: INVALID_JSON`.
* **Solución:** Se reconfiguró el *Input Transformer* de EventBridge para construir manualmente un objeto JSON válido en lugar de pasar el evento crudo.

> **Evidencia:** Mensaje capturado en la DLQ mostrando el error de formato.
>
> ![Error INVALID_JSON en DLQ](./docs/layer-2/dlq-error-diagnosis.png)

---

## 4. Capa 3: Consumo y Persistencia (Backend)

Se implementó la lógica de negocio mediante funciones Serverless y una base de datos NoSQL para auditoría.

### 4.1. Base de Datos de Auditoría (DynamoDB)
Se creó la tabla `Project_Notifications_System_Audit` para registrar el estado de cada notificación.

* **Modelo de Datos:**
    * **PK (Partition Key):** `NotificationsID` (String) - ID único del mensaje.
    * **SK (Sort Key):** `Timestamp` (String) - Marca de tiempo Unix.
* **Analítica en Tiempo Real:** Se habilitó **DynamoDB Streams** con la configuración `New Image` para permitir que futuros consumidores analíticos reaccionen a cada inserción.

> **Evidencia:** Tabla DynamoDB activa en la región Ohio con Streams habilitados.
>
> ![Tabla DynamoDB Activa](./docs/layer-3/dynamo-table.png)

### 4.2. Canal Email (Implementación Real)
Se configuró el flujo completo para el envío de correos electrónicos transaccionales.

* **Proveedor:** Amazon SES (Simple Email Service).
* **Identidad:** Se verificó la dirección de correo del remitente (Sandbox Mode).
* **Lambda:** `EmailConsumerLambda` (Python 3.12).
    * Integra `boto3` para enviar el correo y registrar el éxito en DynamoDB.

> **Evidencia de Éxito:** Registro de auditoría en DynamoDB con estado `SENT` y el ID del mensaje de SES (`SESMessageId`), confirmando el envío real.
>
> ![Registro Exitoso Email](./docs/layer-3/dynamodb-audit-log.png)

---

## 5. Implementación Multi-Canal (Estrategia de Mocking)

Para cumplir con los requisitos de canales SMS y Push en una cuenta nueva de AWS con restricciones de Sandbox, se implementó una estrategia de simulación arquitectónica.

### 5.1. El Reto del Sandbox
AWS bloqueó el acceso al servicio de envío de SMS reales (`sns:Publish`) debido a que la cuenta se encuentra en periodo de validación antifraude.


### 5.2. Solución: Lambdas Simuladas (Mock)
Se desarrollaron las funciones `SMSConsumerLambda` y `PushConsumerLambda` con la lógica completa de recepción y validación, pero simulando el paso final de envío.

* **Estado de Auditoría:** Se registra explícitamente como `SENT_MOCK` o `SENT_MOCK_PUSH` en DynamoDB.
* **Valor:** Permite validar el enrutamiento y procesamiento de la arquitectura sin depender de la activación comercial de la cuenta.

> **Evidencia de Funcionamiento:** Registro en DynamoDB mostrando que el evento SMS fue enrutado, procesado y auditado correctamente (Estado `SENT_MOCK`).
>
> ![Auditoría SMS Mock](./docs/layer-3/dynamodb-audit-log.png)

---

## Conclusiones 

Se ha entregado una arquitectura **Serverless** robusta y desacoplada que cumple con todos los requisitos funcionales y no funcionales:

1.  **Multi-Canal:** Soporte para Email (Real), SMS y Push (Simulados).
2.  **Event-Driven:** Uso de EventBridge para enrutamiento inteligente.
3.  **Resiliencia:** Implementación de DLQ y políticas de reintento en SQS.
4.  **Observabilidad:** Trazabilidad total mediante CloudWatch Logs y DynamoDB Audit.
5.  **Seguridad:** Uso estricto de roles IAM, políticas de recursos y encriptación de datos.
