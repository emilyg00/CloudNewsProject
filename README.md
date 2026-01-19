# 🚀 Cloud News Analyzer & Notification System

Sistema automatizzato basato su architettura **AWS Serverless e Containerizzata** per lo scraping di notizie e la gestione delle notifiche utenti.

## 🛠️ Architettura AWS Utilizzata
* **Amazon ECS (Fargate):** Esecuzione del container Python per lo scraping.
* **Amazon DynamoDB:** Database NoSQL per il salvataggio delle news e la gestione dello stato utenti (`pending`/`notified`).
* **Amazon S3:** Storage per i file JSON delle news sincronizzate.
* **Amazon SNS:** Servizio di notifica per l'invio massivo di news e codici di conferma.
* **Amazon SES:** Gestione delle identità verificate per l'invio sicuro delle email.
* **Amazon EventBridge:** Scheduler per l'avvio automatico del task ECS.

## 📋 Funzionalità
1. **Scraping Multi-Categoria:** Analisi di diverse categorie (Tech, Sport, Economia, etc.).
2. **User Onboarding:** Rilevamento automatico di nuovi utenti nel database e invio immediato di un codice di conferma via email.
3. **Email Notifications:** Invio dei riepiloghi news agli utenti iscritti tramite SNS.

## 🚀 Setup & Sicurezza
Il sistema utilizza **IAM Role** per l'accesso ai servizi AWS, evitando l'uso di chiavi d'accesso cablate nel codice, seguendo le Best Practices di sicurezza AWS.