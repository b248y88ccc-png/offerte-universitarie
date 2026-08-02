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

# --- 1. FUNZIONE PER OTTENERE IL PREZZO DA AMAZON ---
def get_current_price(asin):
    """Apre un browser per leggere il prezzo attuale su Amazon"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            url = f"https://www.amazon.it/dp/{asin}"
            print(f"🌐 Apro Amazon per {asin}...")
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Legge l'HTML
            html = page.content()
            browser.close()
            
            # --- HO SPOSTATO L'IMPORT DI 're' QUI DENTRO ---
            import re 

            # Cerca il prezzo nel DOM
            price_match = re.search(r'<span class="a-price-whole">([\d\.]+)', html)
            if price_match:
                price = float(price_match.group(1).replace('.', ''))
                return price
            
            # Prova a prendere il prezzo da un altro selettore
            price_match_off = re.search(r'<span class="a-offscreen">[€\s]*([\d\.]+)', html)
            if price_match_off:
                 price = float(price_match_off.group(1).replace('.', ''))
                 return price

            print(f"⚠️ Prezzo Amazon non trovato per {asin}")
            return None

    except Exception as e:
        print(f"❌ Errore Playwright per {asin}: {e}")
        return None

# --- 2. FUNZIONE PER OTTENERE IL PREZZO MINIMO STORICO DA KEEPA ---
def get_keepa_historical_price(asin):
    """Chiama l'API di Keepa"""
    if not KEEPA_API_KEY:
        print("❌ CHIAVE KEEPA NON TROVATA! Controlla i Secrets.")
        return None

    url = "https://api.keepa.com/product"
    params = {
        'key': KEEPA_API_KEY,
        'asin': asin,
        'domain': 10,
        'stats': 3600
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['products']:
                price_data = data['products'][0]['stats']
                if price_data:
                    min_price_cents = price_data['min']
                    min_price = min_price_cents / 100.0
                    print(f"📉 Prezzo minimo storico Keepa: € {min_price}")
                    return min_price
        else:
            print(f"❌ Errore API Keepa: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Errore connessione Keepa: {e}")
        return None

# --- 3. FUNZIONE PER INVIARE SU TELEGRAM ---
def send_telegram_alert(asin, title, current_price, min_price):
    link = f"https://www.amazon.it/dp/{asin}?tag={AMAZON_AFFILIATE_TAG}"
    
    caption = f"🛒 *{title[:50]}...*\n\n" \
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
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Allarme inviato su Telegram!")
        else:
            print(f"❌ Errore Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Errore connessione Telegram: {e}")

# --- MAIN ---
def main():
    print("🚀 Avvio bot con Keepa...")
    
    for asin in ASIN_LIST:
        current_price = get_current_price(asin)
        
        if current_price:
            print(f"💰 Prezzo Attuale Amazon: € {current_price}")
            min_price = get_keepa_historical_price(asin)
            
            if min_price:
                if current_price < min_price:
                    print(f"🚨 SCONTO ERRATO TROVATO! {asin} sotto il minimo storico!")
                    send_telegram_alert(asin, asin, current_price, min_price)
                else:
                    print(f"ℹ️ Prezzo normale per {asin} (Sopra la media storica).")
            else:
                print(f"⏭️ Impossibile ottenere storico da Keepa per {asin}, salto.")
        else:
            print(f"⏭️ Prezzo attuale non trovato per {asin}, salto.")
        
        time.sleep(5)

if __name__ == "__main__":
    main()
