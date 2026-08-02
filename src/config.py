"""
Configurazione centrale del bot "Offerte Universitarie".
Tutte le impostazioni sono qui. Modifica solo questo file.
"""

import os

# ============================================
# 1. CREDENZIALI (da variabili d'ambiente)
# ============================================

KEEPA_API_KEY = "m3t93ksddqntnpgibgijubm4s78u769rsrr9jah9p33m4aab4cinrot1170322ki"
TELEGRAM_BOT_TOKEN = "8854356674:AAF65IdHYZE1S3xSfeP6cqGn9X3yrxZYH9E"
TELEGRAM_CHANNEL_ID = "@offerteuniversitarie"
AMAZON_AFFILIATE_TAG = "offerteuni06-21"

# ============================================
# 2. DOMINI
# ============================================

AMAZON_DOMAIN = "amazon.it"
KEEPA_DOMAIN_ID = 8

# ============================================
# 3. CATEGORIE
# ============================================

CATEGORIE = {
    "studente": {
        "node_id": None,
        "emoji": "🎓",
        "label": "Prodotti per studenti",
        "termini_ricerca": [
            "computer+portatile+offerta",
            "zaino+studente+sconto",
            "libri+universitari+usati",
            "cuffie+studio+offerte",
            "powerbank+promozione",
            "penne+evidenziatori+offerta",
            "taccuino+universitario",
            "lampada+scrivania+led",
            "borraccia+acqua",
            "monitor+pc+studente",
            "mouse+wireless",
            "tastiera+bluetooth",
            "auricolari+sportivi",
            "caricabatterie+usb+rapido",
            "hard+disk+esterno",
            "quaderno+universitario",
            "calcolatrice+scientifica",
            "astuccio+grande",
            "mochila+studente",
            "agenda+universitaria",
        ]
    }
}

# ============================================
# 4. SOGLIE PER LE OFFERTE
# ============================================

SCONTO_MINIMO_PERCENTUALE = 0  # ABBASATO AL 2%
PREZZO_MINIMO = 3.0
PREZZO_MASSIMO = 500.0
SCONTO_MASSIMO_PLAUSIBILE = 80
SCONTO_TOP_PERCENTUALE = 30

# ============================================
# 5. COMPORTAMENTO DEL BOT
# ============================================

MAX_OFFERTE_PER_ESECUZIONE = 6
GIORNI_STORICO_PREZZO = 90
MAX_ASIN_PER_ESECUZIONE = 30
MAX_TERMINI_RICERCA = 8

# ============================================
# 6. ASIN MANUALI (PRODOTTI DA MONITORARE)
# ============================================

ASIN_MANUALI = [
     "B07X3T1F9J",  # Amazon Basics Cavo HDMI
    "B08N5WRWNW",  # Prodotto di esempio
]

# ============================================
# 7. TEMPLATE MESSAGGI
# ============================================

TEMPLATE_MESSAGGIO = """
{emoji} {titolo}

💰 Prezzo: {prezzo_attuale}€ invece di {prezzo_precedente}€ (-{sconto}%)

{frase_utilita}

👉 [Acquista su Amazon]({link})

#Offerte #Studenti
"""

TEMPLATE_TOP = """
🚨 OFFERTA IMPERDIBILE 🚨

{emoji} {titolo}

💰 {prezzo_attuale}€ invece di {prezzo_precedente}€ (-{sconto}%)

⭐ {frase_utilita}

⚠️ Prezzo ai minimi storici! Affrettati!

👉 [Acquista ora su Amazon]({link})

#OffertaTop #Studenti
"""

FRASI_UTILITA = {
    "studente": "🎓 Perfetto per la vita universitaria!",
    "tech": "💻 L'accessorio che ti semplifica lo studio.",
    "casa": "🏠 Rende il tuo spazio più accogliente.",
}
