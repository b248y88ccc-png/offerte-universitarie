"""
Modulo che TROVA offerte su Amazon (scraping) e le VERIFICA con Keepa.
VERSIONE SEMPLIFICATA E ROBUSTA.
"""

import config
import requests
from bs4 import BeautifulSoup
import time
import re


def _chiamata_keepa(endpoint, parametri):
    """Effettua una chiamata all'API Keepa."""
    url = f"https://api.keepa.com/{endpoint}"
    parametri["key"] = config.KEEPA_API_KEY
    try:
        print(f"   📡 Chiamata Keepa: {endpoint} per {parametri.get('asin', '')}")
        risposta = requests.get(url, params=parametri, timeout=30)
        risposta.raise_for_status()
        dati = risposta.json()
        return dati
    except Exception as e:
        print(f"   ❌ Errore API Keepa: {e}")
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


def verifica_con_keepa(asin):
    """Verifica un singolo ASIN con Keepa."""
    print(f"   🔍 Verifico: {asin}...")
    
    # Salta codici che sembrano ISBN
    if re.match(r'^\d{10,13}$', str(asin)):
        print(f"   ⚠️ Saltato (sembra un ISBN)")
        return None
    
    # Chiamata API
    parametri = {
        "asin": asin,
        "domain": config.KEEPA_DOMAIN_ID,
        "stats": "1",
    }
    
    dati = _chiamata_keepa("product", parametri)
    
    # Controlli di sicurezza
    if not dati:
        print(f"   ❌ Nessuna risposta da Keepa")
        return None
    
    if "products" not in dati:
        print(f"   ⚠️ Risposta senza 'products'")
        return None
    
    if not dati["products"]:
        print(f"   ⚠️ Nessun prodotto trovato per {asin}")
        return None
    
    prodotto = dati["products"][0]
    
    # SE IL PRODOTTO È NONE, SALTA
    if prodotto is None:
        print(f"   ⚠️ Prodotto None per {asin}")
        return None
    
    # SE IL PRODOTTO NON È UN DIZIONARIO, SALTA
    if not isinstance(prodotto, dict):
        print(f"   ⚠️ Prodotto non è un dizionario: {type(prodotto)}")
        return None
    
    # Prezzo attuale
    prezzi = prodotto.get("prices")
    if not prezzi or not isinstance(prezzi, list) or len(prezzi) == 0:
        print(f"   ❌ Prezzo non disponibile per {asin}")
        return None
    
    if prezzi[-1] is None or prezzi[-1] <= 0:
        print(f"   ❌ Prezzo non valido per {asin}")
        return None
    
    prezzo_attuale = prezzi[-1] / 100
    titolo = prodotto.get("title", "Prodotto")
    
    # Immagine
    immagine = None
    immagini = prodotto.get("images", [])
    if immagini and isinstance(immagini, list) and len(immagini) > 0:
        immagine = costruisci_url_immagine(immagini[0])
    
    # Minimo storico (da stats)
    minimo_storico = None
    stats = prodotto.get("stats_parsed", {})
    if stats and isinstance(stats, dict):
        if "min" in stats and isinstance(stats["min"], dict):
            min_val = stats["min"].get("AMAZON")
            if min_val and min_val > 0:
                minimo_storico = min_val / 100
        
        if minimo_storico is None and "avg30" in stats and isinstance(stats["avg30"], dict):
            avg30 = stats["avg30"].get("AMAZON")
            if avg30 and avg30 > 0:
                minimo_storico = avg30 / 100
    
    # Se non c'è minimo, usa fallback
    if minimo_storico is None or minimo_storico <= 0:
        minimo_storico = prezzo_attuale * 0.90  # Fallback: 10% di sconto ipotetico
    
    # Calcola sconto
    if prezzo_attuale >= minimo_storico:
        sconto = 0
    else:
        sconto = round((1 - prezzo_attuale / minimo_storico) * 100)
    
    print(f"   💰 Prezzo: {prezzo_attuale}€ | Minimo: {minimo_storico}€ | Sconto: {sconto}%")
    
    # Filtra per sconto
    if sconto < config.SCONTO_MINIMO_PERCENTUALE:
        print(f"   ❌ Sconto {sconto}% < soglia {config.SCONTO_MINIMO_PERCENTUALE}%")
        return None
    
    if sconto > config.SCONTO_MASSIMO_PLAUSIBILE:
        print(f"   ❌ Sconto {sconto}% > max {config.SCONTO_MASSIMO_PLAUSIBILE}%")
        return None
    
    print(f"   ✅ OFFERTA VALIDA!")
    
    return {
        "asin": asin,
        "titolo": titolo,
        "immagine": immagine,
        "prezzo_attuale_eur": round(prezzo_attuale, 2),
        "prezzo_precedente_eur": round(minimo_storico, 2),
        "sconto_percentuale": sconto,
        "link": f"https://www.amazon.it/dp/{asin}?tag={config.AMAZON_AFFILIATE_TAG}",
    }


def trova_tutte_le_offerte():
    """Funzione principale."""
    print("🚀 Avvio bot offerte universitarie...")
    
    if not config.KEEPA_API_KEY:
        print("❌ KEEPA_API_KEY non impostata!")
        return []

    # Test connessione
    test = _chiamata_keepa("product", {"asin": "B07X3T1F9J", "domain": 8})
    if not test or "products" not in test:
        print("❌ Errore nella connessione a Keepa. Verifica la tua API key.")
        return []
    
    print("✅ Connessione a Keepa OK")
    
    # Lista ASIN da verificare
    asins_da_verificare = []
    
    # 1. ASIN manuali da config
    if config.ASIN_MANUALI:
        print(f"   📋 Aggiungo {len(config.ASIN_MANUALI)} ASIN manuali...")
        asins_da_verificare.extend(config.ASIN_MANUALI)
    
    # 2. Scraping Amazon (solo se abbiamo pochi ASIN manuali)
    if len(asins_da_verificare) < 5:
        print("🔍 Cerco offerte su Amazon...")
        termini = config.CATEGORIE["studente"]["termini_ricerca"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        }
        
        for termine in termini[:config.MAX_TERMINI_RICERCA]:
            url = f"https://www.amazon.it/s?k={termine}&rh=p_n_deal_type%3A2356605031&language=it"
            try:
                print(f"   Cerco: {termine}...")
                risposta = requests.get(url, headers=headers, timeout=15)
                risposta.raise_for_status()
                soup = BeautifulSoup(risposta.text, 'html.parser')
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
    print(f"   📊 Totale ASIN da verificare: {len(asins_da_verificare)}")
    
    # Limita il numero
    asins_da_verificare = asins_da_verificare[:config.MAX_ASIN_PER_ESECUZIONE]
    
    # Verifica ogni ASIN
    print("🔍 Verifico le offerte con Keepa...")
    offerte_valide = []
    for asin in asins_da_verificare:
        offerta = verifica_con_keepa(asin)
        if offerta:
            offerte_valide.append(offerta)
        time.sleep(0.2)  # Rispetta i limiti API
    
    print(f"🎯 Offerte valide: {len(offerte_valide)}")
    offerte_valide.sort(key=lambda o: o["sconto_percentuale"], reverse=True)
    return offerte_valide[:config.MAX_OFFERTE_PER_ESECUZIONE]
