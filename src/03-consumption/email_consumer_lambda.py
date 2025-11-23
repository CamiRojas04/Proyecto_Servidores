import json
import boto3
import os
import time

# Inicialización de clientes fuera del handler para optimizar arranque en frío
sqs = boto3.client('sqs')
ses = boto3.client('ses')
dynamodb = boto3.resource('dynamodb')

# Configuración vía Variables de Entorno
TABLE_NAME = os.environ['DYNAMODB_TABLE']
SENDER_EMAIL = os.environ['SENDER_EMAIL']
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Procesa lotes de mensajes de SQS, envía correos vía SES y audita en DynamoDB.
    Maneja fallos parciales retornando batchItemFailures.
    """
    print(f"Procesando lote de {len(event['Records'])} mensajes.")
    batch_item_failures = []

    for record in event['Records']:
        message_id = record['messageId']
        try:
            # 1. Parseo del Evento (Limpio desde EventBridge)
            body = json.loads(record['body'])
            recipient = body.get('recipient_email')
            subject = body.get('subject', 'Notificación')
            message_content = body.get('message', 'Sin contenido')
            # Uso de ID propio o fallback al ID de SQS
            notification_id = body.get('id', message_id)

            if not recipient:
                print(f"WARN: Mensaje {message_id} sin destinatario. Omitiendo.")
                continue

            # 2. Envío Transaccional (Amazon SES)
            response = ses.send_email(
                Source=SENDER_EMAIL,
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': message_content}}
                }
            )
            print(f"SUCCESS: Email enviado a {recipient}. SES ID: {response['MessageId']}")

            # 3. Auditoría Persistente (DynamoDB)
            audit_item = {
                'NotificationsID': notification_id, # Clave de Partición
                'Timestamp': str(time.time()),      # Clave de Ordenación
                'Channel': 'EMAIL',
                'Status': 'SENT',
                'Recipient': recipient,
                'SESMessageId': response['MessageId']
            }
            table.put_item(Item=audit_item)

        except Exception as e:
            print(f"ERROR en mensaje {message_id}: {str(e)}")
            # Marcamos el mensaje para que SQS lo reintente (mecanismo de DLQ)
            batch_item_failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": batch_item_failures}
