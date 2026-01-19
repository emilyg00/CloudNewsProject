import feedparser, boto3, json, requests, random
from datetime import datetime
import time

# CONFIGURAZIONE AWS
REGION = "eu-central-1"
BUCKET_NAME = "progetto-finale-news-rawnewsbucket-lylvfnkdtxzs"
TABLE_NAME = "NewsDashboardTable"
USERS_TABLE = "CloudUsers"  # <--- Assicurati che la tabella esista con Partition Key: email
SNS_TOPIC_ARN = "arn:aws:sns:eu-central-1:529544622043:CloudNewsNotifications"

s3 = boto3.client('s3', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)
users_table = dynamodb.Table(USERS_TABLE)

FEEDS = {
    'Motori': 'https://www.ansa.it/sito/notizie/motori/motori_rss.xml', 
    'Sport': 'https://www.gazzetta.it/rss/home.xml',
    'Economia': 'https://www.wallstreetitalia.com/feed/', 
    'News': 'https://www.ansa.it/sito/ansait_rss.xml',
    'Tech': 'https://www.punto-informatico.it/feed/',
    'Cucina': 'https://www.fattoincasadabenedetta.it/feed/'
}

def check_and_notify_new_users():
    """Legge la tabella CloudUsers e invia la mail di conferma ai nuovi indirizzi reali"""
    print(f"--- 📧 Scansione tabella {USERS_TABLE} per nuovi utenti ---")
    try:
        # Scansiona la tabella utenti
        response = users_table.scan()
        users = response.get('Items', [])
        
        count = 0
        for user in users:
            # Controlla se lo stato è 'pending'
            if user.get('status') == 'pending':
                email_destinatario = user['email']
                nome_utente = user.get('name', 'Utente Cloud')
                
                print(f"Rilevato nuovo utente: {email_destinatario}. Invio codice...")
                
                message = (f"Ciao {nome_utente}!\n\n"
                           f"Grazie per esserti registrato a CloudNews.\n"
                           f"Il tuo account è quasi pronto.\n\n"
                           f"Codice di attivazione da inserire sul sito:\n"
                           f"AWS-CONFIRM-2026\n\n"
                           f"Benvenuto nell'infrastruttura di Emily!")
                
                # Invia via SNS
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=message,
                    Subject="📧 Conferma Registrazione CloudNews",
                    MessageAttributes={
                        'category': {
                            'DataType': 'String',
                            'StringValue': 'Registration'
                        }
                    }
                )
                
                # Aggiorna lo stato su DynamoDB a 'notified' usando ExpressionAttributeNames 
                # perché 'status' è una parola riservata in DynamoDB
                users_table.update_item(
                    Key={'email': email_destinatario},
                    UpdateExpression="set #st = :val",
                    ExpressionAttributeNames={'#st': 'status'},
                    ExpressionAttributeValues={':val': 'notified'}
                )
                print(f"✅ Mail inviata e database aggiornato per: {email_destinatario}")
                count += 1
        
        if count == 0:
            print("Nessun nuovo utente in attesa.")

    except Exception as e:
        print(f"⚠️ Errore durante il ciclo utenti: {str(e)}")

def send_sns_notification(category, title):
    """Invia notifica flash per le news"""
    try:
        message = f"Notizia Flash ({category}):\n\n{title}\n\nControlla la tua Cloud Dashboard!"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=f"🚀 CloudNews Flash: {category}",
            MessageAttributes={
                'category': {
                    'DataType': 'String',
                    'StringValue': category
                }
            }
        )
        print(f"📧 Messaggio news inviato a SNS per: {category}")
    except Exception as e:
        print(f"⚠️ Errore SNS News: {str(e)}")

def run_sync():
    all_news = []
    categories_notified = set() 
    
    print(f"--- 🚀 Avvio Sync News ---")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for category, url in FEEDS.items():
        clean_category = category.strip().capitalize()
        try:
            response = requests.get(url, headers=headers, timeout=15)
            feed = feedparser.parse(response.content)
            source_name = feed.feed.get('title', clean_category).split(' - ')[0].split(' | ')[0]

            for entry in feed.entries[:8]:
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    data_formattata = time.strftime('%d/%m/%Y %H:%M', entry.published_parsed)
                else:
                    data_formattata = datetime.now().strftime('%d/%m/%Y %H:%M')
                
                item = {
                    'NewsId': entry.link,
                    'Source': source_name,
                    'Category': clean_category, 
                    'Title': entry.title,
                    'Description': entry.get('summary', 'Leggi i dettagli sul sito.').split('<')[0][:150],
                    'Link': entry.link,
                    'Timestamp': datetime.now().isoformat(),
                    'PublishedDate': data_formattata
                }
                
                if clean_category not in categories_notified:
                     send_sns_notification(clean_category, item['Title'])
                     categories_notified.add(clean_category)

                all_news.append(item)
                table.put_item(Item=item)
            
            print(f"✅ {clean_category} sincronizzata.")
            
        except Exception as e:
            print(f"❌ Errore su {clean_category}: {str(e)}")

    # Bitcoin Live
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCEUR", timeout=5)
        price = float(res.json()['price'])
        all_news.append({
            'NewsId': 'live-btc', 'Source': 'Binance', 'Category': 'Live',
            'Title': f"📊 BITCOIN LIVE: €{price:,.2f}", 'Description': "Prezzo aggiornato ora",
            'Link': 'https://www.binance.com', 'Timestamp': datetime.now().isoformat(),
            'PublishedDate': datetime.now().strftime('%d/%m/%Y %H:%M')
        })
    except: pass

    random.shuffle(all_news) 

    s3.put_object(
        Bucket=BUCKET_NAME, Key='news.json',
        Body=json.dumps(all_news, ensure_ascii=False),
        ContentType='application/json',
        CacheControl='no-store, no-cache, must-revalidate'
    )
    
    # --- LOGICA UTENTI REALI ---
    check_and_notify_new_users()

    print(f"--- 🎉 SYNC COMPLETATA ---")

if __name__ == "__main__":
    run_sync()