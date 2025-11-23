import json
import boto3
import os
import time

# Cliente SNS comentado por restricción de Sandbox en cuenta nueva
# sns = boto3.client('sns') 
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ['DYNAMODB_TABLE']
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Simulación de envío SMS. Valida la lógica de negocio y registra
    el intento exitoso en DynamoDB sin realizar el gasto en SNS.
    """
    batch_item_failures = []

    for record in event['Records']:
        message_id = record['messageId']
        try:
            body = json.loads(record['body'])
            phone_number = body.get('phone_number')
            message_content = body.get('message')
            notification_id = body.get('id', message_id)

            # Simulación de latencia de red y generación de ID
            fake_sns_id = f"mock-sns-id-{int(time.time())}"
            print(f"MOCK: Enviando SMS a {phone_number}. ID Generado: {fake_sns_id}")

            # Auditoría con estado explícito de simulación
            audit_item = {
                'NotificationsID': notification_id,
                'Timestamp': str(time.time()),
                'Channel': 'SMS',
                'Status': 'SENT_MOCK', 
                'Recipient': phone_number,
                'SESMessageId': fake_sns_id
            }
            table.put_item(Item=audit_item)

        except Exception as e:
            print(f"Error: {str(e)}")
            batch_item_failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": batch_item_failures}
