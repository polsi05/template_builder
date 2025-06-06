
# Fase 4 – Controllo Automatico del Rispetto del Workflow

In questa fase ogni milestone deve passare attraverso una serie di controlli stringenti:  
- **CRT approvato**  
- **Verifica contratti/interfacce**  
- **Pre-commit (lint, type-check, security check)**  
- **CI (unit test, integration test, vulnerability scan)**  
- **AI-review (commenti automatici sui diff)**  
- **Canary Deploy (per milestone finali)**  

Nessuna milestone può avanzare alla successiva se uno di questi passaggi fallisce.

---

## 4.1. CRT (Change Request Template)

1. **Formato CRT**  
   - Titolo breve  
   - Descrizione dettagliata  
   - Elenco moduli/file impattati  
   - Potenziali effetti collaterali  
   - Piano di rollback  
2. **Validazione manuale**  
   - Ogni CRT va salvato in JIRA (o file system) come riferimento.  
   - Deve essere **approvato** almeno da un reviewer umano prima di procedere.  
3. **Azione AI**  
   - L’AI genera il CRT base partendo dal titolo fornito dall’utente.  
   - L’utente rivede e completa i dettagli.

---

## 4.2. Verifica Contratti/Interfacce (Contract Check)

1. **Estrazione contratti**  
   - Prima di ogni modifica, l’AI recupera dal *vector store* (estratto di `docs/contracts.md`) i contratti del modulo interessato: funzioni, classi, signature.  
2. **Confronto**  
   - Gli stub di test e il diff proposto non devono alterare le signature già stabilite (type hint, nomi parametri).  
   - Se il diff modifica un’interfaccia pubblica, l’AI segnala un allarme (“Breaking Change: cambia signature di …”).  
3. **Output**  
   - Se i contratti rimangono invariati → passo OK.  
   - Se vengono modificati, l’AI produce un report che descrive le modifiche e chiede all’utente conferma per aggiornare il contratto.

---

## 4.3. Pre‐Commit Check

Impostare **pre-commit** per bloccare in locale errori di linting, tipizzazione e sicurezza.

### 4.3.1. File di configurazione `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--fast, --line-length=88]
  - repo: https://github.com/pycqa/ruff
    rev: 0.0.300
    hooks:
      - id: ruff
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        args: [--strict]
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [--severity-level=LOW]
  - repo: https://github.com/asottile/pyupgrade
    rev: v3.3.0
    hooks:
      - id: pyupgrade
```

### 4.3.2. Comandi in locale

- **Installazione**:  
  ```bash
  pre-commit install
  ```
- **Esecuzione manuale**:  
  ```bash
  pre-commit run --all-files
  ```
- **Fallimento**  
  - Se `black`, `ruff`, `mypy` o `bandit` restituiscono errori, la commit non viene permessa.  
  - L’AI segnala quali righe non sono conformi e propone correzioni.

---

## 4.4. Continuous Integration (CI)

Ogni commit/pull request deve passare la pipeline CI, che comprende:

1. **Lint & Type‐check**  
   - `black --check .`  
   - `ruff .`  
   - `mypy --strict .`  

2. **Unit/Property Tests**  
   - `pytest tests/unit/ --maxfail=1 --disable-warnings -q`  

3. **Integration Tests**  
   - `pytest tests/integration/ --maxfail=1 --disable-warnings -q`  

4. **Security Scan**  
   - `osv-scanner --file=requirements.txt | tee osv-report.txt`  
   - Fail se trovate vulnerabilità con severità ≥ MEDIUM.  

5. **SBOM Generation**  
   - `cyclonedx-py --output sbom.cdx.json`  
   - Caricare come artefatto della build.

### 4.4.1. Esempio di `.github/workflows/ci.yml`

```yaml
name: CI Pipeline

on:
  pull_request:
    branches: [main]
  push:
    tags: [v*.*.*]

jobs:
  lint-type:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: python-version: '3.12'
      - run: pip install -e .[test]
      - run: black --check .
      - run: ruff .
      - run: mypy --strict .

  unit-tests:
    needs: lint-type
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: python-version: '3.12'
      - run: pip install -e .[test]
      - run: pytest tests/unit/ --maxfail=1 --disable-warnings -q

  integration-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: python-version: '3.12'
      - run: pip install -e .[test]
      - run: pytest tests/integration/ --maxfail=1 --disable-warnings -q

  security-scan:
    needs: integration-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install osv-scanner cyclonedx-bom
      - run: osv-scanner --file=requirements.txt --exit-code on-high
      - run: cyclonedx-py --output sbom.cdx.json
      - uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: sbom.cdx.json

  ai-review:
    needs: security-scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gpt-review-bot/action@v1
        with:
          model: "gpt-4o-mini"
          token: ${{ secrets.OPENAI_API_KEY }}
```

> **Nota:**  
> - Il job `ai-review` commenta automaticamente sui diff eventuali violazioni di stile, possibili regressioni o cambiamenti di interfaccia non autorizzati.  
> - Se uno qualunque di questi step fallisce, la pipeline si interrompe e il merge è bloccato.  

---

## 4.5. AI‐Review

1. **Action**: `gpt-review-bot/action@v1`  
   - Utilizza un modello specificato (`gpt-4o-mini` o `gpt-4-mini-high`).  
   - Riceve il `diff` del PR e i contratti estratti da `contracts.md`.  
2. **Controlli eseguiti**:  
   - Linter virtuale: verifica che non ci siano import circolari, funzioni non tipizzate, errori di formattazione.  
   - Regression check: analizza il diff e confronta l’output dei test valore‐correnti vs output previsti.  
   - Contract check: verifica che le signature delle funzioni pubbliche non siano mutate senza consenso.  
3. **Commenti generati**:  
   - Errori di stile suggeriti (es. “Black suggerisce 1 riga di indentazione in più”).  
   - Potenziali regressioni (es. “La funzione X ora non restituisce più Y”).  
   - Breaking change di interfaccia (es. “Hai cambiato la signature di foo() in bar(arg1,arg2) senza aggiornare i test”).  

> **Flusso**:  
> - PR aperta → `ai-review` action commenta su GitHub → sviluppatore interviene → repusha → `ai-review` verifica di nuovo.  
> - Solo quando tutti i commenti vengono “resolved” (da umano o dall’AI), il PR può passare.  

---

## 4.6. Canary Deploy

(Applicabile solo alle milestone finali, es. M9/M10)

### 4.6.1. Pipeline Canary

1. **Build Container**  
   - CI genera l’immagine Docker `project:canary-${{ github.sha }}`.  
2. **Deploy su ambiente di staging**  
   - Utilizza GitHub Actions per pubblicare su Kubernetes/cluster di staging (etichetta `canary`).  
3. **Smoke Test in Canary**  
   - Esegui test automatici di sanity:  
     - `curl http://canary.example.com/health` → 200 OK  
     - `curl http://canary.example.com/api/version` → contiene `v1.0.0-canary`  
4. **Monitoraggio Telemetria**  
   - OpenTelemetry traccia p95 latency su endpoint critici (`/build_preview`, `/export`).  
   - Se la latenza supera baseline + 20 % in 15 minuti, invia alert a Slack e rollback automatico.  

### 4.6.2. Script di Canary Deploy (`deploy_canary.sh`)

```bash
#!/bin/bash
set -e

# 1. Build Docker
docker build -t myrepo/project:canary-$GITHUB_SHA .

# 2. Push su registry
docker push myrepo/project:canary-$GITHUB_SHA

# 3. Applica manifest su staging
kubectl set image deployment/project-deploy project=myrepo/project:canary-$GITHUB_SHA --namespace=staging

# 4. Esegui smoke tests
sleep 30
if ! curl -sf http://canary.example.com/health; then
    echo "Smoke test fallito!"
    # Rolling back
    kubectl rollout undo deployment/project-deploy --namespace=staging
    exit 1
fi

echo "Canary OK"
```

> **Rollback automatico**:  
> - Il job di monitoraggio (ad es. un cron Kubernetes Job) esegue periodicamente uno script simile a quello sopra.  
> - Nel caso di errori, esegue `kubectl rollout undo` e notifica il team.

---

## 4.7. Sintesi del Flusso di Controllo

Per ciascuna **Milestone (M1…M10)**:

1. **Utente aprirà un PR** con la patch minima e lo stub di test.  
2. **Pre-commit**: `ruff`, `black`, `mypy`, `bandit` → blocco se errori.  
3. **CI**:  
   - Lint → Type‐check → Unit tests → Property tests → Integration tests → SBOM → Vulnerability scan.  
   - Se uno fallisce → PR “red” → nessun merge.  
4. **AI‐Review**:  
   - Commenta su eventuali problematiche.  
   - Sviluppatore corregge → repusha.  
   - Ripete finché commenti non risolti.  
5. **Canary Deploy** (solo milestone finali):  
   - Build → Push → Deploy → Smoke test → Monitoraggio telemetria.  
   - Fail → rollback e notifica.  

Solo quando tutti i controlli sono **✓ passati**, la Milestone viene marcata come completata e si procede alla successiva.

---

**Fine Fase 4 – Controllo Automatico del Workflow**
