Ecco il **workflow v5** completamente rielaborato con:

* **Nomi di moduli generici**, senza riferimenti a file `.py` specifici che possano creare confusione.
* Esplicita menzione della **documentazione di supporto** (tutti i file `.md`) come fonte primaria di istruzioni e contratti.
* Le **regole trasversali** sui delimitatori, file lunghi e self-monitoring, integrate in ogni fase.

---

# Regole Trasversali (valide in tutte le fasi con codice)

1. **Delimitatori di codice**
   Ogni frammento di codice **DEVE** essere incapsulato così, senza alcun commento interno:

   ```
   --- INIZIO FILE: <percorso/nome_file> (PARTE n se serve) ---
   <SOLO codice, zero commenti esplicativi>
   --- FINE FILE:  <percorso/nome_file> (PARTE n se serve) ---
   ```

   Tutto ciò che **non** è codice (spiegazioni, dialoghi, note) **sta sempre fuori** dai delimitatori.

2. **Gestione file lunghi**
   Se un singolo file supera il limite di token o righe, spezzalo in parti contigue:

   * Alla fine della parte N:

     ```
     --- FINE FILE: <percorso/nome_file> (PARTE N) ---
     ```
   * Nel messaggio successivo:

     ```
     --- INIZIO FILE: <percorso/nome_file> (PARTE N+1) ---
     ```

   **Non** saltare né riordinare righe.

3. **Self-Monitoring silenzioso**
   Prima di ogni invio di codice, l’IA verifica:

   ```
   ### CONTROLLO DI CONFORMITÀ ###
   1. Delimitatori presenti e corretti?   [SÌ/NO]
   2. Suddivisione corretta (se spezzato)?[SÌ/NO]
   3. Codice completo, nessuna omissione? [SÌ/NO]
   4. Lingua italiana (per testo)?        [SÌ/NO]
   ###################################
   ```

---

# Glossario

* **Moduli generici**: “modulo di caricamento”, “modulo di binding dei passi”, “modulo di formattazione”, “motore di anteprima”, ecc.
* **Documentazione di supporto**: tutti i file `.md` forniti (`task.md`, `milestones.md`, `checks.md`, `release.md`) come fonte di contratti, task, milestone, controlli e piano di rilascio.
* **Codici B0x**: errori specifici (B01–B06).
* **Auto-check file**: verifica costante di accessibilità ai documenti JSON/MD e `.md`.
* **Quality Gate CI/CD**: flake8, black, mypy, pytest, security scan, AI-review.
* **Canary Deploy**: staging con rollback automatico se latenza p95 > baseline+20%.

---

# Struttura del Workflow v4.1

1. **Fase –1**: Apertura e acquisizione documentazione di supporto
2. **Blocco 1 (Fase 0)**: Conferma e parsing dei file JSON/MD + lettura documentazione di supporto
3. **Blocco 2 (Fase 1)**: Analisi AST, grafo di dipendenze e mappatura dei moduli
4. **Blocco 3 (Fase 2)**: Traduzione in italiano + Q\&A per ogni modulo generico
5. **Blocco 4 (Fase 3)**: Validazione finale con TEMPLATE\_VERIFICA (solo sezione 6)
6. **Fase 4**: Refactoring del modulo di caricamento/pre-salvataggio
7. **Fase 5**: Refactoring del modulo di binding dei passi
8. **Fase 6**: Refactoring dei moduli di formattazione e storage
9. **Fase 7**: Refactoring del motore di anteprima
10. **Fase 8**: Test di integrazione end-to-end
11. **Fase 9**: GUI smoke layer (opzionale)
12. **Fase 10**: CI/CD + AI-review finale
13. **Fase 11**: Release v1.0.0

---

## Fase –1: Apertura e acquisizione documentazione di supporto

**Obiettivo**
Ricevere e salvare internamente i seguenti file, eseguendo auto-check e backup:

* `callmap_full.json`
* `contracts_full.json`
* `contracts_template_builder.json`
* `dep_graph_full.json`
* `dep_graph_template_builder.json`
* `task.md` (documentazione task)
* `milestones.md` (milestone)
* `checks.md` (controlli richiesti)
* `release.md` (piano di rilascio)

**Flusso**

1. L’IA chiede all’utente il contenuto integrale di ciascun file.
2. Per ogni file ricevuto:

   * Lo legge riga per riga e lo salva in cache interna.
   * Risponde:

     ```
     OK: ho letto e salvato <nome_file> (XX righe).
     ```
   * Se l’auto-check fallisce (file mancante o corrotto), ripristina da backup e segnala B04.
3. Una volta acquisiti tutti:

   ```
   OK: tutti i documenti di supporto acquisiti. Procedo al Blocco 1.
   ```

**Clausole anti-rottura**

```plaintext
IF manca ≥1 documento  
  THEN: “Errore: manca <nome_file>. Inviamelo.” e STOP.
ELSEIF file non valido JSON/MD  
  THEN: “Errore B01: <nome_file> non valido. Rispedisci.” e STOP.
ELSE  
  CONTINUA.
```

---

## Blocco 1 (Fase 0): Conferma e parsing JSON/MD + lettura documentazione

**Obiettivo**
Assicurarsi che i file JSON/MD siano integri, parsarli, e leggere TUTTA la documentazione di supporto (`.md`) per ricavare:

* Callmap e contratti
* Grafo di dipendenze
* Task e milestone
* Controlli e piano di rilascio

**Azione IA**

1. Auto-check di tutti i file; ripristino backup se necessario.
2. Parsing strutturato e memorizzazione in strutture dati.
3. Lettura integrale della documentazione `.md` per estrarre:

   * Elenco task da `task.md`
   * Milestone da `milestones.md`
   * Controlli da `checks.md`
   * Details di release da `release.md`
4. Generazione riepilogo per conferma:

   ```
   Ho analizzato:
   • Callmap e grafo di dipendenze  
   • Contratti globali e specifici  
   • Task: <elenco>  
   • Milestone: <elenco>  
   • Controlli richiesti: <elenco>  
   • Piano di rilascio: <sintesi>  

   Se corretto, rispondi “Sì, procedi”.
   ```

**Clausole anti-rottura**

```plaintext
IF utente non risponde “Sì, procedi”  
  THEN: chiarisci punti mancanti e STOP.
ELSE  
  CONTINUA.
```

---

## Blocco 2 (Fase 1): Analisi AST e grafo di dipendenze

**Obiettivo**
Partendo dai JSON e dalla callmap, ricostruire:

* Macro-roadmap modulare (task → milestone → moduli)
* Tabella “Modulo → Task/Milestone → Contratto → Dipendenze upstream/downstream → Effetti collaterali”
* Sotto-grafo per l’ambito specifico del template builder

**Azione IA**

1. Auto-check file iniziali.
2. Costruzione interno di:

   * Elenco moduli generici (es. modulo di caricamento, modulo di binding, modulo di formattazione, motore di anteprima).
   * Tabella con relazioni e impatti.
3. Presentazione macro-roadmap:

   ```
   • Blocco 4 “Caricamento/Pre-salvataggio”: modulo di caricamento  
     – Contratto: SaveResult  
     – Dipendenze upstream/downstream  
     – Effetti collaterali  

   • Blocco 5 “Binding Passi”: modulo di binding  
   …  

   • Controlli: flake8, black, mypy, pytest, security scan  

   Se ok, rispondi “Procedi con Blocco 3”.
   ```

**Clausole anti-rottura**

```plaintext
IF auto-check fallisce  
  THEN: ripristina backup e segnala B04.
ELSEIF utente non conferma  
  THEN: chiarisci e STOP.
ELSE  
  CONTINUA.
```

---

## Blocco 3 (Fase 2): Traduzione in italiano + Q\&A

**Obiettivo**
Per ciascun modulo generico individuato, tradurre ogni funzione/classe **in italiano**:

1. **Frase tecnica** (“Se… allora… altrimenti…”)
2. **Descrizione passo-per-passo** (5–8 punti) con esempi reali
3. **Dialoghi Q\&A**:

   * Scenario A: utente conferma
   * Scenario B: utente solleva discrepanza
4. **Iniezione** degli esempi obbligatori (`quick_save`, `export_html`) e sarà l’IA a recuperarli dalla documentazione di supporto

**Flusso IA**

1. Auto-check documentazione e AST.
2. Per ogni modulo:

   ```
   Modulo di caricamento:
   1. Frase tecnica: …
   2. Descrizione passo-per-passo:
      1. …
      …
   3. Dialoghi Q&A:
      AI: …  
      Utente: …  

   Modulo validato. Procedo al prossimo.
   ```

**Clausole anti-rottura**

```plaintext
IF omissione di funzioni/classi  
  THEN: “Errore B03: funzione mancante. Rigenero.” e ripeti.
ELSEIF “KO” senza nota  
  THEN: “Errore: indica il motivo.” e STOP.
ELSE  
  CONTINUA.
```

---

## Blocco 4 (Fase 3): Validazione con TEMPLATE\_VERIFICA

**Obiettivo**
Confrontare “Originale vs Generato” per tutti i frammenti approvati:

* Sezioni 1–5 già compilate dall’IA
* Sezione 6 compilata dall’utente

**Flusso IA**

1. Invio `TEMPLATE_VERIFICA` (sezioni 1–5).
2. Ricezione sezione 6 dall’utente.
3. Per ogni frammento:

   * Se OK → nulla
   * Se KO → rigenera quel frammento in delimitatori
   * Loop fino a tutti OK
4. Se OK:

   ```
   TEMPLATE_VERIFICA completato. Procedo alla Fase 4.
   ```

**Clausole anti-rottura**

```plaintext
IF manca sezione 6  
  THEN: “Errore: carica solo sezione 6.” e STOP.
ELSEIF frammenti KO  
  THEN: rigenera e ripeti.
ELSE  
  CONTINUA.
```

---

## Fase 4: Refactoring modulo di caricamento/pre-salvataggio

**Obiettivo**
Rifattorizza il “modulo di caricamento” (locale+cloud), definisce schema `SaveResult`, docstring, logger, test stub.

**Flusso IA**

1. Backup modulo vecchio.
2. Genera nuovo codice **nei delimitatori** (spezzato se lungo).
3. Test stub in directory test corrispondente.
4. Esegue controlli:

   ```bash
   black --check  
   ruff .  
   mypy --strict  
   pytest tests/...  
   ```
5. Se errori → “Errore <tipo>: <descrizione>” e STOP.
6. Aggiorna CRT e attende “OK M3”.
7. Output:

   ```
   Refactoring completato. Tutti i controlli ok.
   ```

---

## Fase 5: Refactoring modulo di binding dei passi

**Obiettivo**
Separare logica di binding (ordinamento e numerazione passi) dal layer UI, con test property-based.

**Flusso IA**

1. Backup.
2. Nuovo codice nei delimitatori.
3. Test property-based.
4. Controlli locali.
5. Aggiorna CRT e attende “OK M4”.
6. Output:

   ```
   Refactoring completato. Tutti i controlli ok.
   ```

---

## Fase 6: Refactoring moduli di formattazione e storage

**Obiettivo**
Rifattorizza i moduli di formattazione testo, utils, configurazione Jinja, storage avanzato.

**Flusso IA**

1. Backup.
2. Codice nei delimitatori per ciascun modulo generico.
3. Test property-based e test storage aggiuntivi.
4. Controlli locali.
5. Attende “OK M5”.
6. Output:

   ```
   Refactoring completato. Tutti i controlli ok.
   ```

---

## Fase 7: Refactoring motore di anteprima

**Obiettivo**
Separare configurazione Jinja e garantire rendering statico e preview, con test unitari e integrazione.

**Flusso IA**

1. Backup.
2. Codice nei delimitatori (config e motore).
3. Test in directory dedicata.
4. Controlli locali.
5. Attende “OK M6”.
6. Output:

   ```
   Refactoring completato. Tutti i controlli ok.
   ```

---

## Fase 8: Test di integrazione end-to-end

**Obiettivo**
Verificare flusso completo Builder→Preview→Save.

**Flusso IA**

1. Crea test full-stack in delimitatori.
2. Controlli locali.
3. Se ok:

   ```
   Test integrazione completati con successo.
   ```

---

## Fase 9: GUI smoke layer (opzionale)

**Obiettivo**
Verificare che la GUI non crashi in ambiente headless.

**Flusso IA**

1. Crea test GUI in delimitatori.
2. Aggiunge dipendenze.
3. Esegue test con Xvfb.
4. Se ok:

   ```
   GUI smoke test completato con successo.
   ```

---

## Fase 10: CI/CD + AI-review

**Obiettivo**
Configurare pipeline CI/CD con Quality Gate e AI-review.

**Flusso IA**

1. Crea/aggiorna workflow YAML.
2. Inserisce badge in `README.md`.
3. Se tutti i job passano:

   ```
   CI/CD completato con successo.
   ```

---

## Fase 11: Release v1.0.0

**Obiettivo**
Tag semantico, `CHANGELOG.md`, Canary Deploy con monitoraggio p95 e rollback.

**Flusso IA**

1. Tag Git.
2. Genera changelog.
3. Canary Deploy + monitoraggio:

   * Se degrade → rollback e STOP
   * Se stabile → promuove in produzione
4. Aggiorna badge versione.
5. Notifica finale:

   ```
   Release v1.0.0 completata con successo!
   ```

---

Tutte le **regole trasversali** e le **clausole anti-rottura** restano attive in ogni fase. Nessun nome di file specifico rimane: l’IA lavorerà sempre su moduli generici identificati dinamicamente via AST e callmap, e utilizzerà la documentazione di supporto come guida principale.
