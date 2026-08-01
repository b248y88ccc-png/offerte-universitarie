"""
Costruisce il testo del post Telegram a partire da un'offerta.
Supporta template standard e template per offerte top.
"""

import config


def costruisci_frase_utilita(categoria_key, titolo):
    """
    Sceglie una frase utile in base alla categoria e al titolo.
    """
    # Prova a trovare una frase specifica per la categoria
    if categoria_key in config.FRASI_UTILITA:
        return config.FRASI_UTILITA[categoria_key]
    
    # Altrimenti, genera una frase in base al titolo
    titolo_lower = titolo.lower()
    if any(word in titolo_lower for word in ["libro", "manuale", "testo", "edizione"]):
        return "📖 Perfetto per lo studio e gli esami!"
    elif any(word in titolo_lower for word in ["computer", "portatile", "tablet", "monitor"]):
        return "💻 L'alleato ideale per le tue lezioni!"
    elif any(word in titolo_lower for word in ["zaino", "borraccia", "lampada"]):
        return "🎒 Comodo e pratico per la vita universitaria!"
    else:
        return "🎓 Utile per la tua esperienza universitaria!"


def costruisci_messaggio(offerta):
    """
    Costruisce il messaggio Telegram per un'offerta.
    Sceglie il template in base allo sconto.
    """
    titolo = offerta["titolo"]
    prezzo_attuale = offerta["prezzo_attuale_eur"]
    prezzo_precedente = offerta["prezzo_precedente_eur"]
    sconto = offerta["sconto_percentuale"]
    link = offerta["link"]
    emoji = offerta["categoria_info"]["emoji"]
    categoria_key = offerta["categoria_key"]
    
    frase_utilita = costruisci_frase_utilita(categoria_key, titolo)
    
    # Scegli il template in base allo sconto
    if sconto >= config.SCONTO_TOP_PERCENTUALE:
        template = config.TEMPLATE_TOP
    else:
        template = config.TEMPLATE_MESSAGGIO
    
    # Formatta il messaggio
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
        messaggi.append({
            "testo": testo,
            "immagine": offerta.get("immagine"),
            "immagine_bytes": None,  # Per ora non generiamo immagini
        })
    return messaggi