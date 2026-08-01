"""
Script principale: trova le offerte su Amazon, le verifica con Keepa, le pubblica su Telegram.
"""

import keepa_client
import templates
import telegram_publisher
import config


def main():
    # Valida la configurazione
    if not config.valida_config():
        print("❌ Configurazione non valida. Correggi gli errori e riprova.")
        return
    
    # Trova le offerte
    offerte = keepa_client.trova_tutte_le_offerte()
    
    if not offerte:
        print("❌ Nessuna offerta valida trovata in questa esecuzione.")
        return
    
    print(f"✅ Trovate {len(offerte)} offerte valide. Preparo i messaggi...")
    
    # Costruisci i messaggi
    messaggi = templates.costruisci_messaggi_batch(offerte)
    
    # Pubblica su Telegram
    print("📤 Pubblico su Telegram...")
    telegram_publisher.pubblica_batch(messaggi)


if __name__ == "__main__":
    main()