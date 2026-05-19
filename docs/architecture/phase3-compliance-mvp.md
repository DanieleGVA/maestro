# Phase 3 — Compliance & Safety: MVP Minimum

> Versione ridotta all'osso per MVP (1 scuola, 1 classe, 1 docente, ~25 studenti minori).
> Ogni sezione indica cosa e' legalmente obbligatorio vs cosa si puo' rimandare a V1.

---

## T3.1 — DPIA + Consenso (MVP minimum)

### DPIA slim

Il GDPR Art. 35 richiede una DPIA quando il trattamento comporta rischio elevato per i diritti dei minori. Per MVP e' sufficiente un documento strutturato — non serve un tool enterprise.

**Sezioni obbligatorie della DPIA MVP:**

1. **Descrizione del trattamento**: cosa raccogliamo, per chi (minori 13-19), base giuridica (consenso genitoriale Art. 8), finalita' (apprendimento personalizzato)
2. **Necessita' e proporzionalita'**: perche' ogni dato e' necessario, non raccogliamo piu' del minimo
3. **Rischi per gli interessati**: profilazione di minori, lingua nativa come dato Art. 9, LLM esterno
4. **Misure di mitigazione**: pseudonimizzazione, EU residency, consenso granulare, right to erasure
5. **Parere DPO**: da ottenere prima del pilota (OQ11 — serve conferma da Daniele se DPO esterno o liaison)

**Rimandato a V1**: valutazione d'impatto formale con Garante Privacy, certificazione MIUR.

### 5 Consensi granulari — MVP implementation

I 5 consensi sono non negoziabili (CLAUDE.md). Per MVP il flusso e' **amministrato** (F14.4):

| Consenso | Tipo | Base giuridica | Se negato |
|---|---|---|---|
| (a) Profilazione adattamento | Opt-in | Art. 6(1)(a) + Art. 8 | Profilo uniforme, contenuti non personalizzati |
| (b) Lingua nativa | Opt-in | Art. 9(2)(a) esplicito | Nessun bilinguismo, contenuti solo in lingua ufficiale |
| (c) Comunicazioni famiglia | Opt-in | Art. 6(1)(a) | Nessun report mensile, famiglia non riceve comunicazioni |
| (d) Storico cross-anno | Opt-in | Art. 6(1)(a) + Art. 8 | Mappa azzerata a ogni anno scolastico |
| (e) Ricerca anonima | Opt-in | Art. 6(1)(a) | Dati non inclusi in aggregazioni anonime |

**Flusso MVP:**
1. Admin IT crea studente nel sistema (form manuale)
2. Il sistema genera un **modulo cartaceo PDF** con i 5 consensi, linguaggio chiaro per genitori, in italiano
3. Il docente distribuisce, raccoglie firmati, l'admin registra nel sistema il flag per ogni consenso
4. Lo studente riceve credenziali solo dopo che almeno i consensi obbligatori sono registrati

**Cosa serve implementare:**
- Endpoint `POST /admin/students/{id}/consents` che accetta un array di `{type: "a"|"b"|"c"|"d"|"e", granted: bool, granted_at: date}`
- Template PDF generabile con i 5 consensi (testo fisso, genera con dati studente)
- Tabella `core.consent` gia' nel DDL di HLD-004
- Gate applicativo: se consenso (a) = negato, il Profiler Agent ritorna profilo uniforme. Se (b) = negato, Bilingual Composer non si attiva.

**Rimandato a V1**: flusso self-service via link/QR + SPID, UI di gestione consensi per la famiglia.

### Right to erasure — MVP minimum

- Stored procedure atomica gia' progettata in HLD-004
- MVP: richiesta via admin IT (form), esecuzione entro 30 giorni
- Genera certificato di cancellazione PDF
- Audit log pseudonimizzato preservato

**Rimandato a V1**: richiesta self-service da famiglia/studente via UI.

---

## T3.2 — Safeguarding (MVP minimum)

### Cosa e' obbligatorio per MVP

Ogni output generato dal sistema passa per il Safeguarding Agent **prima** di arrivare allo studente (N3, strutturalmente garantito dall'orchestratore — ADR-003).

### Implementazione MVP: regole nel prompt, non ML pipeline

Per MVP, il safeguarding e' **embedded nel system prompt** di ogni agente generativo + un check post-generazione con regole deterministiche. Non serve un modello ML dedicato.

**System prompt safeguarding (iniettato in ogni call LLM):**

```
REGOLE INVIOLABILI — Il contenuto generato DEVE rispettare TUTTE queste regole:
1. MAI confrontare lo studente con altri studenti, direttamente o indirettamente.
2. MAI usare tono punitivo, sarcastico, o scoraggiante. Anche per insufficienza grave, il tono e' incoraggiante.
3. MAI usare linguaggio offensivo, discriminatorio, sessista, razzista, omofobo.
4. MAI usare sfondo rosso per risultati negativi. Usare arancione per "da migliorare".
5. MAI creare urgenza artificiale (FOMO, scarcity, countdown).
6. MAI sostituirsi a un professionista per disagio psicologico.
7. Ogni lacuna e' presentata come "una porta aperta" con la missione di recupero allegata.
8. I termini tecnici sono sempre spiegati, mai dati per scontati.
9. Le analogie sono diversificate e non stereotipate (no stereotipi nazionali, regionali, di genere).
```

**Check post-generazione (deterministico, in codice Python):**

```python
BLOCKED_PATTERNS = [
    r"(?i)(peggio|meglio) (di|degli altri|dei compagni|della classe)",
    r"(?i)(sei (scarso|incapace|lento|stupido))",
    r"(?i)(non (sei|sarai) (mai|capace))",
    r"(?i)(devi vergognarti|che figuraccia)",
    r"(?i)(tutti.*tranne te|solo tu)",
]

def safeguarding_check(content: str) -> tuple[bool, list[str]]:
    """Returns (passed, list_of_violations). Blocking check."""
    violations = []
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, content):
            violations.append(pattern)
    return len(violations) == 0, violations
```

**Se il check fallisce**: il contenuto viene rigenerato (max 2 retry). Al terzo fallimento, viene servito un contenuto fallback generico dal materiale del docente (non generato da LLM).

**Alert docente**: Se il sistema rileva keyword di disagio nell'input studente (es. "non ce la faccio", "voglio smettere", "mi fa stare male"), genera un alert in-app per il docente. MVP: pattern matching su keyword list, non analisi sentimentale.

```python
WELLBEING_KEYWORDS = [
    "non ce la faccio", "voglio smettere", "mi fa stare male",
    "mi sento solo", "nessuno mi capisce", "e' inutile",
    "tanto non cambiera' niente", "non servo a niente",
]
```

**Rimandato a V1**: ML classifier per tono/sentimento, pipeline di moderazione multi-step, escalation automatica a referente scolastico, rilevamento pattern temporali (regressione ripetuta, inattivita' prolungata, uso notturno).

---

## T3.3 — Accessibilita' (MVP minimum)

### WCAG 2.1 AA — checklist MVP

Non serve un design system completo. Serve una **checklist vincolante** + token di design base.

**Obbligatorio per MVP:**

| Criterio | Requisito | Come |
|---|---|---|
| 1.1.1 Non-text content | Alt text su tutte le immagini | `alt` attribute obbligatorio |
| 1.3.1 Info and relationships | Struttura semantica | HTML5 semantico (`<nav>`, `<main>`, `<article>`, `<section>`) |
| 1.4.3 Contrast minimum | Rapporto contrasto >= 4.5:1 (testo), >= 3:1 (testo grande) | Token colore con contrasto verificato |
| 1.4.11 Non-text contrast | Elementi UI >= 3:1 | Bordi, icone, focus ring |
| 2.1.1 Keyboard | Tutto raggiungibile da tastiera | `tabIndex`, focus management |
| 2.4.3 Focus order | Ordine logico di focus | DOM order = visual order |
| 2.4.7 Focus visible | Focus ring visibile | `outline` CSS, mai `outline: none` |
| 4.1.2 Name, role, value | ARIA su componenti custom | `aria-label`, `role`, `aria-expanded` |

**Token di design MVP (colori semaforo con contrasto verificato):**

| Stato | Colore sfondo | Colore testo | Contrasto | Hex |
|---|---|---|---|---|
| non_introdotto | Grigio chiaro | Nero | 12.6:1 | bg: #E0E0E0, fg: #1A1A1A |
| introdotto | Bianco | Nero | 21:1 | bg: #FFFFFF, fg: #1A1A1A |
| lacuna | Rosso attenuato | Bianco | 4.8:1 | bg: #D32F2F, fg: #FFFFFF |
| in_recupero | Arancione | Nero | 5.2:1 | bg: #F57C00, fg: #1A1A1A |
| da_consolidare | Giallo | Nero | 8.1:1 | bg: #FDD835, fg: #1A1A1A |
| consolidato | Verde | Bianco | 4.6:1 | bg: #388E3C, fg: #FFFFFF |

**Font MVP**: Inter (sans-serif, buona leggibilita'), dimensione base 16px, line-height 1.5.

**Rimandato a V1**: design system completo (Storybook), font dyslexia-friendly (OpenDyslexic come opzione), modalita' alto contrasto, test con utenti BES/DSA, screen reader test completo.

---

## T3.4 — Bilinguismo (MVP minimum)

### Scope MVP: 2 lingue (ucraino + arabo)

**Cosa serve:**

1. **Glossario tecnico controllato** per ucraino e arabo
   - ~200 termini IT di base (variabile, funzione, ciclo, array, oggetto, classe, sessione, query, etc.)
   - Formato: JSON `{term_it: string, term_uk: string, term_ar: string, context: string}`
   - Curato manualmente una tantum, revisionato da madrelingua prima del pilota
   - Usato dal Bilingual Composer come lookup constraint nei prompt

2. **Bilingual Composer prompt** (gia' specificato in HLD-003)
   - Genera in lingua ufficiale → adatta in lingua nativa (post-generation)
   - Vincolo: glossario tecnico iniettato nel prompt, termini tecnici devono usare la traduzione dal glossario
   - Layout output: JSON con campi `{official: string, native: string}` per ogni blocco

3. **Gate consenso (b)**: se negato, il Bilingual Composer non si attiva. Gia' nel flusso orchestratore.

**Cosa NON serve per MVP:**
- Revisore madrelingua in produzione (basta una revisione pre-pilota del glossario)
- SLA di qualita' traduzione
- Podcast cross-language (V1)
- Rilevamento lettura squilibrata F13.20 (V1)
- UI in ucraino/arabo N9 (V1 — MVP: UI solo italiano)

**Rimandato a V1**: espansione a 6 lingue, revisori madrelingua ricorrenti, N9 (UI multilingua), podcast bilingue, rilevamento F13.20.

---

## T3.5 — Security (MVP minimum)

### Autenticazione

**MVP: credenziali locali + Keycloak basic.**

- Admin IT crea utente con email + password temporanea
- Login via Keycloak (gia' in ADR-001): username/password per MVP, SSO (SAML/OIDC) configurabile per V1
- MFA obbligatorio solo per admin (TOTP via Keycloak)
- JWT con scadenza 1h, refresh token 24h
- 3 ruoli: `admin`, `teacher`, `student`

**Rimandato a V1**: SSO con registro elettronico, SPID, WebAuthn.

### Crittografia

- **At rest**: PII crittografati con pgcrypto (`pgp_sym_encrypt`/`pgp_sym_decrypt`). Campi: `name`, `email`, `school_registry_ref`. Gia' nel DDL di HLD-004.
- **In transit**: TLS 1.3 obbligatorio su tutti gli endpoint.
- **Chiave di crittografia**: variabile d'ambiente, mai in codice. Rotazione manuale per MVP.

**Rimandato a V1**: key management service (Vault), rotazione automatica, crittografia end-to-end dei materiali.

### Pseudonimizzazione LLM

Gia' specificata in HLD-001 (LLM Gateway):

```python
PSEUDONYMIZATION_RULES = {
    "student_name":    "Studente_{hash[:8]}",
    "teacher_name":    "Docente_{hash[:8]}",
    "school_name":     "Scuola_PILOT",
    "class_name":      "Classe_A",
    "email":           "[REDACTED]",
    "native_language": "[REDACTED]",  # Art. 9, MAI inviata al LLM
    "registry_id":     "[REDACTED]",
}
```

Session-scoped: la mappa pseudo → reale vive solo in memoria per la durata della richiesta. Mai persistita.

### Audit log

- Append-only, immutabile (trigger PostgreSQL in HLD-004)
- Ogni accesso a dati di un minore loggato
- Export CSV/JSON per admin
- Retention: 5 anni (allineamento conservativo con normativa scolastica italiana)

### Threat model — top 5 MVP

| # | Minaccia | Mitigazione MVP |
|---|---|---|
| 1 | PII leak verso LLM esterno | Pseudonimizzazione al boundary (LLM Gateway) |
| 2 | Accesso non autorizzato a dati studente | Keycloak RBAC, JWT, audit log |
| 3 | SQL injection | Parameterized queries (SQLAlchemy ORM), input validation |
| 4 | XSS su dashboard docente | Content Security Policy, output escaping (React default) |
| 5 | Accesso fisico al server | Hetzner full-disk encryption, SSH key-only, firewall |

**Rimandato a V1**: pen-test formale, WAF, IDS/IPS, threat model completo STRIDE, secrets manager (Vault).

---

## Riepilogo: cosa implementare per MVP

### Must-have (bloccanti per pilota)

| Area | Deliverable | Effort stimato |
|---|---|---|
| DPIA | Documento 5 sezioni in `.maestro/dpia/dpia-mvp.md` | 1 documento |
| Consenso | Endpoint API + template PDF + gate applicativi | ~2 giorni dev |
| Erasure | Stored procedure + certificato PDF | Gia' nel DDL |
| Safeguarding | System prompt rules + regex check + keyword alert | ~1 giorno dev |
| Accessibilita' | Checklist + token colore + font + semantic HTML | Integrato nello sviluppo UI |
| Bilinguismo | Glossario JSON 200 termini (uk + ar) + prompt Composer | ~3 giorni (1 dev + revisione) |
| Auth | Keycloak basic + 3 ruoli + JWT + MFA admin | ~2 giorni dev |
| Crittografia | pgcrypto su PII + TLS | ~1 giorno dev |
| Pseudonimizzazione | LLM Gateway rules | Gia' nell'architettura |
| Audit log | Trigger + export | Gia' nel DDL |

### Esplicitamente rimandato a V1

- DPIA formale con Garante Privacy
- Consenso self-service (SPID/QR)
- SSO con registro elettronico
- ML safeguarding classifier
- Design system completo (Storybook)
- Font dyslexia + test BES/DSA
- UI in ucraino/arabo (N9)
- Pen-test formale
- Key management (Vault)
- Espansione a 6 lingue
- Revisori madrelingua ricorrenti

---

## Checklist gate Phase 3 MVP

- [ ] DPIA slim presente in `.maestro/dpia/dpia-mvp.md`
- [ ] 5 consensi implementati (API + template PDF + gate)
- [ ] Right to erasure funzionante (stored procedure + certificato)
- [ ] Safeguarding rules nel system prompt + regex check post-generazione
- [ ] Wellbeing keyword alert implementato
- [ ] Token colore con contrasto verificato
- [ ] Semantic HTML + keyboard nav + ARIA su componenti custom
- [ ] Glossario tecnico bilingue (uk + ar) curato e revisionato
- [ ] Bilingual Composer funzionante con gate consenso (b)
- [ ] Keycloak configurato con 3 ruoli + MFA admin
- [ ] PII crittografati at rest (pgcrypto)
- [ ] TLS 1.3 su tutti gli endpoint
- [ ] Pseudonimizzazione LLM Gateway funzionante
- [ ] Audit log append-only + export
