import os
import time
import re
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# --- CONFIGURAZIONE (Legge le variabili da GitHub Secrets) ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

# Lista prodotti da controllare (Sostituiscili con i tuoi ASIN)
ASIN_LIST = [
    "B07X3T1F93",
    "B08N5WRWNW",
]

def get_amazon_price_with_playwright(asin):
    """Funzione che apre un vero browser per evitare il 503"""
    try:
        with sync_playwright() as p:
            # Lancia il browser Chromium in modalità headless (invisibile)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Vai su Amazon
            url = f"https://www.amazon.it/dp/{asin}"
            print(f"🔍 Apro browser per ASIN: {asin}")
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Aspetta che il prezzo sia visibile (fino a 5 secondi)
            try:
                page.wait_for_selector(".a-price-whole, .a-offscreen", timeout=5000)
            except:
                pass # Se non trova il prezzo, va avanti lo stesso
            
            # Legge l'HTML
            html = page.content()
            browser.close()
            
            # Analizza con BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # 1. Estrai il Titolo
            title_elem = soup.select_one('#productTitle')
            title = title_elem.get_text(strip=True) if title_elem else f"Prodotto ASIN {asin}"
            
            # 2. Estrai il Prezzo (Playwright carica il DOM completo, quindi funziona)
            price_elem = soup.select_one('.a-price-whole') # Formato classico
            if not price_elem:
                price_elem = soup.select_one('.a-offscreen') # Formato alternativo
            
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace('.', '').replace(',', '.')
                # Prende solo i numeri
                price_match = re.search(r'(\d+(?:\.\d+)?)', price_text)
                if price_match:
                    price = float(price_match.group(1))
                    print(f"💰 Prezzo trovato: € {price}")
                    return price, title
            
            print(f"⚠️ Prezzo non rilevato per {asin}")
            return None, title

    except Exception as e:
        print(f"❌ Errore grave con Playwright per {asin}: {e}")
        return None, None

def send_telegram_alert(asin, title, price):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("❌ Token Telegram mancanti!")
        return

    link = f"https://www.amazon.it/dp/{asin}"
    image_url = f"https://images-eu.ssl-images-amazon.com/images/I/41{asin}.jpg" # Placeholder immagine
    
    caption = f"🛒 *{title[:50]}...*\n\n" \
              f"💰 Prezzo attuale: *€ {price:.2f}*\n" \
              f"(Sconto rilevato!)\n\n" \
              f"🛍️ [Acquista su Amazon]({link})"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'photo': image_url,
        'caption': caption,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Inviato su Telegram!")
        else:
            print(f"❌ Errore Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Errore connessione Telegram: {e}")

def main():
    print("🚀 Avvio bot...")
    
    # Per avere un risultato "Sconti Errati", dobbiamo avere un prezzo storico.
    # Dato che non hai un database, controlliamo se il prezzo è molto basso rispetto alla media.
    soglia_sconto = 50.0 # Se il prezzo è sotto i 50€, lo mandiamo (esempio fittizio)
    
    for asin in ASIN_LIST:
        price, title = get_amazon_price_with_playwright(asin)
        
        if price:
            # LOGICA SCONTO: Se prezzo è inferiore alla soglia
            if price < soglia_sconto: 
                print(f"🚨 SCONTO TROVATO! {asin} a € {price}")
                send_telegram_alert(asin, title, price)
            else:
                print(f"ℹ️ Prezzo normale per {asin} (€ {price})")
        
        # Aspetta 5 secondi prima di fare il prossimo prodotto, per non sovraccaricare Amazon
        time.sleep(5)

if __name__ == "__main__":
    main()
