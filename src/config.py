"""
Configurazione centrale del bot "Offerte Universitarie".
Tutte le impostazioni sono qui. Modifica solo questo file.
"""

import os

# ============================================
# 1. CREDENZIALI (da variabili d'ambiente)
# ============================================

KEEPA_API_KEY = os.environ.get("KEEPA_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
AMAZON_AFFILIATE_TAG = os.environ.get("AMAZON_AFFILIATE_TAG", "IL_TUO_TAG-21")

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

SCONTO_MINIMO_PERCENTUALE = 2  # ABBASATO AL 2%
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
    "B07V5KK3PD",  # Norton Antivirus
    "B0B4VXBMX6",  # Tastiera Dierya
    "B0D8FR9DMR",  # Prodotto in offerta
    "B0BZMLKXL4",  # Prodotto in offerta
    "B0DGKDRXYZ",  # Prodotto in offerta
    "B08J7G9S1F",  # Prodotto in offerta
    "B0CQK8TZCF",  # Prodotto in offerta
    "B0D45KJ86P",  # Prodotto in offerta
    "B0D7MN4W7H",  # Prodotto in offerta
    "B0DPQKWBZJ",  # Prodotto in offerta
    "B0BPMHFNTJ",  # Prodotto in offerta
    "B0FKBDT8FR",  # Prodotto in offerta
    "B0DD43PYQ6",  # Prodotto in offerta
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
