# Phase 3 — Compliance & Safety: MVP Minimum

> Versione ridotta all'osso per MVP (1 scuola, 1 classe, 1 docente, ~25 studenti minori).
> Solo safeguarding, accessibilita' e security sono in scope MVP. DPIA, consenso e bilinguismo rimandati a V1.

---

## Scope MVP vs V1

| Area | MVP | V1 |
|---|---|---|
| **DPIA** | -- | Documento 5 sezioni slim + DPIA formale Garante |
| **Consenso** | -- | API + template PDF + gate + self-service SPID/QR |
| **Right to erasure** | -- | Stored procedure atomica + certificato PDF |
| **Bilinguismo** | -- | Glossario 200 termini (uk+ar) + Composer prompt + espansione 6 lingue |
| **Safeguarding** | System prompt rules + regex check + keyword alert | ML classifier, escalation automatica |
| **Accessibilita'** | Checklist WCAG + token colore + semantic HTML | Design system completo, test BES/DSA |
| **Auth** | Keycloak basic + 3 ruoli + JWT + MFA admin | SSO registro elettronico, SPID |
| **Security** | pgcrypto PII + TLS + pseudonimizzazione + audit | Pen-test, Vault, WAF |

> **Decisione**: DPIA, consenso e bilinguismo sono rimandati interamente a V1 per ridurre lo scope MVP al minimo tecnico necessario per il pilota. Il pilota MVP opera senza profilazione personalizzata, senza bilinguismo e con consenso gestito fuori sistema (cartaceo). La tabella `core.consent` e la stored procedure di erasure restano nel DDL ma non vengono implementate a livello applicativo nel MVP.

---

## T3.1 — DPIA + Consenso (RIMANDATO A V1)

Tutto il contenuto di T3.1 e' rimandato a V1:
- DPIA slim (5 sezioni)
- 5 consensi granulari (API + template PDF + gate applicativi)
- Right to erasure (stored procedure + certificato PDF)

**Rationale**: per il pilota MVP con 1 classe e ~25 studenti, il consenso viene gestito fuori sistema (cartaceo scolastico standard). Il sistema non raccoglie PII oltre username/password gestiti da Keycloak. La profilazione adattiva (F3) e il bilinguismo non sono attivi, quindi i consensi (a) e (b) non si applicano. I consensi (c), (d), (e) non sono rilevanti senza le funzionalita' corrispondenti.

**Per V1**: implementare l'intero flusso come da spec originale (vedi git history per il dettaglio).

---

## T3.2 — Safeguarding (MVP)

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

## T3.3 — Accessibilita' (MVP)

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

## T3.4 — Bilinguismo (RIMANDATO A V1)

Tutto il contenuto di T3.4 e' rimandato a V1:
- Glossario tecnico controllato (200 termini, uk + ar)
- Bilingual Composer prompt
- Gate consenso (b)

**Rationale**: il pilota MVP opera solo in lingua italiana. Il bilinguismo richiede il consenso (b) per la lingua nativa (Art. 9) che e' anch'esso rimandato a V1.

**Per V1**: glossario 200 termini (uk + ar), Bilingual Composer con gate consenso, espansione a 6 lingue.

---

## T3.5 — Security (MVP)

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

Session-scoped: la mappa pseudo -> reale vive solo in memoria per la durata della richiesta. Mai persistita.

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

| Area | Deliverable |
|---|---|
| Safeguarding | System prompt rules + regex check + keyword alert |
| Accessibilita' | Checklist + token colore + font + semantic HTML |
| Auth | Keycloak basic + 3 ruoli + JWT + MFA admin |
| Crittografia | pgcrypto su PII + TLS |
| Pseudonimizzazione | LLM Gateway rules |
| Audit log | Trigger + export |

### Rimandato a V1 (era precedentemente in scope MVP)

- **DPIA**: documento 5 sezioni slim + DPIA formale Garante
- **Consenso**: 5 consensi granulari (API + template PDF + gate applicativi)
- **Right to erasure**: stored procedure + certificato PDF (DDL gia' presente)
- **Bilinguismo**: glossario 200 termini (uk + ar) + Bilingual Composer + espansione 6 lingue

### Esplicitamente rimandato a V1 (gia' fuori scope MVP)

- SSO con registro elettronico
- ML safeguarding classifier
- Design system completo (Storybook)
- Font dyslexia + test BES/DSA
- UI in ucraino/arabo (N9)
- Pen-test formale
- Key management (Vault)
- Revisori madrelingua ricorrenti

---

## Checklist gate Phase 3 MVP

- [ ] Safeguarding rules nel system prompt + regex check post-generazione
- [ ] Wellbeing keyword alert implementato
- [ ] Token colore con contrasto verificato
- [ ] Semantic HTML + keyboard nav + ARIA su componenti custom
- [ ] Keycloak configurato con 3 ruoli + MFA admin
- [ ] PII crittografati at rest (pgcrypto)
- [ ] TLS 1.3 su tutti gli endpoint
- [ ] Pseudonimizzazione LLM Gateway funzionante
- [ ] Audit log append-only + export
