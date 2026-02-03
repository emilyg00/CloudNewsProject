import feedparser, boto3, json, requests, random
from datetime import datetime
import time

# CONFIGURAZIONE AWS
REGION = "eu-central-1"
BUCKET_NAME = "progetto-finale-news-rawnewsbucket-lylvfnkdtxzs"
TABLE_NAME = "NewsDashboardTable"
USERS_TABLE = "CloudUsers"
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
    """Invia il codice di attivazione SOLO ai nuovi utenti registrati"""
    print(f"--- 📧 Scansione tabella {USERS_TABLE} per gli utenti iscritti ---")
    try:
        response = users_table.scan()
        users = response.get('Items', [])
        
        count = 0
        for user in users:
            if user.get('status') == 'pending':
                email_destinatario = user['email']
                nome_utente = user.get('name', 'Utente Cloud')
                
                print(f"Rilevato nuovo utente: {email_destinatario}. Invio codice...")
                
                message = (f"Ciao {nome_utente}!\n\n"
                           f"Grazie per esserti registrato a CloudNews.\n"
                           f"Codice di attivazione: AWS-CONFIRM-2026\n\n"
                           f"Benvenuto nell'infrastruttura di Emily!")
                
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
                
                users_table.update_item(
                    Key={'email': email_destinatario},
                    UpdateExpression="set #st = :val",
                    ExpressionAttributeNames={'#st': 'status'},
                    ExpressionAttributeValues={':val': 'notified'}
                )
                print(f"✅ Mail inviata a: {email_destinatario}")
                count += 1
        
        if count == 0: print("Nessun nuovo utente in attesa.")
    except Exception as e:
        print(f"⚠️ Errore ciclo utenti: {str(e)}")

def send_sns_notification(category, title):
    """Invia notifica SOLO agli utenti che hanno scelto questa categoria nel browser"""
    try:
        # 1. Recuperiamo gli utenti e le loro preferenze dal DB
        response = users_table.scan()
        users = response.get('Items', [])
        
        for user in users:
            user_email = user['email']
            # Leggiamo la preferenza salvata dall'index.html
            user_pref = user.get('preference', 'None')
            
            # 2. Inviamo la mail solo se c'è un match
            if user_pref == category:
                print(f"Match trovato! Inviando {category} a {user_email}")
                message = f"Notizia Flash ({category}):\n\n{title}"
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
    except Exception as e:
        print(f"⚠️ Errore SNS News: {str(e)}")

def run_sync():
    all_news = []
    categories_notified = set() 
    
    print(f"--- 🚀 Avvio Sync News ---")
    headers = {'User-Agent': 'Mozilla/5.0'}

    for category, url in FEEDS.items():
        clean_category = category.strip().capitalize()
        try:
            response = requests.get(url, headers=headers, timeout=15)
            feed = feedparser.parse(response.content)
            source_name = feed.feed.get('title', clean_category).split(' - ')[0]

            for entry in feed.entries[:8]:
                data_formattata = datetime.now().strftime('%d/%m/%Y %H:%M')
                
                item = {
                    'NewsId': entry.link,
                    'Source': source_name,
                    'Category': clean_category, 
                    'Title': entry.title,
                    'Description': entry.get('summary', '').split('<')[0][:150],
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

    # Bitcoin Price
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCEUR")
        price = float(res.json()['price'])
        all_news.append({
            'NewsId': 'live-btc', 'Source': 'Binance', 'Category': 'Live',
            'Title': f"📊 BTC: €{price:,.2f}", 'Description': "Prezzo Live",
            'Link': 'https://binance.com', 'Timestamp': datetime.now().isoformat(),
            'PublishedDate': datetime.now().strftime('%d/%m/%Y %H:%M')
        })
    except: pass

    s3.put_object(
        Bucket=BUCKET_NAME, Key='news.json',
        Body=json.dumps(all_news, ensure_ascii=False),
        ContentType='application/json'
    )
    
    check_and_notify_new_users()
    print(f"--- 🎉 SYNC COMPLETATA ---")

if __name__ == "__main__":
    run_sync()