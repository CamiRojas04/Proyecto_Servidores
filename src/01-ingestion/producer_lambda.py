import json
import boto3
import time

events = boto3.client('events')

def lambda_handler(event, context):
    # API Gateway entrega el método HTTP en esta ruta del evento
    http_method = event.get('requestContext', {}).get('http', {}).get('method')

    # ------------------------------------------------------------------
    # 1. FRONTEND: Servir Interfaz Web (GET)
    # ------------------------------------------------------------------
    if http_method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': """
            <html>
                <head>
                    <title>API de Notificaciones</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f0f2f5; }
                        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; width: 400px; }
                        h1 { color: #d63384; }
                        code { background: #eee; padding: 5px; border-radius: 5px; }
                        .status { color: green; font-weight: bold; }
                        input, select, textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; font-family: Arial, sans-serif; }
                        button { background-color: #d63384; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px; }
                        button:hover { background-color: #b02a6b; }
                        button:disabled { background-color: #ccc; cursor: not-allowed; }
                        #response { margin-top: 20px; font-size: 14px; min-height: 20px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Project: Notification System</h1>
                        <p class="status">System is properly working</p>
                        <hr>
                        <form id="notifForm">
                            <div style="text-align: left; font-size: 14px; color: #666; margin-bottom: 5px;">Channel:</div>
                            <select id="channel">
                                <option value="EMAIL">Email</option>
                                <option value="SMS">SMS</option>
                                <option value="PUSH">Push</option>
                            </select>
                            <input type="text" id="to" placeholder="Recipient (Email / Phone / Token)" required>
                            <textarea id="msg" placeholder="Write your message here..." rows="3" required></textarea>
                            <button type="submit">Send Notification</button>
                        </form>
                        <div id="response"></div>
                    </div>
                    <script>
                        document.getElementById('notifForm').addEventListener('submit', async (e) => {
                            e.preventDefault();
                            const btn = e.target.querySelector('button');
                            const respDiv = document.getElementById('response');
                            
                            const data = {
                                channel: document.getElementById('channel').value,
                                to: document.getElementById('to').value,
                                msg: document.getElementById('msg').value
                            };

                            btn.disabled = true;
                            btn.innerText = 'Sending...';
                            respDiv.innerText = '';
                            respDiv.style.color = '#333';

                            try {
                                const res = await fetch('/send', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify(data)
                                });
                                
                                let result;
                                try { result = await res.json(); } catch(e) { result = { error: 'Error parsing JSON' }; }
                                
                                if(res.ok) {
                                    respDiv.style.color = 'green';
                                    respDiv.innerHTML = '<b>✅ Success!</b><br>ID: ' + (result.id || 'N/A');
                                } else {
                                    throw new Error(result.error || 'Unknown Error (' + res.status + ')');
                                }
                            } catch (err) {
                                respDiv.style.color = 'red';
                                respDiv.innerText = '❌ ' + err.message;
                            } finally {
                                btn.disabled = false;
                                btn.innerText = 'Send Notification';
                            }
                        });
                    </script>
                </body>
            </html>
            """
        }

    # ------------------------------------------------------------------
    # 2. BACKEND: Procesar Notificación (POST)
    # ------------------------------------------------------------------
    print("Recibida solicitud POST API Gateway")
    
    try:
        # Parsear body
        if 'body' in event:
            if isinstance(event['body'], str):
                payload = json.loads(event['body'])
            else:
                payload = event['body']
        else:
            payload = event

        # Validar campos obligatorios
        if 'channel' not in payload or 'to' not in payload:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Faltan campos: channel y to son obligatorios'})
            }

        # Construir Evento Estándar
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
                'id': f"api-{int(time.time())}"
            }),
            'EventBusName': 'default'
        }

        # Publicar en EventBridge
        response = events.put_events(Entries=[entry])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notificación recibida y encolada',
                'id': response['Entries'][0]['EventId']
            })
        }

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
