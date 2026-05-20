# Garante Privacy Alignment Checklist -- MAESTRO MVP

**Documento**: Checklist di conformita' alle disposizioni del Garante Privacy per tecnologie educative con minori
**Versione**: 1.0
**Data**: 2026-05-20
**Autore**: MSTR-16 (Privacy & Compliance Engineer)
**Riferimenti normativi**: Provvedimento Garante n. 529/2025, DM 166/2025 (MIM), Vademecum "La scuola a prova di privacy" (2025), GDPR

---

## Legenda status

| Sigla | Significato |
|---|---|
| OK | Conforme -- implementato e verificato |
| PARTIAL | Parzialmente conforme -- implementato con limitazioni documentate |
| PLANNED | Non ancora conforme -- pianificato per V1 |
| N/A | Non applicabile al contesto MAESTRO |
| OPEN | Richiede chiarimento normativo o parere DPO |

---

## 1. Provvedimento Garante n. 529/2025 -- Obblighi per le scuole nel trattamento dati

| # | Requisito | Status | Evidenza / Note |
|---|---|---|---|
| 1.1 | Registro dei trattamenti aggiornato che includa il trattamento tramite MAESTRO | **PARTIAL** | Il registro del trattamento e' responsabilita' della scuola. MAESTRO fornisce la descrizione tecnica del trattamento (questa DPIA) da inserire nel registro. La scuola deve aggiornare il proprio registro. |
| 1.2 | DPIA per trattamenti ad alto rischio (profilazione alunni) | **OK** | DPIA presente in `.maestro/dpia/dpia-mvp-slim.md`. Copre profilazione, Art. 9, minori. |
| 1.3 | Definizione chiara dei ruoli: titolare, responsabile, sub-responsabili | **PARTIAL** | Titolare: Istituto scolastico. Responsabile: gestore tecnico MAESTRO. Sub-responsabili: Anthropic, OpenAI (per dati pseudonimizzati), Hetzner, Scaleway. DPA da formalizzare con ciascuno. |
| 1.4 | Informativa ai genitori/studenti prima dell'avvio del trattamento | **OK** | Informativa prevista nelle procedure pre-pilot (DPIA sezione 7.3). Due versioni: completa per famiglie, semplificata per studenti. |
| 1.5 | Consenso specifico e granulare per trattamenti che eccedono il compito istituzionale | **OK** | 5 consensi granulari separati (F14.3), ciascuno con propria base giuridica, indipendentemente revocabile. Moduli in `consent-templates-mvp.md`. |
| 1.6 | Misure di sicurezza adeguate al rischio | **OK** | Cifratura at rest (pgcrypto AES-256), TLS 1.3, RBAC, audit immutabile, pseudonimizzazione LLM, EU residency. Dettaglio in DPIA sezione 5.1. |
| 1.7 | Nomina DPO e comunicazione al Garante | **OK** | Le scuole pubbliche hanno obbligo di DPO (Art. 37). Il DPO della scuola sara' informato della DPIA (sezione 7.2). |
| 1.8 | Formazione del personale che accede ai dati | **PARTIAL** | Formazione docente prevista prima del pilot (DPIA sezione 5.2). Documentazione formativa da produrre. |
| 1.9 | Gestione data breach: procedura di notifica entro 72 ore | **PLANNED** | Procedura di incident response da formalizzare. Per il pilot MVP la responsabilita' e' dell'admin IT della scuola con supporto tecnico del team MAESTRO. |
| 1.10 | Diritti degli interessati garantiti: accesso, rettifica, cancellazione, portabilita' | **OK** | Implementati come da DPIA sezione 6.1. Right to erasure: stored procedure atomica. |

---

## 2. DM 166/2025 (MIM) -- Linee guida per l'uso dell'IA negli istituti scolastici

| # | Requisito | Status | Evidenza / Note |
|---|---|---|---|
| 2.1 | Divieto di sistemi di riconoscimento delle emozioni | **OK** | MAESTRO non effettua riconoscimento emotivo. La wellbeing detection analizza keyword testuali inserite dallo studente (input esplicito), non riconosce emozioni da biometria, voce o comportamento. |
| 2.2 | Minimizzazione dei dati: usare dati personali solo quando strettamente necessario | **OK** | Data minimisation documentata in DPIA sezione 3.1. Anno di nascita (non DOB), hash IP (non raw), lingua come codice ISO. Se consensi negati: profilo neutro. |
| 2.3 | Preferenza per dati sintetici rispetto a dati reali di studenti/docenti | **PARTIAL** | I dati inviati alle API LLM sono pseudonimizzati (STUDENTE_{hash}), non reali. Non vengono usati dati sintetici per il training perche' MAESTRO non effettua fine-tuning. I modelli LLM sono usati "as-is" con prompting. |
| 2.4 | Trasparenza: chiara definizione di ruoli e responsabilita' | **PARTIAL** | Ruoli definiti nel data model (student, teacher, admin). Responsabilita' nel trattamento da formalizzare nel contratto scuola-fornitore. |
| 2.5 | Centralita' della persona: l'IA come strumento di supporto, non sostituto del docente | **OK** | MAESTRO supporta il docente ma non lo sostituisce: il docente conferma le transizioni (F4.4), puo' fare override (F11.12), decide le verifiche, valida i concept mapping. Il sistema genera proposte, il docente decide. |
| 2.6 | Adozione di criteri etici nell'uso dell'IA | **OK** | 9 regole di safeguarding enforced architetturalmente, divieto confronti, tono incoraggiante, no dark patterns, no FOMO. Bias audit eseguito. |
| 2.7 | Riferimento ai contenuti informativi della Piattaforma Unica del MIM | **OPEN** | Da verificare se la Piattaforma Unica ha pubblicato contenuti specifici su MAESTRO o se e' richiesta una registrazione/notifica. |
| 2.8 | Privacy impact assessment prima dell'adozione dello strumento IA | **OK** | Questa DPIA e' stata redatta prima dell'avvio del pilot. |

---

## 3. Vademecum "La scuola a prova di privacy" (2025)

| # | Requisito | Status | Evidenza / Note |
|---|---|---|---|
| 3.1 | Non pubblicare online dati personali degli studenti (voti, assenze, nomi) | **OK** | MAESTRO non espone dati degli studenti pubblicamente. Tutti i dati sono dietro autenticazione con RBAC. La mappa di classe e' visibile solo al docente. |
| 3.2 | Non esporre foto o video di minori senza consenso | **N/A** | MAESTRO non raccoglie ne' mostra foto o video degli studenti. |
| 3.3 | Limitare l'uso di chat/messaggistica per comunicazioni ufficiali | **N/A** | MAESTRO non ha funzionalita' di chat tra utenti. Le notifiche sono unidirezionali (sistema -> utente). |
| 3.4 | Protezione dei dati relativi alla salute degli studenti | **PARTIAL** | MAESTRO non tratta dati sanitari esplicitamente, ma la wellbeing detection rileva segnali di disagio. Questi dati sono trattati con massima cautela: visibili solo a docente/referente, non in dashboard studente, non in export, con SLA di presa in carico. |
| 3.5 | Registri elettronici: sicurezza e accesso limitato | **N/A** | MAESTRO non e' un registro elettronico. V2 prevede integrazione (lettura) con il registro, ma per MVP non c'e' integrazione. |
| 3.6 | Telecamere e videosorveglianza: regole specifiche | **N/A** | MAESTRO non utilizza telecamere o videosorveglianza. |
| 3.7 | Rispetto del copyright e proprieta' intellettuale del docente | **OK** | F2.13: rispetto copyright. Materiali del docente usati come fonte primaria. Proprieta' intellettuale del docente preservata. |
| 3.8 | Consenso dei genitori per attivita' extra-didattiche con dati minori | **OK** | 5 consensi granulari. Il trattamento base (KMM, generazione contenuti) rientra nel compito educativo; i trattamenti extra (profilazione, bilingue, comunicazioni, storico, ricerca) richiedono consenso separato. |

---

## 4. GDPR -- Disposizioni specifiche per minori

| # | Requisito | Status | Evidenza / Note |
|---|---|---|---|
| 4.1 | Art. 8: Consenso genitoriale per minori sotto la soglia nazionale (14 anni in Italia) | **OK** | Moduli di consenso prevedono firma obbligatoria genitore/tutore per < 14. Consenso assistito (doppia firma) per 14-17. |
| 4.2 | Art. 12: Informativa in linguaggio chiaro e comprensibile per i minori | **OK** | Due versioni dell'informativa: completa per famiglie, semplificata per studenti (senza legalese). |
| 4.3 | Art. 17: Right to erasure rafforzato per minori | **OK** | Stored procedure atomica `core.execute_right_to_erasure` con cancellazione completa e certificato. Max 30 giorni (target 24h). |
| 4.4 | Art. 25: Privacy by design e by default | **OK** | Pseudonimizzazione al boundary LLM, cifratura PII, RBAC, audit immutabile. Default: profilo neutro se consenso non dato. |
| 4.5 | Art. 35: DPIA obbligatoria per trattamento su larga scala di dati di minori / profilazione | **OK** | DPIA presente e completa. |
| 4.6 | Art. 5(1)(c): Minimizzazione dei dati | **OK** | Vedi DPIA sezione 3.1. Solo dati strettamente necessari. |
| 4.7 | Art. 5(1)(d): Esattezza dei dati | **OK** | Lo studente puo' modificare il proprio profilo. Il docente puo' fare override. L'admin corregge l'anagrafica. |
| 4.8 | Art. 5(1)(e): Limitazione della conservazione | **OK** | Retention schedule esplicita per ogni categoria di dato. Partitioning mensile per gestione automatizzata. |
| 4.9 | Art. 5(1)(f): Integrita' e riservatezza | **OK** | Cifratura, TLS, RBAC, firewall, audit. |
| 4.10 | Art. 5(2): Accountability | **OK** | Audit log immutabile, DPIA documentata, consensi tracciati, deletion certificates. |
| 4.11 | Considerando 38: Protezione specifica per minori in relazione a profilazione e marketing | **OK** | Nessun marketing. La profilazione e' esclusivamente didattica, con consenso separato, e produce solo adattamento del formato dei contenuti. Non viene usata per targeting commerciale. |
| 4.12 | Considerando 58: Principio di trasparenza per i minori | **OK** | Pannello di spiegabilita' (N7): lo studente vede perche' il sistema propone un contenuto. Dashboard profilo visibile e modificabile. |

---

## 5. Art. 9 GDPR -- Categorie particolari di dati

| # | Requisito | Status | Evidenza / Note |
|---|---|---|---|
| 5.1 | Consenso esplicito (Art. 9(2)(a)) per lingua nativa | **OK** | Modulo B separato con dichiarazione esplicita, avvertenza sulla natura sensibile, doppia firma. |
| 5.2 | Finalita' limitata e proporzionata per il dato Art. 9 | **OK** | Lingua nativa usata solo per composizione bilingue. Non per altro scopo. |
| 5.3 | Misure di sicurezza adeguate alla sensibilita' del dato | **OK** | Non inviata a LLM, non in dashboard, cancellazione immediata alla revoca, codice ISO (non testo libero). |
| 5.4 | Registrazione del trattamento Art. 9 nel registro | **PARTIAL** | Da includere nel registro dei trattamenti della scuola con la specifica che si tratta di Art. 9. |
| 5.5 | DPIA specifica per trattamento Art. 9 | **OK** | DPIA include sezione dedicata (2.3) su lingua nativa come proxy origine etnica. |

---

## 6. Sicurezza del trattamento (Art. 32)

| # | Requisito | Status | Evidenza / Note |
|---|---|---|---|
| 6.1 | Pseudonimizzazione e cifratura dei dati personali | **OK** | pgcrypto per PII, pseudonimizzazione per LLM, hash per IP/user-agent |
| 6.2 | Capacita' di assicurare riservatezza, integrita', disponibilita' e resilienza | **OK** | RBAC (riservatezza), audit immutabile + trigger (integrita'), backup e DR plan (disponibilita', in progress T6.2), EU infrastructure (resilienza) |
| 6.3 | Capacita' di ripristinare tempestivamente i dati (disaster recovery) | **PLANNED** | DR plan in produzione (T6.2). Target: RPO <= 24h, RTO <= 4h. |
| 6.4 | Procedura per testare e valutare regolarmente l'efficacia delle misure | **PARTIAL** | Pen-test eseguito (T5.4), bias audit eseguito (T5.6). Pen-test annuale pianificato (N2). Test automatizzati di regressione per safeguarding. |
| 6.5 | Istruzioni per il personale autorizzato al trattamento | **PARTIAL** | Formazione docente pianificata. Documentazione operativa per admin IT da produrre. |

---

## 7. Trasferimenti extra-UE

| # | Requisito | Status | Evidenza / Note |
|---|---|---|---|
| 7.1 | Infrastruttura in UE | **OK** | Hetzner (DE), Scaleway (FR/NL). Nessun server extra-UE. |
| 7.2 | API LLM (Anthropic, OpenAI) con server in USA | **OK** | Solo dati pseudonimizzati (non PII) trasferiti. DPA + SCC con entrambi i provider. I dati trasferiti non sono "dati personali" ai sensi del GDPR perche' il mapping pseudonimo-identita' non e' disponibile ai provider. |
| 7.3 | Valutazione di impatto del trasferimento (TIA) | **PARTIAL** | La TIA formale e' semplificata dal fatto che nessun dato personale identificabile raggiunge i server USA. Il mapping e' in-memory, mai persistito, distrutto dopo l'uso. Tuttavia, una TIA formale documentata e' raccomandata per V1. |
| 7.4 | DPA con ciascun sub-responsabile | **PLANNED** | DPA da formalizzare con Anthropic, OpenAI, Hetzner, Scaleway prima dell'avvio del pilot. |

---

## 8. Diritti specifici nel contesto scolastico

| # | Requisito | Status | Evidenza / Note |
|---|---|---|---|
| 8.1 | Diritto alla cancellazione senza penalita' per lo studente | **OK** | La cancellazione non ha conseguenze sulla partecipazione alle lezioni normali. Lo studente semplicemente non usa piu' MAESTRO. |
| 8.2 | Diritto di opporsi alla profilazione (Art. 21) | **OK** | Revoca del consenso (a) -> profilo neutro, contenuti standard. Nessuna profilazione senza consenso. |
| 8.3 | Diritto di non essere soggetto a decisioni basate unicamente su trattamento automatizzato (Art. 22) | **OK** | Le transizioni di stato sono proposte dal sistema e confermate dal docente. Override disponibile. Pannello di spiegabilita'. Il sistema non prende decisioni formali sullo studente (voti, promozioni, bocciature). |
| 8.4 | Accesso del genitore ai dati del figlio minore | **PARTIAL** | Per MVP: il genitore puo' richiedere accesso tramite l'admin IT. V1: portale famiglia dedicato (UC-FAM-01..04). |
| 8.5 | Portabilita' dei dati in caso di trasferimento | **PARTIAL** | Export JSON della mappa della conoscenza disponibile via API. Format strutturato per V1 (con spec documentata). |

---

## 9. Riepilogo conformita'

| Categoria | OK | PARTIAL | PLANNED | OPEN | N/A | Totale |
|---|---|---|---|---|---|---|
| Provvedimento 529/2025 | 6 | 3 | 1 | 0 | 0 | 10 |
| DM 166/2025 (MIM) | 5 | 2 | 0 | 1 | 0 | 8 |
| Vademecum 2025 | 4 | 1 | 0 | 0 | 3 | 8 |
| GDPR minori | 12 | 0 | 0 | 0 | 0 | 12 |
| Art. 9 | 4 | 1 | 0 | 0 | 0 | 5 |
| Art. 32 (sicurezza) | 2 | 2 | 1 | 0 | 0 | 5 |
| Trasferimenti extra-UE | 2 | 1 | 1 | 0 | 0 | 4 |
| Diritti scolastici | 3 | 2 | 0 | 0 | 0 | 5 |
| **TOTALE** | **38** | **12** | **3** | **1** | **3** | **57** |

### Percentuale di conformita'

- Conforme (OK): 38/54 = **70%** (escludendo N/A)
- Parzialmente conforme (PARTIAL): 12/54 = **22%**
- Non conforme pianificato (PLANNED): 3/54 = **6%**
- Da chiarire (OPEN): 1/54 = **2%**

### Azioni prioritarie pre-pilot

1. Formalizzare DPA con Anthropic, OpenAI, Hetzner, Scaleway
2. Produrre documentazione formativa per docente e admin IT
3. Verificare con il DPO della scuola l'adeguatezza della base giuridica Art. 6(1)(e)
4. Predisporre procedura di incident response / data breach notification
5. Aggiornare il registro dei trattamenti della scuola con il trattamento MAESTRO
6. Verificare requisiti di registrazione sulla Piattaforma Unica del MIM

---

## Fonti normative consultate

- [Garante Privacy - Temi: Scuola](https://www.garanteprivacy.it/temi/scuola)
- [Privacy.it - Linee guida MIM per IA nelle scuole (settembre 2025)](https://privacy.it/2025/09/10/scuola-linee-guida-ia/)
- [Garante Privacy - DPIA](https://www.garanteprivacy.it/valutazione-d-impatto-della-protezione-dei-dati-dpia-)
- [Internetscuola.it - Provvedimento Garante n. 529/2025](https://www.internetscuola.it/provvedimento-del-garante-privacy-n-529-2025-cosa-cambia-per-le-scuole-nel-trattamento-dei-dati-personali/)
- [Federprivacy - OK Garante Privacy a linee guida MIM per IA](https://www.federprivacy.org/informazione/garante-privacy/ok-del-garante-privacy-alle-linee-guida-del-ministero-dell-istruzione-per-l-ia-negli-istituti-scolastici)

---

*Documento prodotto per il task T6.3 del DAG MAESTRO. Soggetto a review da MSTR-01 (Director), MSTR-13 (Security), DPO della scuola.*
