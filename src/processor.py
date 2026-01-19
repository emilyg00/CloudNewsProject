import json
import boto3
import os

# Inizializziamo il client DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'NewsAnalyzerTable')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    # 1. Recupera informazioni sul file caricato da S3
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        print(f"Sto elaborando il file {key} dal bucket {bucket}")
        
        # 2. Leggi il contenuto del file JSON
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(response['Body'].read().decode('utf-8'))
        
        # 3. Salva i dati su DynamoDB
        table.put_item(
            Item={
                'NewsId': key,  # Usiamo il nome del file come ID
                'Title': data.get('title', 'N/A'),
                'Content': data.get('content', 'N/A'),
                'Timestamp': data.get('date', 'N/A')
            }
        )
        
    return {
        'statusCode': 200,
        'body': json.dumps('Elaborazione completata!')
    }