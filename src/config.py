"""
Configurazione centrale del bot "Offerte Universitarie".
Tutte le impostazioni sono qui. Modifica solo questo file.
"""

import os

# ============================================
# 1. CREDENZIALI (da variabili d'ambiente)
# ============================================

# Keepa API - la tua chiave (da https://keepa.com)
# Imposta con: export KEEPA_API_KEY="la_tua_chiave"
KEEPA_API_KEY = os.environ.get("KEEPA_API_KEY")

# Telegram - token del bot (da @BotFather)
# Imposta con: export TELEGRAM_BOT_TOKEN="il_tuo_token"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Telegram - ID del canale (es. "@offerteuniversitarie")
# Imposta con: export TELEGRAM_CHANNEL_ID="@offerteuniversitarie"
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# Amazon Associates - il tuo tag affiliato
# Imposta con: export AMAZON_AFFILIATE_TAG="tuo-tag-21"
AMAZON_AFFILIATE_TAG = os.environ.get("AMAZON_AFFILIATE_TAG", "IL_TUO_TAG-21")


# ============================================
# 2. DOMINI
# ============================================

AMAZON_DOMAIN = "amazon.it"
KEEPA_DOMAIN_ID = 8  # 8 = Amazon Italia


# ============================================
# 3. CATEGORIE DA MONITORARE
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
    },
    "tech": {
        "node_id": None,
        "emoji": "💻",
        "label": "Tecnologia",
        "termini_ricerca": [
            "tablet+studente",
            "chromebook+offerta",
            "monitor+usato",
            "ssd+esterno",
            "hub+usb",
        ]
    },
    "casa": {
        "node_id": None,
        "emoji": "🏠",
        "label": "Casa per studenti",
        "termini_ricerca": [
            "mini+frigo+studente",
            "plaid+coperta",
            "cuscino+ergonomico",
            "organizzatore+scrivania",
            "appendiabiti",
        ]
    }
}


# ============================================
# 4. SOGLIE PER LE OFFERTE
# ============================================

# Sconto minimo per pubblicare un'offerta (%)
SCONTO_MINIMO_PERCENTUALE = 5  # Abbassato da 10 a 5

# Prezzo minimo del prodotto (in euro) - sotto questo non si pubblica
PREZZO_MINIMO = 3.0

# Prezzo massimo del prodotto (in euro) - sopra questo non si pubblica
PREZZO_MASSIMO = 500.0

# Sconto massimo plausibile (%) - oltre questo si scarta (probabile errore)
SCONTO_MASSIMO_PLAUSIBILE = 80

# Sconto per considerare un'offerta "top" (usa template speciale)
SCONTO_TOP_PERCENTUALE = 30


# ============================================
# 5. COMPORTAMENTO DEL BOT
# ============================================

# Numero massimo di offerte da pubblicare per esecuzione
MAX_OFFERTE_PER_ESECUZIONE = 6

# Numero di giorni di storico Keepa da usare per verificare lo sconto
GIORNI_STORICO_PREZZO = 90

# Numero massimo di ASIN da verificare per esecuzione
MAX_ASIN_PER_ESECUZIONE = 30

# Numero massimo di termini di ricerca da usare per esecuzione
MAX_TERMINI_RICERCA = 8


# ============================================
# 6. ASIN MANUALI DA MONITORARE (SEMPRE)
# ============================================

# Questi ASIN vengono sempre verificati, indipendentemente dalla ricerca
ASIN_MANUALI = [ "B0B4VXBMX6"
    # Inserisci qui gli ASIN dei prodotti che ti interessano
    # Esempi:
    # "B08N5WRWNW",
    # "B07X3T1F9J",
    # "B08L5V5Z7K",
]


# ============================================
# 7. SETTINGS PER LE IMMAGINI
# ============================================

# Dimensioni dell'immagine da generare (in pixel)
DIMENSIONE_IMMAGINE = 1080

# Colori per il badge delle offerte
COLORE_BADGE_SFONDO = (255, 255, 255, 235)  # Bianco semi-trasparente
COLORE_SCONTO = (214, 39, 40)  # Rosso
COLORE_PREZZO = (20, 20, 20)  # Nero
COLORE_PREZZO_VECCHIO = (140, 140, 140)  # Grigio


# ============================================
# 8. SETTINGS PER IL MESSAGGIO TELEGRAM
# ============================================

# Template del messaggio (usa {variabili} per sostituire)
TEMPLATE_MESSAGGIO = """
{emoji} {titolo}

💰 Prezzo: {prezzo_attuale}€ invece di {prezzo_precedente}€ (-{sconto}%)

{frase_utilita}

👉 [Acquista su Amazon]({link})

#Offerte #Studenti
"""

# Template per offerte "top" (sconto > SCONTO_TOP_PERCENTUALE)
TEMPLATE_TOP = """
🚨 OFFERTA IMPERDIBILE 🚨

{emoji} {titolo}

💰 {prezzo_attuale}€ invece di {prezzo_precedente}€ (-{sconto}%)

⭐ {frase_utilita}

⚠️ Prezzo ai minimi storici! Affrettati!

👉 [Acquista ora su Amazon]({link})

#OffertaTop #Studenti
"""

# Frasi utili per gli studenti (per categoria)
FRASI_UTILITA = {
    "studente": "🎓 Perfetto per la vita universitaria!",
    "tech": "💻 L'accessorio che ti semplifica lo studio.",
    "casa": "🏠 Rende il tuo spazio più accogliente.",
    "libri": "📖 Il libro che ti serve per l'esame.",
    "cancelleria": "✍️ Tutto ciò che serve per i tuoi appunti.",
}


# ============================================
# 9. SETTINGS PER IL LOG
# ============================================

# Livello di log: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_LEVEL = "INFO"

# Mostra i dettagli di debug (True/False)
DEBUG = True


# ============================================
# 10. VALIDAZIONE DELLE IMPOSTAZIONI
# ============================================

def valida_config():
    """Controlla che le impostazioni siano valide."""
    errori = []
    
    if not KEEPA_API_KEY:
        errori.append("KEEPA_API_KEY non impostata")
    if not TELEGRAM_BOT_TOKEN:
        errori.append("TELEGRAM_BOT_TOKEN non impostato")
    if not TELEGRAM_CHANNEL_ID:
        errori.append("TELEGRAM_CHANNEL_ID non impostato")
    
    if SCONTO_MINIMO_PERCENTUALE < 0 or SCONTO_MINIMO_PERCENTUALE > 100:
        errori.append("SCONTO_MINIMO_PERCENTUALE deve essere tra 0 e 100")
    
    if PREZZO_MINIMO < 0 or PREZZO_MINIMO > PREZZO_MASSIMO:
        errori.append("PREZZO_MINIMO deve essere minore di PREZZO_MASSIMO")
    
    if errori:
        print("⚠️ Errori nella configurazione:")
        for errore in errori:
            print(f"   ❌ {errore}")
        return False
    
    print("✅ Configurazione valida")
    return True


# Se esegui questo file direttamente, mostra la configurazione
if __name__ == "__main__":
    print("=" * 50)
    print("CONFIGURAZIONE DEL BOT")
    print("=" * 50)
    print(f"KEEPA_API_KEY: {'✅ Impostata' if KEEPA_API_KEY else '❌ Non impostata'}")
    print(f"TELEGRAM_BOT_TOKEN: {'✅ Impostato' if TELEGRAM_BOT_TOKEN else '❌ Non impostato'}")
    print(f"TELEGRAM_CHANNEL_ID: {TELEGRAM_CHANNEL_ID or '❌ Non impostato'}")
    print(f"AMAZON_AFFILIATE_TAG: {AMAZON_AFFILIATE_TAG}")
    print(f"SCONTO_MINIMO: {SCONTO_MINIMO_PERCENTUALE}%")
    print(f"PREZZO: {PREZZO_MINIMO}€ - {PREZZO_MASSIMO}€")
    print(f"MAX_OFFERTE: {MAX_OFFERTE_PER_ESECUZIONE}")
    print(f"CATEGORIE: {len(CATEGORIE)}")
    print(f"ASIN MANUALI: {len(ASIN_MANUALI)}")
    valida_config()
