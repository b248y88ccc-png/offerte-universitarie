import os
import time
import requests
import json
from playwright.sync_api import sync_playwright

# --- CONFIGURAZIONE ---
TELEGRAM_BOT_TOKEN = "8854356674:AAF65IdHYZE1S3xSfeP6cqGn9X3yrxZYH9E"
TELEGRAM_CHANNEL_ID = "@offerteuniversitarie"
KEEPA_API_KEY = "m3t93ksddqntnpgibgijubm4s78u769rsrr9jah9p33m4aab4cinrot1170322ki"

# I tuoi ASIN
ASIN_LIST = [
    "B07X3T1F93",
    "B08N5WRWNW",
]

# --- FUNZIONE KEEPA (Legge prezzo attuale, storico e titolo) ---
def get_keepa_data(asin):
    if not KEEPA_API_KEY:
        print("❌ Chiave Keepa mancante.")
        return None, None, None

    url = "https://api.keepa.com/product"
    params = {
        'key': KEEPA_API_KEY,
        'asin': asin,
        'domain': 10,      # Amazon Italia
        'stats': 3600,     # Per il prezzo minimo storico
        'update': 1        # Per forzare il prezzo attuale
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['products']:
                product = data['products'][0]
                
                # 1. Titolo
                title = product.get('title', f"Prodotto {asin}")
                
                # 2. Prezzo Attuale (Keepa lo dà in centesimi)
                price_data = product.get('data', [])
                current_price = None
                if price_data:
                    # Prende l'ultimo valore registrato
                    if isinstance(price_data[0], list):
                        last_price_cents = price_data[-1][1]
                    else:
                        last_price_cents = price_data[-1]
                    current_price = last_price_cents / 100.0
                
                # 3. Prezzo Minimo Storico
                min_price = None
                if 'stats' in product and product['stats']:
                    min_cents = product['stats'].get('min')
                    if min_cents:
                        min_price = min_cents / 100.0

                return current_price, min_price, title
        else:
            print(f"❌ Errore Keepa: {response.status_code}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return None, None, None

# --- FUNZIONE TELEGRAM ---
def send_telegram(asin, title, current_price, min_price):
    link = f"https://www.amazon.it/dp/{asin}?tag={AMAZON_AFFILIATE_TAG}"
    
    caption = f"🛒 *{title}*\n\n" \
              f"💰 Prezzo Attuale: *€ {current_price:.2f}*\n" \
              f"📉 Prezzo Minimo Storico: € {min_price:.2f}\n" \
              f"🚨 *SCONTO ERRATO!* 🚨\n\n" \
              f"🛍️ [Acquista subito]({link})"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': caption,
        'parse_mode': 'Markdown'
    }
    
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print("✅ Inviato su Telegram.")
        else:
            print(f"❌ Errore Telegram: {r.text}")
    except Exception as e:
        print(f"❌ Errore invio Telegram: {e}")

# --- MAIN ---
def main():
    print("🚀 Avvio bot API Keepa...")
    
    for asin in ASIN_LIST:
        current, minimum, title = get_keepa_data(asin)
        
        if current and minimum:
            if current < minimum:
                print(f"🚨 Sconto trovato per {title}!")
                send_telegram(asin, title, current, minimum)
            else:
                print(f"ℹ️ Prezzo normale per {title}.")
        else:
            print(f"⏭️ Dati mancanti per {asin}.")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
