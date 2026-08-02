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

# --- 1. FUNZIONE PER OTTENERE PREZZO ATTUALE E TITOLO ---
def get_keepa_product_data(asin):
    """Chiama Keepa per avere prezzo attuale, titolo e storico"""
    if not KEEPA_API_KEY:
        print("❌ CHIAVE KEEPA NON TROVATA! Controlla i Secrets.")
        return None, None, None

    url = "https://api.keepa.com/product"
    params = {
        'key': KEEPA_API_KEY,
        'asin': asin,
        'domain': 10,         # Amazon Italia
        'stats': 3600,        # Per il prezzo minimo storico
        'update': 1           # Forza l'aggiornamento del prezzo attuale
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['products']:
                product = data['products'][0]
                
                # 1. Estrai il Titolo
                title = product.get('title', f"Prodotto {asin}")
                
                # 2. Estrai il Prezzo Attuale
                # Keepa salva i prezzi in una lista di liste: [timestamp, prezzo_in_centesimi]
                price_data = product.get('data', [])
                current_price = None
                
                if price_data and len(price_data) > 0:
                    # Prende l'ultimo valore della lista (quello attuale)
                    if isinstance(price_data[0], list):
                        last_price_cents = price_data[-1][1]
                    else:
                        last_price_cents = price_data[-1]
                    
                    current_price = last_price_cents / 100.0
                    print(f"💰 {title} -> Prezzo Attuale: € {current_price}")
                
                # 3. Estrai il Prezzo Minimo Storico
                min_price = None
                if 'stats' in product and product['stats']:
                    min_price_cents = product['stats'].get('min')
                    if min_price_cents:
                        min_price = min_price_cents / 100.0
                        print(f"📉 {title} -> Prezzo Minimo Storico: € {min_price}")

                return current_price, min_price, title
            else:
                print(f"⚠️ Prodotto {asin} non trovato su Keepa.")
                return None, None, None
        else:
            print(f"❌ Errore API Keepa: {response.status_code}")
            return None, None, None
    except Exception as e:
        print(f"❌ Errore connessione Keepa: {e}")
        return None, None, None

# --- 2. FUNZIONE PER INVIARE SU TELEGRAM ---
def send_telegram_alert(asin, title, current_price, min_price):
    link = f"https://www.amazon.it/dp/{asin}?tag={AMAZON_AFFILIATE_TAG}"
    
    caption = f"🛒 *{title}*\n\n" \
              f"💰 Prezzo Attuale: *€ {current_price:.2f}*\n" \
              f"📉 Prezzo Minimo Storico: € {min_price:.2f}\n" \
              f"🚨 *SCONTO ERRATO TROVATO!* 🚨\n\n" \
              f"🛍️ [Acquista subito]({link})"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': caption,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Allarme inviato su Telegram con successo!")
        else:
            print(f"❌ Errore Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Errore connessione Telegram: {e}")

# --- MAIN ---
def main():
    print("🚀 Avvio bot con Keepa API (Zero Scraping, Zero Errori!)...")
    
    for asin in ASIN_LIST:
        # Passo Unico: Chiedi tutto a Keepa (prezzo attuale, storico e titolo)
        current_price, min_price, title = get_keepa_product_data(asin)
        
        if current_price and min_price:
            # Logica dello sconto: se il prezzo attuale è più basso del minimo storico
            if current_price < min_price:
                print(f"🚨 SCONTO ERRATO TROVATO! {asin} sotto il minimo storico!")
                send_telegram_alert(asin, title, current_price, min_price)
            else:
                print(f"ℹ️ Prezzo normale per {title}. (Attuale €{current_price} > Storico €{min_price})")
        else:
            print(f"⏭️ Dati insufficienti da Keepa per {asin}, salto.")
        
        # Pausa breve tra un prodotto e l'altro per non sovraccaricare le API
        time.sleep(2)

if __name__ == "__main__":
    main()
