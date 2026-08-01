"""
Modulo che usa Keepa per VERIFICARE le offerte.
NON usa /deal (che non funziona), usa solo /product (che FUNZIONA).
"""

import config
import requests
import time
import re


def _chiamata_keepa(endpoint, parametri):
    """Effettua una chiamata all'API Keepa."""
    url = f"https://api.keepa.com/{endpoint}"
    parametri["key"] = config.KEEPA_API_KEY
    
    try:
        risposta = requests.get(url, params=parametri, timeout=30)
        risposta.raise_for_status()
        return risposta.json()
    except Exception as e:
        print(f"[errore API] {e}")
        return None


def costruisci_url_immagine(codice_immagine):
    """Trasforma il codice immagine Keepa in URL Amazon."""
    if not codice_immagine:
        return None

    if isinstance(codice_immagine, list):
        try:
            nome_file = "".join(chr(v) for v in codice_immagine)
        except:
            return None
    elif isinstance(codice_immagine, str):
        nome_file = codice_immagine
    else:
        return None

    if not nome_file:
        return None

    if "." in nome_file:
        nome, estensione = nome_file.rsplit(".", 1)
    else:
        nome, estensione = nome_file, "jpg"

    return f"https://m.media-amazon.com/images/I/{nome}._SL1000_.{estensione}"


def verifica_offerta_con_keepa(asin):
    """
    Verifica un singolo ASIN usando Keepa.
    Ritorna i dettagli dell'offerta se valida, altrimenti None.
    """
    # Salta ASIN che sembrano ISBN (numeri di 10-13 cifre)
    if re.match(r'^\d{10,13}$', str(asin)):
        return None
    
    parametri = {
        "asin": asin,
        "domain": config.KEEPA_DOMAIN_ID,
        "stats": "1",
        "history": "1",
    }
    
    dati = _chiamata_keepa("product", parametri)
    
    if not dati or "products" not in dati:
        return None
    
    prodotto = dati["products"][0] if dati["products"] else None
    if not prodotto:
        return None
    
    # Prezzo attuale
    prezzi = prodotto.get("prices", [])
    if not prezzi or prezzi[-1] <= 0:
        return None
    prezzo_attuale = prezzi[-1] / 100
    
    # Titolo
    titolo = prodotto.get("title", "Prodotto")
    
    # Immagine
    immagine = None
    immagini = prodotto.get("images", [])
    if immagini:
        immagine = costruisci_url_immagine(immagini[0])
    
    # Minimo storico
    minimo_storico = None
    stats = prodotto.get("stats_parsed", {})
    if stats:
        if "min" in stats:
            min_val = stats["min"].get("AMAZON")
            if min_val and min_val > 0:
                minimo_storico = min_val / 100
        
        if minimo_storico is None:
            avg30 = stats.get("avg30", {}).get("AMAZON")
            if avg30 and avg30 > 0:
                minimo_storico = avg30 / 100
    
    if minimo_storico is None or minimo_storico <= 0:
        # Fallback: usa lo storico
        storico = prodotto.get("history", [])
        if storico:
            prezzi_storici = []
            for entry in storico:
                if isinstance(entry, list) and len(entry) >= 2:
                    p = entry[1]
                    if p and p > 0:
                        prezzi_storici.append(p / 100)
            if prezzi_storici:
                minimo_storico = min(prezzi_storici)
    
    if minimo_storico is None or minimo_storico <= 0:
        minimo_storico = prezzo_attuale * 0.85
    
    # Calcola sconto
    if prezzo_attuale >= minimo_storico:
        sconto = 0
    else:
        sconto = round((1 - prezzo_attuale / minimo_storico) * 100)
    
    # Filtra
    if sconto < config.SCONTO_MINIMO_PERCENTUALE:
        return None
    if sconto > config.SCONTO_MASSIMO_PLAUSIBILE:
        return None
    
    return {
        "asin": asin,
        "titolo": titolo,
        "immagine": immagine,
        "prezzo_attuale_eur": round(prezzo_attuale, 2),
        "prezzo_precedente_eur": round(minimo_storico, 2),
        "sconto_percentuale": sconto,
        "link": f"https://www.amazon.it/dp/{asin}?tag={config.AMAZON_AFFILIATE_TAG}",
    }


def trova_offerte_su_amazon():
    """
    Cerca offerte su Amazon via scraping.
    """
    print("🔍 Cerco offerte su Amazon...")
    
    # Termini di ricerca per studenti
    termini = config.CATEGORIE["studente"]["termini_ricerca"]
    
    tutte_le_offerte = []
    asins_da_verificare = []
    
    # ASIN manuale da testare (aggiunto direttamente)
    asins_da_verificare.append("B0B4VXBMX6")
    print(f"   📋 Aggiunto ASIN manuale: B0B4VXBMX6")
    
    for termine in termini[:config.MAX_TERMINI_RICERCA]:
        url = f"https://www.amazon.it/s?k={termine}&rh=p_n_deal_type%3A2356605031&language=it"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        }
        
        try:
            print(f"   Cerco: {termine}...")
            risposta = requests.get(url, headers=headers, timeout=15)
            risposta.raise_for_status()
            soup = BeautifulSoup(risposta.text, 'html.parser')
            
            # Estrai ASIN
            risultati = soup.select('[data-component-type="s-search-result"]')
            for elem in risultati[:8]:
                asin = elem.get('data-asin')
                if asin and asin != "" and not re.match(r'^\d{10,13}$', asin):
                    asins_da_verificare.append(asin)
            
            time.sleep(1.5)
            
        except Exception as e:
            print(f"   ❌ Errore per {termine}: {e}")
    
    # Rimuovi duplicati
    asins_da_verificare = list(set(asins_da_verificare))
    print(f"   📊 Trovati {len(asins_da_verificare)} ASIN unici")
    
    # Limita il numero di ASIN da verificare
    asins_da_verificare = asins_da_verificare[:config.MAX_ASIN_PER_ESECUZIONE]
    
    # Verifica con Keepa
    print("🔍 Verifico le offerte con Keepa...")
    for asin in asins_da_verificare:
        print(f"   Verifico: {asin}...")
        offerta = verifica_offerta_con_keepa(asin)
        if offerta:
            tutte_le_offerte.append(offerta)
            titolo_corto = offerta['titolo'][:40] + "..." if len(offerta['titolo']) > 40 else offerta['titolo']
            print(f"      ✅ {titolo_corto} - {offerta['sconto_percentuale']}%")
        else:
            print(f"      ❌ Nessuna offerta valida")
        time.sleep(0.3)
    
    return tutte_le_offerte


def trova_tutte_le_offerte():
    """
    Funzione principale.
    """
    print("🚀 Avvio bot offerte universitarie...")
    
    if not config.KEEPA_API_KEY:
        print("❌ KEEPA_API_KEY non impostata!")
        return []

    # Test connessione Keepa
    test = _chiamata_keepa("product", {"asin": "B08N5WRWNW", "domain": 8})
    if not test or "products" not in test:
        print("❌ Errore nella connessione a Keepa. Verifica la tua API key.")
        return []
    
    print("✅ Connessione a Keepa OK")

    # Trova offerte
    offerte = trova_offerte_su_amazon()
    
    if not offerte:
        print("❌ Nessuna offerta trovata")
        return []
    
    print(f"🎯 Offerte valide: {len(offerte)}")
    offerte.sort(key=lambda o: o["sconto_percentuale"], reverse=True)
    return offerte[:config.MAX_OFFERTE_PER_ESECUZIONE]
