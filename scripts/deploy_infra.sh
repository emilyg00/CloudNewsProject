#!/bin/bash

# Definiamo il nome dello stack
STACK_NAME="CloudNewsAnalyzer-Infra"
REGION="eu-central-1" # Cambiala se preferisci un'altra regione

echo "--- Inizio Deployment dell'Infrastruttura ---"

aws cloudformation deploy \
  --template-file iac/infrastructure.yaml \
  --stack-name $STACK_NAME \
  --region $REGION \
  --capabilities CAPABILITY_IAM

echo "--- Infrastruttura pronta su AWS! ---"