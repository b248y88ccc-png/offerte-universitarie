"""
Modulo che pubblica i messaggi sul canale Telegram usando la Bot API.
"""

import requests
import config
import image_composer


def invia_messaggio(testo, immagine_url=None, immagine_bytes=None):
    """
    Invia un singolo post al canale.
    """
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHANNEL_ID:
        raise ValueError("TELEGRAM_BOT_TOKEN o TELEGRAM_CHANNEL_ID non impostati.")

    base_url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"

    # 1. Prova a inviare l'immagine generata (con badge)
    if immagine_bytes:
        url_foto = f"{base_url}/sendPhoto"
        files = {"photo": ("offerta.jpg", immagine_bytes, "image/jpeg")}
        data = {"chat_id": config.TELEGRAM_CHANNEL_ID, "caption": testo}
        risposta = requests.post(url_foto, data=data, files=files, timeout=30)
        if risposta.status_code == 200:
            print("   ✅ Messaggio con immagine badge inviato!")
            return True
        else:
            print(f"   ❌ Errore invio immagine badge: {risposta.status_code}")

    # 2. Prova con URL esterno
    if immagine_url:
        url_foto = f"{base_url}/sendPhoto"
        payload = {
            "chat_id": config.TELEGRAM_CHANNEL_ID,
            "photo": immagine_url,
            "caption": testo,
        }
        risposta = requests.post(url_foto, data=payload, timeout=30)
        if risposta.status_code == 200:
            print("   ✅ Messaggio con immagine URL inviato!")
            return True
        else:
            print(f"   ❌ Errore invio immagine URL: {risposta.status_code}")

    # 3. Fallback: solo testo
    url_testo = f"{base_url}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHANNEL_ID,
        "text": testo,
        "disable_web_page_preview": True,
    }
    risposta = requests.post(url_testo, data=payload, timeout=30)
    if risposta.status_code == 200:
        print("   ✅ Messaggio solo testo inviato!")
        return True
    else:
        print(f"   ❌ Errore invio testo: {risposta.status_code}")
        return False


def pubblica_batch(messaggi):
    """
    Pubblica una lista di messaggi.
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
        else:
            print(f"   ❌ Fallito invio per: {messaggio['testo'][:50]}...")
    print(f"📊 Pubblicati {pubblicati}/{len(messaggi)} messaggi.")
    return pubblicati
