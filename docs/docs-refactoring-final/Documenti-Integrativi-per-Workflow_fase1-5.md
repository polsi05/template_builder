## Documenti Integrativi per Workflow v4.2

### 1. Simulazioni di traduzione Python → Linguaggio comune

Per ogni funzione, descrivi in modo chiaro e colloquiale cosa fa l’utente nella UI e come il codice risponde. Ecco alcuni scenari comuni che l’IA deve saper tradurre esattamente:

* **save\_html**: quando clicchi “Salva” dopo aver riempito tutti i segnaposto, la funzione controlla:

  * Se **tutti** i segnaposto sono popolati:

    * Procede a generare il file HTML pronto all’uso e segnala “Salvataggio completato”.
  * Se **uno o più** segnaposto sono vuoti:

    * Mostra un alert “Manca il valore per ‘{nome\_segnaposto}’ nello step {numero\_step}.”
    * Chiede “Vuoi procedere comunque?”

      * Se l’utente risponde **Sì**, salva con segnaposto vuoti e segnala “File salvato con avvisi.”
      * Se l’utente risponde **No**, interrompe il salvataggio e torna alla UI per completare i campi.

* **save\_file(path, data)**: quando esegui l’export in locale:

  * Tenta di scrivere il file nella cartella specificata.
  * Se il percorso non esiste, lo crea automaticamente.
  * Se non ha permessi di scrittura:

    * Mostra un messaggio “Permessi insufficienti: impossibile salvare in locale.”
    * Passa a salvare nel cloud (S3).
  * Alla fine, restituisce un riepilogo all’utente:

    * “File salvato in locale” oppure “File salvato nel cloud: s3://…”.

* **load\_file(path)**: quando apri un documento esistente:

  * Se il file **non esiste**:

    * Restituisce contenuto vuoto e mostra “File non trovato, creane uno nuovo.”
  * Se il file **esiste ma contiene JSON malformato**:

    * Mostra “Errore nel formato del file” e chiede “Vuoi ripristinare una copia di backup?”

      * Se **Sì**, ripristina copia precedente.
      * Se **No**, interrompe e permette di correggere manualmente.
  * Se il file è valido, carica i dati e li restituisce alla UI.

* **delete\_file(path)**: quando elimini un documento:

  * Se il file è presente in locale:

    * Lo cancella e conferma “File eliminato correttamente.”
  * Se non lo trova in locale:

    * Prova a rimuoverlo dal cloud.
    * Se nemmeno nel cloud esiste, segnala “Nessun file da eliminare.”

* **list\_files(dir\_path)**: quando chiedi di vedere tutti i documenti:

  * Tenta di leggere la directory in locale.
  * Se trova file, li elenca all’utente.
  * Se la directory è vuota:

    * Consulta il cloud e, se ci sono documenti, mostra “Non ci sono file locali, ne trovi {n} in cloud.”
    * Se anche il cloud è vuoto, mostra “Nessun file disponibile.”

* **export\_html(ctx, template\_path)**: quando esporti con un template Jinja:

  * Controlla se Jinja2 è installato:

    * Se mancante, mostra “Installa jinja2 con ‘pip install jinja2’.”
  * Se installato, carica il template e sostituisce i segnaposto `{{TITLE}}`, `{{CONTENT}}`, ecc.
  * Se il template ha errori di sintassi:

    * Solleva un errore catturato dall’UI: “Errore nel template: {descrizione}.”
  * Restituisce la stringa HTML renderizzata alla UI.

Questi scenari coprono i casi di utilizzo più frequenti e aiutano l’IA a tradurre qualsiasi funzione Python in un testo comune, passo‑per‑passo, con tutte le possibili varianti di flusso.

### 2. Template Q\&A Generico

```plaintext
**Scenario A – Utente conferma**
AI: "Ho spiegato la funzione `<nome_funzione>` con logica X, cosa Y e fallback Z. Ti è chiaro?"
Utente: "OK, perfetto."
AI: "Bene, passo al prossimo modulo."

**Scenario B – Utente osserva discrepanza**
AI: "Ho descritto `<nome_funzione>` come sopra. Ci sono dubbi?"
Utente: "KO: [breve motivo della discrepanza]."
AI: "Capito, modifico la parte: ‘…’. Fammi sapere se OK."
```

### 3. TEMPLATE\_VERIFICA (Full)

```plaintext
TEMPLATE_VERIFICA

1. Verifica import errati:      [ ] OK    [ ] KO — Nota: ____________
2. Verifica coerenza contratti: [ ] OK    [ ] KO — Nota: ____________
3. Verifica tassonomia:         [ ] OK    [ ] KO — Nota: ____________
4. Verifica fallback & doc:     [ ] OK    [ ] KO — Nota: ____________
5. Verifica dipendenze:
   Modulo A → Modulo B: [ ] OK [ ] KO — Nota: ______
   …
6. **Comparazione Originale vs Generato**
_____________________
# frammento originale
————————————————
<codice originale>
————————————————
# frammento generato
————————————————
<codice generato>
————————————————
_____________________
```

### 4. Pseudocodice Sanity‑check JSON vs Stubs AST

```python
# /scripts/sanity_check.py
import json, sys
from pathlib import Path
from stubs import ast_stubs  # contiene stub AST

def load_json(path):
    try:
        return json.load(open(path))
    except Exception as e:
        sys.exit(f"B01 JSON non valido: {path}")

def compare(json_obj, stubs):
    missing = [name for name in stubs if name not in json_obj]
    extra   = [name for name in json_obj if name not in stubs]
    if missing or extra:
        print(f"B02/B06 Incongruenze: missing={missing}, extra={extra}")
        sys.exit(1)
    print("Sanity-check OK")

if __name__ == '__main__':
    j1 = load_json('contracts_template_builder.json')
    s1 = ast_stubs.get_contracts()
    compare(j1.keys(), s1)

    j2 = load_json('dep_graph_template_builder.json')
    s2 = ast_stubs.get_modules()
    compare(j2.keys(), s2)
```

### 5. Snippet Generazione Lista Dinamica di File

```python
# /scripts/generate_refactor_list.py
import json

def load_dep_graph(path):
    return json.load(open(path))

dg = load_dep_graph('dep_graph_template_builder.json')

# consideriamo solo moduli con almeno un contratto
to_refactor = [mod for mod, info in dg.items() if info.get('contracts')]
print("Moduli da rifattorizzare:")
for m in to_refactor:
    print(f"- {m}.py")
```

---

Questi documenti integrativi forniscono esempi concreti e template operativi per automatizzare e consolidare il workflow v4.2.
