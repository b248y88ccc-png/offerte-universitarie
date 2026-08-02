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

# --- 1. FUNZIONE CHE LEGGE IL PREZZO ATTUALE DIRETTAMENTE DA KEEPA (NO SCRAPING) ---
def get_keepa_current_price(asin):
    """
    Usa l'API di Keepa per leggere il prezzo attuale del prodotto.
    Keepa ha una chiamata specifica per i dati in tempo reale.
    """
    if not KEEPA_API_KEY:
        print("❌ CHIAVE KEEPA NON TROVATA! Controlla i Secrets.")
        return None

    # Parametri per la richiesta Product all'API di Keepa
    # domain=10 è per Amazon Italia
    url = "https://api.keepa.com/product"
    params = {
        'key': KEEPA_API_KEY,
        'asin': asin,
        'domain': 10,
        'stats': 1 # 1 significa "dammi i dati della pagina appena aggiornati"
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['products']:
                # Il prezzo attuale è dentro 'data' (che sono le variazioni di prezzo giornaliere)
                # La struttura di Keepa prevede che l'ultimo valore della lista sia quello attuale
                product_data = data['products'][0]['data']
                
                # Keepa restituisce i prezzi nei suoi array. L'ultimo elemento è il prezzo attuale.
                # In molti casi è l'ultimo valore della lista (es. se è una lista di prezzi nel tempo)
                # Il formato di Keepa: [timestamp, prezzo_in_centesimi]
                if product_data and len(product_data) > 0:
                    # In alcuni casi Keepa restituisce una lista di liste.
                    # Se la lista è piatta, proviamo a prendere l'ultimo valore
                    if isinstance(product_data[0], list):
                        last_price_cents = product_data[-1][1]
                    else:
                        # Se la struttura è diversa, l'ultimo numero è il prezzo attuale
                        last_price_cents = product_data[-1]
                    
                    current_price = last_price_cents / 100.0
                    print(f"💰 Prezzo Attuale (Keepa): € {current_price}")
                    return current_price
            print(f"⚠️ Prezzo attuale non trovato su Keepa per {asin}")
            return None
        else:
            print(f"❌ Errore API Keepa (Get Price): {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Errore connessione Keepa: {e}")
        return None

# --- 2. FUNZIONE PER OTTENERE IL PREZZO MINIMO STORICO DA KEEPA ---
def get_keepa_historical_price(asin):
    if not KEEPA_API_KEY:
        return None

    url = "https://api.keepa.com/product"
    params = {
        'key': KEEPA_API_KEY,
        'asin': asin,
        'domain': 10,
        'stats': 3600 # 3600 chiede il minimo storico
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
            print(f"❌ Errore API Keepa (Get History): {response.status_code}")
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
    print("🚀 Avvio bot con Keepa API (Zero Scraping!)...")
    
    for asin in ASIN_LIST:
        # Passo 1: Leggi il prezzo attuale direttamente da Keepa
        current_price = get_keepa_current_price(asin)
        
        if current_price:
            # Passo 2: Leggi il minimo storico da Keepa
            min_price = get_keepa_historical_price(asin)
            
            if min_price:
                # Passo 3: Confronta
                if current_price < min_price:
                    print(f"🚨 SCONTO ERRATO TROVATO! {asin} sotto il minimo storico!")
                    # Invia a Telegram (title lo mettiamo come ASIN per ora, funziona lo stesso)
                    send_telegram_alert(asin, asin, current_price, min_price)
                else:
                    print(f"ℹ️ Prezzo normale per {asin} (Sopra la media storica).")
            else:
                print(f"⏭️ Impossibile ottenere storico da Keepa per {asin}, salto.")
        else:
            print(f"⏭️ Prezzo attuale non trovato per {asin}, salto.")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
