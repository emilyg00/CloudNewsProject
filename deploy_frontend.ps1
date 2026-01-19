# 1. Variabili
$BUCKET_NAME = "progetto-finale-news-rawnewsbucket-lylvfnkdtxzs"
$REGION = "eu-central-1"

Write-Host "--- Avvio Deploy Frontend su S3 ---" -ForegroundColor Cyan

# 2. Configura il bucket per ospitare un sito web
aws s3 website "s3://$BUCKET_NAME/" --index-document index.html

# 3. Carica il file index.html
aws s3 cp index.html "s3://$BUCKET_NAME/index.html"

# (Il punto 4 è stato rimosso perché la Bucket Policy gestisce i permessi)

# 5. Genera e mostra l'URL
$URL = "http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"
Write-Host "`n--- DEPLOY COMPLETATO ---" -ForegroundColor Green
Write-Host "Puoi accedere al tuo frontend qui:" -ForegroundColor Yellow
Write-Host $URL -ForegroundColor Cyan