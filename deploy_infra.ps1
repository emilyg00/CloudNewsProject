# --- Script Infrastructure as Code (IaC) ---

# 1. Creazione Bucket S3 per il Frontend
Write-Host "Creazione Bucket S3..." -ForegroundColor Cyan
aws s3api create-bucket --bucket "dashboard-news-emily-2026" --region eu-central-1 --create-bucket-configuration LocationConstraint=eu-central-1

# 2. Creazione Tabella DynamoDB per lo storico
Write-Host "Creazione Tabella DynamoDB..." -ForegroundColor Cyan
aws dynamodb create-table `
    --table-name "NewsDashboardTable" `
    --attribute-definitions AttributeName=NewsId,AttributeType=S `
    --key-schema AttributeName=NewsId,KeyType=HASH `
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 `
    --region eu-central-1

Write-Host "✅ Infrastruttura creata con successo via AWS CLI!" -ForegroundColor Green