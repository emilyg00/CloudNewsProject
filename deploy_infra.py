import boto3
import time

region = "eu-central-1"
s3_client = boto3.client('s3', region_name=region)
dynamodb_client = boto3.client('dynamodb', region_name=region)

def deploy():
    print("--- Inizio Deployment Infrastruttura (IaC) ---")

    # 1. Creazione Bucket S3
    bucket_name = "progetto-news-dashboard-tuonome" # Cambialo con uno unico
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        print(f"✅ Bucket S3 creato: {bucket_name}")
    except Exception as e:
        print(f"❌ Errore S3: {e}")

    # 2. Creazione Tabella DynamoDB
    table_name = "NewsDashboardTable"
    try:
        dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'NewsId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'NewsId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"✅ Tabella DynamoDB '{table_name}' in creazione...")
        # Aspettiamo che la tabella sia attiva
        waiter = dynamodb_client.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        print("🚀 Tabella attiva e pronta!")
    except Exception as e:
        print(f"❌ Errore DynamoDB: {e}")

    print("--- Deployment Completato con Successo ---")

if __name__ == "__main__":
    deploy()