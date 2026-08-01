# Offerte Universitarie — Bot automatico

Bot che trova offerte Amazon valide (verificate con lo storico prezzi Keepa) e le pubblica
automaticamente sul canale Telegram, seguendo i template decisi per il progetto.

## Come funziona

1. Ogni 2 ore, GitHub Actions fa girare `main.py`
2. Lo script interroga Keepa per le categorie configurate in `config.py`
3. Filtra solo le offerte con sconto reale sopra la soglia minima
4. Pubblica al massimo N offerte per esecuzione sul canale Telegram

## Setup — passo per passo

### 1. Crea il bot Telegram
1. Apri Telegram, cerca **@BotFather**
2. Manda `/newbot`, segui le istruzioni (nome e username del bot)
3. BotFather ti darà un **token** — salvalo, ti servirà dopo
4. Aggiungi il bot come **amministratore** del tuo canale (@offerteuniversitarie), con permesso di pubblicare messaggi

### 2. Crea l'account Keepa e prendi l'API key
1. Vai su [keepa.com](https://keepa.com), crea un account
2. Attiva l'abbonamento API (necessario per usare la Deals API)
3. Prendi la tua **API key** dalla dashboard

### 3. Trova i `node_id` delle categorie
I `node_id` sono i codici numerici che Amazon/Keepa usano per identificare le categorie
(es. "Informatica", "Cancelleria"). Vanno recuperati una volta sola:
- Puoi cercarli tramite la Keepa Category Search API, oppure
- Scrivimi quando arrivi a questo punto e ti aiuto a trovarli per le categorie scelte

Una volta trovati, inseriscili in `src/config.py` al posto di `None`.

### 4. Iscriviti ad Amazon Associati
1. Vai su [affiliazione.amazon.it](https://affiliazione.amazon.it)
2. Completa la registrazione (serve un canale/sito da collegare — il tuo canale Telegram)
3. Prendi il tuo **tag di affiliazione** (es. `offerteuni-21`)

### 5. Carica il progetto su GitHub
1. Crea un account GitHub (gratuito) se non ce l'hai già
2. Crea un nuovo repository (puoi tenerlo privato)
3. Carica tutti i file di questa cartella nel repository

### 6. Configura i "Secrets" su GitHub
Vai su: repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Aggiungi questi 4 secrets (uno alla volta):
- `KEEPA_API_KEY` → la chiave presa al punto 2
- `TELEGRAM_BOT_TOKEN` → il token preso al punto 1
- `TELEGRAM_CHANNEL_ID` → l'username del canale, es. `@offerteuniversitarie`
- `AMAZON_AFFILIATE_TAG` → il tag preso al punto 4

Questo è il modo sicuro per gestire le chiavi: non finiscono mai scritte nel codice.

### 7. Attiva il workflow
Il file `.github/workflows/pubblica_offerte.yml` è già pronto: appena i secrets sono impostati,
GitHub Actions inizierà a far girare lo script automaticamente ogni 2 ore.

Per testarlo subito senza aspettare: vai su repository → **Actions** → seleziona il workflow →
**Run workflow** (pulsante manuale).

## Modificare il comportamento

Tutto si regola da `src/config.py`, senza toccare il resto del codice:
- `SCONTO_MINIMO_PERCENTUALE`: sotto quale sconto un'offerta viene scartata
- `PREZZO_MINIMO` / `PREZZO_MASSIMO`: range di prezzo accettato
- `MAX_OFFERTE_PER_ESECUZIONE`: quante offerte pubblicare ogni volta
- `CATEGORIE`: aggiungi o rimuovi categorie qui

## Prossimi passi possibili

- Aggiungere altre categorie (stagionali, tipo riscaldamento in autunno)
- Aggiungere altri programmi di affiliazione oltre Amazon
- Un log persistente per evitare di ripubblicare lo stesso prodotto due volte di seguito
