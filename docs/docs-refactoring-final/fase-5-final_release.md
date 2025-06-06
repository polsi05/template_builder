
# Fase 5 – Versioning e Validazione Finale

Nella **Fase 5** si conclude il ciclo di rilascio:  
- **Tag della versione**  
- **Generazione del CHANGELOG**  
- **Canary Deploy** finale  
- **Validazioni:** integration test, latenza canary, copertura minima, qualità del codice  

Solo se **tutti** questi passaggi sono superati, la release è considerata pronta per produzione.

---

## 5.1. Tagging della Release

### 5.1.1. Definizione della Versione  
- Seguire il **versioning semantico**: `MAJOR.MINOR.PATCH`  
- L’ultima milestone completata (M10) corrisponde alla **v1.0.0** (ad esempio).  

### 5.1.2. CRT 5.1 (Change Request Template per Release)

| Campo                    | Descrizione                                                    |
|--------------------------|----------------------------------------------------------------|
| **Titolo**               | `M10 · Release v1.0.0`                                         |
| **Descrizione**          | Finalizzazione del rilascio: tag v1.0.0, generazione changelog, canary deploy finale |
| **Moduli impattati**     | Nessuno (solo script di rilascio e configurazioni CI/CD)       |
| **Effetti collaterali**  | Nessuno sul codice; potenziali bug in canary non ancora emersi  |
| **Piano di rollback**    | Rimuovere tag, cancellare immagine canary, riportare produzione alla versione precedente |

1. Verificare che **tutte** le milestone (M1–M9) siano completate e che non ci siano PR aperte su `main`.  
2. Assicurarsi che la **pipeline CI** su `main` sia verde (lint, test, integration, scan).  
3. Verificare la copertura (coverage) sia ≥ **baseline + 1 %**.  

---

## 5.2. Generazione del CHANGELOG

### 5.2.1. Strumenti  
- **git-cliff** per estrarre automaticamente le note di rilascio dai commit  
- File di configurazione: `.gitcliff.toml`  

Esempio di `.gitcliff.toml`:
```toml
[git]
    tag_pattern = '^v[0-9]+\.[0-9]+\.[0-9]+$'

[parsed]
    commit_url_format = "https://github.com/utente/progetto/commit/{{hash}}"
    issue_url_format = "https://github.com/utente/progetto/issues/{{id}}"
    ignore_merge_commits = true

[sections]
    [[sections.unreleased]]
    title = "Unreleased"
    kind = "unreleased"

    [[sections.standard]]
    title = "Changelog"
    kind = "header"
```

### 5.2.2. Comando per generare il Changelog

```bash
git checkout main
git pull origin main

# Tag sigillato: v1.0.0
git tag v1.0.0

# Genera il CHANGELOG.md basato sui commit tra l’ultimo tag e v1.0.0
git-cliff --config .gitcliff.toml --output CHANGELOG.md v1.0.0
```

> **Nota:**  
> - Il comando `git-cliff v1.0.0` genera note riportando le modifiche da `v0.x.x` a `v1.0.0`.  
> - Il file `CHANGELOG.md` andrà aggiunto al commit e pushato insieme al tag.

---

## 5.3. Canary Deploy Finale

La versione **canary** serve a validare il comportamento in un ambiente “shadow” prima di promuovere la release a produzione.

### 5.3.1. Script di Canary Deploy (`deploy_canary_final.sh`)

Posizionato in `scripts/deploy_canary_final.sh`:

```bash
#!/bin/bash
set -e

# 1. Verifica tag
if [[ -z "$GITHUB_SHA" ]]; then
  echo "ERROR: GITHUB_SHA non definito"
  exit 1
fi

# 2. Build Docker con tag canary
IMAGE_TAG="myrepo/project:canary-${GITHUB_SHA}"
docker build -t $IMAGE_TAG .

# 3. Push su registry
docker push $IMAGE_TAG

# 4. Deploy su staging con etichetta canary
kubectl set image deployment/project-deploy project=$IMAGE_TAG --namespace=staging

# 5. Attendi per stabilizzazione
sleep 30

# 6. Smoke tests
echo "## Smoke Test Canary ##"
HEALTH_URL="http://staging.example.com/health"
if curl -sf $HEALTH_URL; then
  echo "Health check OK"
else
  echo "Health check fallito"
  kubectl rollout undo deployment/project-deploy --namespace=staging
  exit 1
fi

# 7. Test di latenza (p95) con Telemetria
# Script Prometheus o chiamata custom
LATENCY=$(curl -s http://prometheus.example.com/api/v1/query?query=histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)))
echo "p95 latency: $LATENCY ms"
# Confronta con baseline (100 ms ad esempio)
BASELINE=100
if (( $(echo "$LATENCY > $BASELINE * 1.2" | bc -l) )); then
  echo "Latenza canary superiore a 120% del baseline"
  kubectl rollout undo deployment/project-deploy --namespace=staging
  exit 1
fi

echo "Canary Deploy OK"
```

> **Parametri**: l’URL Health e Prometheus vanno adattati all’ambiente.  
> Se il Canary fallisce, esegue rollback e manda notifica (da implementare con Slack webhook o simile).

---

## 5.4. Validazioni Finali

Prima di promuovere `v1.0.0` in produzione, eseguire:

1. **Integration Tests** _(già richiesti in M9)_  
   ```bash
   pytest tests/integration/ --maxfail=1 --disable-warnings -q
   ```
   - Devono essere **verdi**.  

2. **Coverage Check**  
   ```bash
   pytest --cov=template_builder --cov-report=term-missing
   ```
   - Percentuale totale (unit + integration) ≥ **baseline + 1 %**.  

3. **Quality Gate**  
   - Controllare che **bandit** non segnali vulnerabilità critiche (`severity >= HIGH`).  
   - Verificare che **ruff** e **mypy** non segnalino errori.  

4. **Latenza Canary**  
   - Il test di latenza nel `deploy_canary_final.sh` deve mostrare p95 ≤ 120% del baseline.  

5. **Documentazione**  
   - Verificare che `CHANGELOG.md` sia aggiornato e coerente con le commit note.  
   - Controllare che `README.md` contenga la nuova versione ed eventuali note d’installazione se cambiano dipendenze.

---

## 5.5. Promozione in Produzione

Se tutte le verifiche sono superate:

1. **Tag v1.0.0** e push (già eseguito).  
2. **Merge in branch `release`** (se usi Git Flow) oppure **promuovere il container canary** in produzione:  
   ```bash
   kubectl set image deployment/project-deploy project=myrepo/project:canary-${GITHUB_SHA} --namespace=production
   ```
3. **Verifica Health Check in produzione**:  
   ```bash
   curl -sf http://prod.example.com/health
   ```
4. **Aggiornamento Badge**  
   - Aggiornare `README.md` con badge di test, coverage, qualità del container (canary).  
   - Se usi GitHub Actions, il badge si aggiorna automaticamente.

5. **Notifica al Team**  
   - Pubblicazione automatico di un messaggio su Slack/Teams:  
     > “v1.0.0 rilasciata in produzione con p95 latency X ms, coverage Y %, no vulnerabilità critiche.”

---

## 5.6. Piano di Rollback in Produzione

In caso di regressioni critiche:

1. Eseguire:
   ```bash
   kubectl rollout undo deployment/project-deploy --namespace=production
   ```
2. Creare CRITICAL HOTFIX in branch `hotfix/v1.0.1`:  
   - Correggere il problema  
   - Generare tag `v1.0.1`  
   - Seguire nuovamente il flusso F5 per la release minore.  

---

**Fine Fase 5 – Versioning e Validazione Finale**
