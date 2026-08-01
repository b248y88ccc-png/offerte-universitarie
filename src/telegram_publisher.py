"""
Modulo che pubblica i messaggi sul canale Telegram usando la Bot API,
via semplici chiamate HTTP (nessuna libreria complessa necessaria).
"""

import time
import requests

import config


def _invia_richiesta(url, payload):
    """Esegue la chiamata HTTP e ritorna True/False in base all'esito."""
    risposta = requests.post(url, data=payload, timeout=15)
    if risposta.status_code != 200:
        print(f"[errore invio] {risposta.status_code}: {risposta.text}")
        return False
    return True


def invia_messaggio(testo, immagine_url=None, immagine_bytes=None):
    """
    Invia un singolo post al canale.

    - Se 'immagine_bytes' è fornito (immagine generata localmente, es. con
      il badge prezzo sovrapposto), viene caricata direttamente come file.
    - Altrimenti, se c'è 'immagine_url', Telegram scarica lui stesso l'immagine.
    - Se entrambe falliscono/mancano, invia solo testo (con l'anteprima
      automatica del link disattivata, per evitare la card generata da Telegram).
    """
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHANNEL_ID:
        raise ValueError("TELEGRAM_BOT_TOKEN o TELEGRAM_CHANNEL_ID non impostati.")

    base_url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"

    # --- Tentativo 1: immagine composta localmente (file caricato direttamente) ---
    if immagine_bytes:
        url_foto = f"{base_url}/sendPhoto"
        files = {"photo": ("offerta.jpg", immagine_bytes, "image/jpeg")}
        data = {"chat_id": config.TELEGRAM_CHANNEL_ID, "caption": testo}
        risposta = requests.post(url_foto, data=data, files=files, timeout=30)
        if risposta.status_code == 200:
            return True
        print(f"[errore invio foto locale] {risposta.status_code}: {risposta.text}")
        print("[fallback] Riprovo con l'URL esterno, se disponibile...")

    # --- Tentativo 2: URL esterno dell'immagine ---
    if immagine_url:
        url_foto = f"{base_url}/sendPhoto"
        payload_foto = {
            "chat_id": config.TELEGRAM_CHANNEL_ID,
            "photo": immagine_url,
            "caption": testo,
        }
        if _invia_richiesta(url_foto, payload_foto):
            return True
        print("[fallback] Invio immagine fallito, riprovo come solo testo...")

    # --- Tentativo 3: solo testo, senza generare l'anteprima automatica del link ---
    url_testo = f"{base_url}/sendMessage"
    payload_testo = {
        "chat_id": config.TELEGRAM_CHANNEL_ID,
        "text": testo,
        "disable_web_page_preview": True,
    }
    return _invia_richiesta(url_testo, payload_testo)


def pubblica_batch(messaggi):
    """
    Pubblica una lista di messaggi con una pausa tra uno e l'altro,
    per non affollare il canale ed evitare i rate limit di Telegram.
    """
    pubblicati = 0
    for messaggio in messaggi:
        successo = invia_messaggio(
            messaggio["testo"],
            immagine_url=messaggio.get("immagine"),
            immagine_bytes=messaggio.get("immagine_bytes"),
        )
        if successo:
            pubblicati += 1
        time.sleep(5)  # piccola pausa di cortesia tra un post e l'altro

    print(f"Pubblicati {pubblicati}/{len(messaggi)} post.")
    return pubblicati
