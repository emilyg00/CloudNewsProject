<img width="650" height="650" alt="Screenshot 2026-01-25 181737" src="https://github.com/user-attachments/assets/33ff378f-a1e3-4f56-8115-185de36233fa" />

Cloud News Analyzer è un'applicazione web cloud-native per lo scraping, l'analisi e la distribuzione automatizzata di notizie, sviluppata come progetto universitario con un’architettura serverless e containerizzata su AWS.

L'applicazione permette di monitorare in tempo reale diverse testate giornalistiche, categorizzare i contenuti e gestire un sistema di onboarding utenti con notifiche email personalizzate. L'obiettivo del progetto è mostrare l'integrazione professionale di servizi AWS (ECS Fargate, DynamoDB, S3, SNS, SES, EventBridge) in un sistema scalabile, sicuro e completamente automatizzato.

## Indice
* [Architettura](#architettura)
* [Struttura del Progetto](#struttura-del-progetto)
* [Requisiti](#requisiti)
* [Guida alla configurazione](#guida-alla-configurazione-e-allavvio)
* [Funzionalità Principali](#funzionalità-principali)
* [Area Riservata & UX](#area-riservata--user-experience)
* [Setup Developer](#guida-al-setup-developer)
* [Monitoraggio e Logs](#monitoraggio-e-logs-il-tocco-aws)

# Architettura
- **Frontend:** HTML5, CSS3 (Bootstrap), JavaScript (Fetch API)
- **Backend:** Python Scraper containerizzato su AWS ECS (Fargate)
- **Database: Amazon DynamoDB** (Persistenza news e gestione stato utenti)
- **Storage: Amazon S3** (Hosting statico frontend e storage dataset JSON)
- **Messaging & Notifiche:**
  - **Amazon SNS:** Distribuzione massiva delle news
  - **Amazon SES:** Invio sicuro di email di conferma account
- **Event-driven: Amazon EventBridge** (Scheduler per avvio task orario)
- **CI/CD: GitHub Actions** (Build & Push immagine Docker su Amazon ECR)
- **Security: IAM Roles** (Principio del minimo privilegio)

## Struttura del Progetto
```text
.
├── backend/
│   ├── Dockerfile          # Configurazione container
│   ├── scraper.py          # Logica di scraping Python
│   └── requirements.txt    # Dipendenze backend
├── frontend/
│   ├── index.html          # Dashboard principale
│   ├── script.js           # Logica Fetch e Chart.js
│   └── styles.css          # Design e Bootstrap custom
└── .github/workflows/
    └── ci-cd.yml           # Pipeline GitHub Actions
```

# Requisiti
- Docker Desktop
- AWS CLI configurata
- AWS Account con permessi IAM corretti
- Repository privato su Amazon ECR

# Guida alla configurazione e all'avvio
1. **Configurazione Infrastruttura:** Carica lo stack tramite CloudFormation o configura manualmente i servizi (S3, DynamoDB, SNS).
2. **Setup Variabili d'Ambiente:** Configura le variabili nel task ECS per puntare correttamente alle risorse create (es. `BUCKET_NAME`, `TABLE_NAME`).
3. **Deployment del Backend:**
   - Esegui il login al registro ECR:
     ```bash
     aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
     ```
   - Build e Push dell'immagine:
     ```bash
     docker build -t cloud-news-scraper .
     docker tag cloud-news-scraper:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/cloud-news-scraper:latest
     docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/cloud-news-scraper:latest
     ```
4. **Deploy del Frontend:** Caricare i file statistici (`index.html`, `script.js`, `styles.css`) sul bucket S3 configurato:
     ```bash
     aws s3 sync ./frontend s3://progetto-finale-news-rawnewsbucket-lylvfnkdtxzs --acl public-read
     ```

# Funzionalità Principali
- **Scraping Multi-Categoria:** Analisi di fonti quali ANSA, Gazzetta, Wall Street Italia, Fatto in Casa da Benedetta, Punto Informatico e Binance (BTC Live).
- **User Onboarding:** Rilevamento automatico di nuovi utenti "pending" e invio codice di conferma `AWS-CONFIRM-2026`.
- **Data Visualization:** Dashboard interattiva con grafici `Chart.js` per la distribuzione delle fonti.

## Area Riservata & User Experience
L'accesso alle funzionalità avanzate è gestito tramite un'area protetta che simula un sistema di **Identity & Access Management**.

### 1. Onboarding e Validazione
Per garantire la sicurezza, il workflow di registrazione prevede:
* Inserimento di `username`, `email` e `password`.
* Invio automatico di una mail di conferma tramite **Amazon SES/SNS**.
* Validazione dell'account tramite il codice univoco: `AWS-CONFIRM-2026`.

### 2. Dashboard Personale (Comando Cloud)
Una volta autenticato, l'utente accede a un pannello di controllo dinamico che include:
* **Libreria**: Archivio persistente per consultare gli articoli salvati in precedenza.
* **Community**: Sezione interattiva per lasciare commenti e interagire con altri utenti sotto i moduli informativi.
* **Centro Notifiche**: Hub che segnala in tempo reale le risposte ai commenti e le conferme di cambio preferenze (es. `Sincronizzazione Cloud attiva per: Tech`).

### 3. Personalizzazione
L'utente può interagire con il sistema definendo:
* **Dark Mode Cloud**: Per un'interfaccia ad alto contrasto.
* **News Preference**: Menu a tendina per istruire il backend (DynamoDB) su quali categorie di notizie dare la priorità durante lo scraping.

## Guida al Setup (Developer)
Per configurare l'ambiente di sviluppo locale e collegarlo ai servizi AWS:

```bash
# Clona il repository
git clone [https://github.com/tuo-username/cloud-news-analyzer.git](https://github.com/tuo-username/cloud-news-analyzer.git)

# Installa le dipendenze Python
pip install -r requirements.txt
```
### Monitoraggio e Logs (Il tocco AWS)
Visto che usi **Fargate**, sarebbe ottimo aggiungere una riga su come si controlla se tutto funziona. Questo dimostra che sai usare **CloudWatch**.

Il sistema utilizza **Amazon CloudWatch** per il logging centralizzato. È possibile monitorare l'esecuzione dei task ECS e lo stato delle notifiche SNS direttamente dalla console AWS, garantendo una rapida risoluzione di eventuali errori di scraping o di invio email.
