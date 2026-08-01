"""
Genera l'immagine finale da pubblicare: foto del prodotto + badge sovrapposto.
Versione semplificata che usa solo Pillow (non matplotlib).
"""

import io
import requests
from PIL import Image, ImageDraw, ImageFont


def scarica_immagine(url):
    """Scarica l'immagine del prodotto."""
    try:
        risposta = requests.get(url, timeout=15)
        risposta.raise_for_status()
        return Image.open(io.BytesIO(risposta.content)).convert("RGBA")
    except Exception as e:
        print(f"   ❌ Errore scaricamento immagine: {e}")
        return None


def componi_immagine_offerta(url_immagine_prodotto, prezzo_attuale, prezzo_precedente, sconto_percentuale):
    """
    Scarica la foto del prodotto e ci sovrappone un badge con prezzo e sconto.
    """
    try:
        # Scarica l'immagine
        foto = scarica_immagine(url_immagine_prodotto)
        if not foto:
            return None

        # Dimensioni base
        dimensione = 1080
        canvas = Image.new("RGBA", (dimensione, dimensione), (255, 255, 255, 255))
        
        # Ridimensiona e centra la foto
        foto.thumbnail((int(dimensione * 0.92), int(dimensione * 0.92)))
        pos_x = (dimensione - foto.width) // 2
        pos_y = (dimensione - foto.height) // 2
        canvas.paste(foto, (pos_x, pos_y), foto)

        # Crea il badge in basso a destra
        draw = ImageDraw.Draw(canvas, "RGBA")
        
        # Testi
        testo_sconto = f"-{sconto_percentuale}%"
        testo_prezzo = f"{prezzo_attuale:.2f}€".replace(".", ",")
        testo_prezzo_vecchio = f"{prezzo_precedente:.2f}€".replace(".", ",")

        # Font (usa font di sistema o default)
        try:
            font_sconto = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
            font_prezzo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 68)
            font_prezzo_vecchio = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
        except:
            # Fallback a font di default
            font_sconto = ImageFont.load_default()
            font_prezzo = ImageFont.load_default()
            font_prezzo_vecchio = ImageFont.load_default()

        # Dimensioni badge
        margine = 30
        larghezza_badge = 380
        altezza_badge = 210
        x0 = dimensione - larghezza_badge - margine
        y0 = dimensione - altezza_badge - margine
        x1 = dimensione - margine
        y1 = dimensione - margine

        # Sfondo bianco semi-trasparente
        draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255, 230))
        
        # Testi
        padding = 25
        draw.text((x0 + padding, y0 + 10), testo_sconto, font=font_sconto, fill=(214, 39, 40))
        draw.text((x0 + padding, y0 + 65), testo_prezzo, font=font_prezzo, fill=(20, 20, 20))
        draw.text((x0 + padding, y0 + 150), testo_prezzo_vecchio, font=font_prezzo_vecchio, fill=(140, 140, 140))

        # Converti in RGB e salva
        canvas_finale = canvas.convert("RGB")
        buffer = io.BytesIO()
        canvas_finale.save(buffer, format="JPEG", quality=90)
        return buffer.getvalue()

    except Exception as e:
        print(f"   ❌ Errore generazione badge: {e}")
        return None
