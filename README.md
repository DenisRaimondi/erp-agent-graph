# erp-agent-graph

Un agente [LangGraph](https://langchain-ai.github.io/langgraph/) che legge la casella di posta
di un ERP e capisce, mail per mail, di cosa si tratta e di quale cliente si parla.

Il problema di partenza è concreto: in un gestionale gli ordini arrivano come email scritte da
persone, in linguaggio libero — "le solite guarnizioni", "la misura piccola", un allegato senza
codici. Qualcuno le legge e le ribatte a mano. Questo repository è il tentativo di automatizzare
la parte d'ingresso senza far inventare niente al modello.

## Cosa fa oggi

```
                 ┌───────────┐  nessun ordine   ┌─────┐
  mail  ────────▶│ classify  │─────────────────▶│ END │
                 └───────────┘                  └─────┘
                       │ new_order_request
                       ▼
              ┌──────────────────┐        ┌─────┐
              │ extract_customer │───────▶│ END │
              └──────────────────┘        └─────┘
```

**`classify`** — una chiamata al modello con output strutturato (Pydantic). Restituisce un
`Verdict`: la lista dei temi riconosciuti (`new_order_request`, `quote_request`, `ticket`,
`spam`, `general_info`), un punteggio di confidenza fra 0 e 1 e la motivazione in chiaro.
Una mail può avere più temi insieme, perché nella realtà li ha.

**`extract_customer`** — un sotto-agente con tre strumenti sul database clienti:
ricerca per email esatta, per dominio, per ragione sociale. Il prompt gli chiede di usare
il minor numero di strumenti possibile e gli dice esplicitamente che **assegnare il cliente
sbagliato è peggio che non assegnarlo**: se non è sicuro restituisce `None`.

**Il dispatcher sta fuori dal grafo.** È codice deterministico: ogni 60 secondi chiede a
Mailpit le mail non lette, ne scarica il corpo e invoca il grafo una volta per mail, usando
l'ID del messaggio come `thread_id`. Niente LLM, niente stato.

Lo stato di ogni run è persistito su **Postgres** con il checkpointer ufficiale di LangGraph,
quindi ogni mail ha la sua storia riprendibile.

**Cosa non fa:** non estrae le righe d'ordine, non chiede conferma a un umano e non scrive
nulla nelle tabelle ERP. Lo schema (6 tabelle) e i dati di esempio ci sono e sono applicati,
ma nessun ordine viene creato dal grafo. Il disegno completo del flusso, con le parti ancora
da costruire e il perché delle scelte, sta in [GRAFO.md](GRAFO.md).

## Qualche decisione, e il motivo

**Estrazione in sequenza, non in parallelo.** Il cliente si identifica prima delle righe
d'ordine anche se i due rami sembrano indipendenti: sapere *chi* scrive permette di mettere
il suo storico d'acquisto nel prompt di estrazione, ed è così che "le solite guarnizioni"
si risolvono da sole invece di finire sul tavolo di chi revisiona.

**Al modello non si fanno inventare gli identificativi.** Gli id dei clienti stanno a
database, non nella mail: uno strumento che chieda al modello un `customer_id` lo costringe
a indovinare. Gli strumenti partono sempre da quello che nella mail c'è davvero — indirizzo,
dominio, ragione sociale.

**Lo schema ERP è il sistema di verità.** Niente tabelle di appoggio con ordini provvisori:
o l'ordine è valido e si scrive, o non esiste.

**Output strutturato via `ToolStrategy`.** Il provider usato (DeepSeek) non supporta il
`response_format` nativo, quindi sia `classify` sia il sotto-agente passano da una chiamata
a strumento — `with_structured_output(method="function_calling")` nel primo caso,
`ToolStrategy` nel secondo.

**Il seed è incompleto di proposito.** Alcuni mittenti e alcuni codici articolo presenti
nelle mail non stanno in anagrafica, così il grafo incontra discrepanze vere invece di un
mondo perfetto.

## Stack

Python 3.13 · LangChain 1.4 · LangGraph 1.2 · DeepSeek · PostgreSQL 17 con
`langgraph-checkpoint-postgres` · Pydantic · httpx · [uv](https://docs.astral.sh/uv/) ·
[Mailpit](https://mailpit.axllent.org/) come finto server di posta ·
ruff, pyright e pytest eseguiti dal pre-commit.

## Come si prova

```bash
docker compose up -d                         # Mailpit (:8025) e Postgres (:5433)
docker compose exec -T postgres psql -U erp -d erp < db/schema.sql
docker compose exec -T postgres psql -U erp -d erp < db/seed.sql

uv sync
uv run erp-agent-graph                       # avvia il dispatcher
```

Serve un `.env` nella radice del progetto:

```dotenv
DEEPSEEK_API_KEY=...
MAILPIT_URL=http://localhost:8025            # opzionale, questo è il default
DATABASE_URL=postgresql://erp:erp@localhost:5433/erp   # opzionale, questo è il default
```

Le mail arrivate si guardano su <http://localhost:8025>.
