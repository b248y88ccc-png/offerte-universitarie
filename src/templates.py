"""
Costruisce il testo del post Telegram a partire da un'offerta.
"""

import config
import image_composer


def costruisci_frase_utilita(categoria_key, titolo):
    if categoria_key in config.FRASI_UTILITA:
        return config.FRASI_UTILITA[categoria_key]
    
    titolo_lower = titolo.lower()
    if any(word in titolo_lower for word in ["libro", "manuale", "testo"]):
        return "📖 Perfetto per lo studio e gli esami!"
    elif any(word in titolo_lower for word in ["computer", "portatile", "tablet"]):
        return "💻 L'alleato ideale per le tue lezioni!"
    else:
        return "🎓 Utile per la tua esperienza universitaria!"


def costruisci_messaggio(offerta):
    titolo = offerta["titolo"]
    prezzo_attuale = offerta["prezzo_attuale_eur"]
    prezzo_precedente = offerta["prezzo_precedente_eur"]
    sconto = offerta["sconto_percentuale"]
    link = offerta["link"]
    emoji = offerta.get("categoria_info", {}).get("emoji", "🎓")
    categoria_key = offerta.get("categoria_key", "studente")
    
    frase_utilita = costruisci_frase_utilita(categoria_key, titolo)
    
    if sconto >= config.SCONTO_TOP_PERCENTUALE:
        template = config.TEMPLATE_TOP
    else:
        template = config.TEMPLATE_MESSAGGIO
    
    messaggio = template.format(
        emoji=emoji,
        titolo=titolo,
        prezzo_attuale=prezzo_attuale,
        prezzo_precedente=prezzo_precedente,
        sconto=sconto,
        frase_utilita=frase_utilita,
        link=link,
    )
    
    return messaggio


def costruisci_messaggi_batch(lista_offerte):
    """
    Costruisce una lista di messaggi per tutte le offerte.
    """
    messaggi = []
    for offerta in lista_offerte:
        testo = costruisci_messaggio(offerta)
        
        # Genera immagine con badge
        immagine_bytes = None
        immagine_url = offerta.get("immagine")
        
        if immagine_url:
            try:
                immagine_bytes = image_composer.componi_immagine_offerta(
                    immagine_url,
                    offerta["prezzo_attuale_eur"],
                    offerta["prezzo_precedente_eur"],
                    offerta["sconto_percentuale"],
                )
            except Exception as e:
                print(f"   ❌ Errore badge: {e}")
        
        messaggi.append({
            "testo": testo,
            "immagine": immagine_url,
            "immagine_bytes": immagine_bytes,
        })
    
    return messaggi
