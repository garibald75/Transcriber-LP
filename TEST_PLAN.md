# Transcriber-LP Test Plan

## Obiettivo
Aggiungere un livello minimo di test automatici per dimostrare qualità e stabilità quando il repository viene esaminato.

## Scope
- Validazione sintassi Python per tutti i moduli principali
- Import test di base per i componenti core e UI
- Verifica del manager dei modelli senza dipendenza da GUI
- Integrazione con GitHub Actions per esecuzione automatica su push/PR

## Success criteria
- Tutti i file Python nel progetto passano la compilazione `py_compile`
- I test automatici di importazione passano in un ambiente pulito
- Il workflow GitHub Actions è configurato e pronto per l'esecuzione

## Test automatici
### 1. Compilazione Python
- Eseguire `python -m py_compile $(find app -name '*.py')`
- Scopo: intercettare errori di sintassi prima che il codice venga esaminato

### 2. Import basic
- Eseguire `python -m unittest discover tests`
- Verifica che i moduli principali siano importabili
- Evita dipendenze complesse come il rendering UI in fase di test

## Test manuali consigliati
### UI
- Avviare l'applicazione locale con `python -m app.main`
- Verificare: drag & drop, selezione file, pulsanti Transcribe/Stop, menu Help

### Model manager
- Verificare la lista modelli e la risoluzione dei percorsi
- Verificare il comportamento con modelli mancanti

### Packaging macOS M1
- Eseguire lo script `scripts/build_macos.sh`
- Verificare che `dist/Transcriber-LP.app` si apri correttamente su M1

## GitHub
Questo progetto può usare GitHub Actions per eseguire i test automatici.
Una pipeline base comprende:
- checkout
- installazione Python
- installazione dipendenze (`pip install -r requirements.txt`)
- esecuzione `python -m py_compile`
- esecuzione `python -m unittest discover tests`

## Prossimi passi
1. Aggiungere altri test unitari per `app/core/model_manager.py`
2. Aggiungere test di integrazione per `app/core/transcriber.py` con mock `subprocess`
3. Estendere la pipeline con linting e controllo delle dipendenze
