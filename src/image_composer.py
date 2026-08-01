"""
Genera l'immagine finale da pubblicare: foto del prodotto + un badge con
prezzo e sconto sovrapposto in basso a destra, nello stile dei canali
offerte più curati (prezzo attuale in grande, prezzo originale barrato,
percentuale di sconto in rosso).
"""

import io
import requests
from PIL import Image, ImageDraw, ImageFont
import matplotlib.font_manager as fm


# --- Font: usiamo quelli inclusi in matplotlib, così funzionano ovunque
# (Mac, Windows, Linux/GitHub Actions) senza bisogno di installarli a parte ---
_FONT_BOLD_PATH = fm.findfont(fm.FontProperties(family="DejaVu Sans", weight="bold"))
_FONT_REGULAR_PATH = fm.findfont(fm.FontProperties(family="DejaVu Sans", weight="normal"))

# Dimensione base del canvas quadrato su cui viene composta l'immagine finale
DIMENSIONE_CANVAS = 1080

# Colori
COLORE_SFONDO = (255, 255, 255)
COLORE_BADGE_SFONDO = (255, 255, 255, 235)  # bianco quasi opaco
COLORE_SCONTO = (214, 39, 40)               # rosso
COLORE_PREZZO = (20, 20, 20)                # nero/grigio scurissimo
COLORE_PREZZO_VECCHIO = (140, 140, 140)     # grigio


def _scarica_immagine(url):
    """Scarica l'immagine del prodotto e la ritorna come oggetto PIL."""
    risposta = requests.get(url, timeout=15)
    risposta.raise_for_status()
    return Image.open(io.BytesIO(risposta.content)).convert("RGBA")


def _disegna_testo_barrato(draw, posizione, testo, font, colore):
    """Disegna un testo con una riga sopra, per simulare il prezzo barrato."""
    x, y = posizione
    bbox = draw.textbbox((x, y), testo, font=font)
    draw.text((x, y), testo, font=font, fill=colore)
    y_linea = (bbox[1] + bbox[3]) // 2
    draw.line([(bbox[0], y_linea), (bbox[2], y_linea)], fill=colore, width=max(2, (bbox[3] - bbox[1]) // 12))


def componi_immagine_offerta(url_immagine_prodotto, prezzo_attuale, prezzo_precedente, sconto_percentuale):
    """
    Scarica la foto del prodotto e ci sovrappone un badge con prezzo e sconto.
    Ritorna i byte dell'immagine finale (JPEG), pronti per essere caricati su Telegram.
    Se qualcosa va storto (immagine non scaricabile, ecc.) ritorna None:
    in quel caso chi chiama questa funzione dovrebbe usare un fallback.
    """
    try:
        foto_prodotto = _scarica_immagine(url_immagine_prodotto)
    except Exception as e:
        print(f"[image_composer] Impossibile scaricare l'immagine: {e}")
        return None

    # Canvas quadrato con sfondo bianco, la foto del prodotto viene centrata
    # e ridimensionata mantenendo le proporzioni (niente tagli o distorsioni)
    canvas = Image.new("RGBA", (DIMENSIONE_CANVAS, DIMENSIONE_CANVAS), COLORE_SFONDO + (255,))

    foto_prodotto.thumbnail((int(DIMENSIONE_CANVAS * 0.92), int(DIMENSIONE_CANVAS * 0.92)))
    pos_x = (DIMENSIONE_CANVAS - foto_prodotto.width) // 2
    pos_y = (DIMENSIONE_CANVAS - foto_prodotto.height) // 2
    canvas.paste(foto_prodotto, (pos_x, pos_y), foto_prodotto)

    draw = ImageDraw.Draw(canvas, "RGBA")

    # --- Testi del badge ---
    testo_sconto = f"-{sconto_percentuale}%"
    testo_prezzo = f"{prezzo_attuale:.2f}€".replace(".", ",")
    testo_prezzo_vecchio = f"{prezzo_precedente:.2f}€".replace(".", ",")

    font_sconto = ImageFont.truetype(_FONT_BOLD_PATH, 46)
    font_prezzo = ImageFont.truetype(_FONT_BOLD_PATH, 68)
    font_prezzo_vecchio = ImageFont.truetype(_FONT_REGULAR_PATH, 38)

    # Calcolo dimensioni badge in base al testo più largo
    bbox_prezzo = draw.textbbox((0, 0), testo_prezzo, font=font_prezzo)
    larghezza_badge = max(bbox_prezzo[2] - bbox_prezzo[0] + 60, 320)
    altezza_badge = 210

    margine = 30
    x0 = DIMENSIONE_CANVAS - larghezza_badge - margine
    y0 = DIMENSIONE_CANVAS - altezza_badge - margine
    x1 = DIMENSIONE_CANVAS - margine
    y1 = DIMENSIONE_CANVAS - margine

    draw.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=COLORE_BADGE_SFONDO)

    padding_interno = 30
    testo_x = x0 + padding_interno

    draw.text((testo_x, y0 + 18), testo_sconto, font=font_sconto, fill=COLORE_SCONTO)
    draw.text((testo_x, y0 + 72), testo_prezzo, font=font_prezzo, fill=COLORE_PREZZO)
    _disegna_testo_barrato(draw, (testo_x, y0 + 155), testo_prezzo_vecchio, font_prezzo_vecchio, COLORE_PREZZO_VECCHIO)

    # Converti in RGB (JPEG non supporta trasparenza) e ritorna i byte
    canvas_finale = canvas.convert("RGB")
    buffer = io.BytesIO()
    canvas_finale.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()
# Alla fine del file, dopo la funzione componi_immagine_offerta
if __name__ == "__main__":
    # Test con un'immagine di esempio
    url_test = "https://m.media-amazon.com/images/I/81wr7L6ZC5L._SL1000_.jpg"
    risultato = componi_immagine_offerta(url_test, 19.99, 29.99, 33)
    if risultato:
        with open("test_badge.jpg", "wb") as f:
            f.write(risultato)
        print("✅ Immagine generata con successo!")
    else:
        print("❌ Errore nella generazione dell'immagine")
