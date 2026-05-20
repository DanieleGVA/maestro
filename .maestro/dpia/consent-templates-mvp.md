# Moduli di Consenso -- MAESTRO MVP Pilot

**Documento**: Moduli cartacei per i 5 consensi granulari (F14.3)
**Versione**: 1.0
**Data**: 2026-05-20
**Autore**: MSTR-16 (Privacy & Compliance Engineer)
**Lingua**: Italiano (adatto a minori 13-19 e alle loro famiglie)
**Riferimenti**: GDPR Art. 6, 8, 9; D.Lgs. 101/2018 Art. 2-quinquies; F14.3; CLAUDE.md

---

## Istruzioni per la compilazione

- Ogni modulo e' **indipendente**: la famiglia puo' acconsentire a uno, alcuni o tutti i trattamenti.
- Nessun consenso e' obbligatorio per partecipare alle lezioni. Lo studente che non acconsente ad alcun trattamento semplicemente non usa MAESTRO.
- Per studenti **sotto i 14 anni**: firma del genitore/tutore obbligatoria e sufficiente.
- Per studenti **dai 14 ai 17 anni**: firma dello studente + firma del genitore/tutore (consenso assistito).
- Per studenti **maggiorenni** (18-19 anni): firma dello studente sufficiente.
- Ogni consenso puo' essere **revocato in qualsiasi momento** senza conseguenze negative.

---

## Modulo A -- Consenso alla profilazione per adattamento dei contenuti

### Intestazione

```
ISTITUTO: ________________________________________________
CLASSE: ____________  ANNO SCOLASTICO: ____________________
DOCENTE: _________________________________________________
```

### Cosa chiediamo

Chiediamo il consenso per analizzare il modo in cui lo studente interagisce con il materiale didattico, al fine di capire quale formato di contenuto funziona meglio per lui/lei (ad esempio: testo scritto, esercizi pratici, lettura approfondita).

### Cosa raccogliamo

- Un **profilo di adattamento** composto da 5 punteggi numerici che indicano la preferenza per diversi formati di contenuto (visivo, audio, pratico, lettura, dialogo)
- Preferenze aggiuntive: tono preferito (confidenziale, neutro, formale) e lunghezza dei contenuti (sintesi o approfondimento)
- I dati del quiz iniziale di onboarding (5-10 minuti)

### A cosa serve

Il sistema usa queste informazioni per generare materiale di recupero nel formato piu' adatto allo studente. Ad esempio, uno studente che preferisce esercizi pratici ricevera' piu' esempi di codice funzionante, mentre uno che preferisce la lettura ricevera' spiegazioni piu' dettagliate.

### Cosa succede se non acconsento

Il sistema funziona comunque, ma con un profilo standard uguale per tutti. I contenuti non saranno personalizzati nel formato.

### Base giuridica

Art. 6(1)(a) GDPR -- consenso dell'interessato (o del titolare della responsabilita' genitoriale per minori sotto i 14 anni, ai sensi dell'Art. 2-quinquies D.Lgs. 101/2018).

### Dichiarazione di consenso

```
Io sottoscritto/a (genitore/tutore legale):

Cognome: ________________________  Nome: ________________________

Documento di identita': __________________  n. __________________

in qualita' di genitore/tutore legale dello/a studente:

Cognome: ________________________  Nome: ________________________

Classe: _________  Data di nascita: ____/____/________

Dichiaro di aver letto e compreso l'informativa privacy e le informazioni
sopra riportate relative al trattamento di profilazione per adattamento
dei contenuti.

[ ] ACCONSENTO al trattamento descritto nel presente modulo
[ ] NON ACCONSENTO al trattamento descritto nel presente modulo

Data: ____/____/________

Firma genitore/tutore: _____________________________________________

Firma studente (se >= 14 anni): ____________________________________
```

### Revoca del consenso

```
Il consenso puo' essere revocato in qualsiasi momento comunicando la
decisione all'admin IT della scuola (nome: ____________, email: ____________)
o al Dirigente Scolastico. La revoca non pregiudica la liceita' del
trattamento basato sul consenso prestato prima della revoca. Dopo la
revoca, il profilo dello studente sara' reimpostato ai valori standard.
```

---

## Modulo B -- Consenso al trattamento della lingua nativa (dato sensibile Art. 9 GDPR)

### Intestazione

```
ISTITUTO: ________________________________________________
CLASSE: ____________  ANNO SCOLASTICO: ____________________
DOCENTE: _________________________________________________
```

### Attenzione -- Dato sensibile

Questo modulo riguarda un **dato che il Regolamento Europeo considera sensibile** (Art. 9 GDPR). La lingua nativa puo' essere considerata un indicatore dell'origine etnica. Per questo motivo:
- Questo consenso e' **separato e indipendente** da tutti gli altri
- Richiede il **consenso esplicito** (non basta il silenzio o la mancata opposizione)
- Il dato e' protetto con garanzie aggiuntive rispetto agli altri dati

### Cosa chiediamo

Chiediamo il consenso per registrare nel sistema la lingua parlata in famiglia dallo studente (ad esempio: ucraino, arabo, cinese), al fine di offrire contenuti didattici bilingui.

### Cosa raccogliamo

- Solo il **codice della lingua** (es. "uk" per ucraino, "ar" per arabo). Non raccogliamo informazioni sull'origine, la nazionalita' o l'etnia dello studente.

### A cosa serve

Se lo studente parla una lingua diversa dall'italiano in famiglia, il sistema puo' generare il materiale di recupero in **due colonne**: italiano a sinistra, lingua nativa a destra. Questo aiuta a comprendere i concetti tecnici anche attraverso la lingua che lo studente padroneggia meglio.

### Garanzie aggiuntive

- La lingua nativa **non viene mai mostrata** ai compagni di classe o nelle classifiche/dashboard visibili ad altri studenti
- La lingua nativa **non viene mai inviata** ai servizi di intelligenza artificiale esterni utilizzati dal sistema
- La lingua nativa e' accessibile **solo al sistema** per generare il contenuto bilingue
- Alla revoca del consenso, il dato viene **cancellato immediatamente**

### Cosa succede se non acconsento

Il sistema funziona comunque, ma tutti i contenuti saranno solo in italiano. Lo studente non ricevera' il supporto bilingue.

### Base giuridica

Art. 9(2)(a) GDPR -- consenso esplicito dell'interessato al trattamento di categorie particolari di dati personali.

### Dichiarazione di consenso esplicito

```
Io sottoscritto/a (genitore/tutore legale):

Cognome: ________________________  Nome: ________________________

Documento di identita': __________________  n. __________________

in qualita' di genitore/tutore legale dello/a studente:

Cognome: ________________________  Nome: ________________________

Classe: _________  Data di nascita: ____/____/________

Dichiaro di aver letto e compreso l'informativa privacy e le informazioni
sopra riportate relative al trattamento della lingua nativa come dato
sensibile ai sensi dell'Art. 9 GDPR.

SONO CONSAPEVOLE che la lingua nativa e' considerata un dato sensibile
in quanto potenziale indicatore dell'origine etnica.

[ ] ACCONSENTO ESPLICITAMENTE al trattamento della lingua nativa
    come descritto nel presente modulo.

    Lingua nativa dello studente: ________________________________
    (scrivere la lingua parlata in famiglia, es. ucraino, arabo, ecc.)

[ ] NON ACCONSENTO al trattamento della lingua nativa.

Data: ____/____/________

Firma genitore/tutore: _____________________________________________

Firma studente (se >= 14 anni): ____________________________________
```

### Revoca del consenso

```
Il consenso puo' essere revocato in qualsiasi momento. Alla revoca, il
dato della lingua nativa sara' CANCELLATO IMMEDIATAMENTE dal sistema e
il supporto bilingue sara' disattivato. Comunicare la revoca all'admin IT
della scuola (nome: ____________, email: ____________) o al Dirigente
Scolastico.
```

---

## Modulo C -- Consenso alle comunicazioni periodiche alla famiglia

### Intestazione

```
ISTITUTO: ________________________________________________
CLASSE: ____________  ANNO SCOLASTICO: ____________________
DOCENTE: _________________________________________________
```

### Cosa chiediamo

Chiediamo il consenso per inviare alla famiglia comunicazioni periodiche sui progressi dello studente nel sistema MAESTRO.

### Cosa comunichiamo

- Un **report mensile** con un riepilogo dello stato della mappa della conoscenza dello studente (quanti concetti padroneggiati, quanti in recupero, quanti consolidati)
- **Alert specifici** se lo studente ha lacune non affrontate da piu' di 7 giorni
- **Conferme** relative al consenso e alla gestione dell'account

Le comunicazioni **non** contengono:
- Confronti con altri studenti
- Voti o giudizi numerici
- Informazioni su altri studenti della classe

### Canale di comunicazione

MVP: email all'indirizzo fornito dalla famiglia.

### Cosa succede se non acconsento

La famiglia non ricevera' i report periodici. Le comunicazioni obbligatorie per legge (es. conferma cancellazione dati) continueranno comunque.

### Base giuridica

Art. 6(1)(a) GDPR -- consenso dell'interessato.

### Dichiarazione di consenso

```
Io sottoscritto/a (genitore/tutore legale):

Cognome: ________________________  Nome: ________________________

Documento di identita': __________________  n. __________________

in qualita' di genitore/tutore legale dello/a studente:

Cognome: ________________________  Nome: ________________________

Classe: _________  Data di nascita: ____/____/________

Dichiaro di aver letto e compreso l'informativa privacy e le informazioni
sopra riportate relative alle comunicazioni periodiche alla famiglia.

[ ] ACCONSENTO alla ricezione delle comunicazioni periodiche
    sui progressi dello studente.

    Email per le comunicazioni: _____________________________________

[ ] NON ACCONSENTO alla ricezione delle comunicazioni periodiche.

Data: ____/____/________

Firma genitore/tutore: _____________________________________________

Firma studente (se >= 14 anni): ____________________________________
```

### Revoca del consenso

```
Il consenso puo' essere revocato in qualsiasi momento. Le comunicazioni
periodiche cesseranno entro 7 giorni lavorativi dalla revoca. Comunicare
la revoca all'admin IT della scuola (nome: ____________, email: ____________)
o al Dirigente Scolastico.
```

---

## Modulo D -- Consenso alla conservazione dello storico cross-anno

### Intestazione

```
ISTITUTO: ________________________________________________
CLASSE: ____________  ANNO SCOLASTICO: ____________________
DOCENTE: _________________________________________________
```

### Cosa chiediamo

Chiediamo il consenso per conservare i dati dello studente (mappa della conoscenza, cronologia delle transizioni, profilo di adattamento) oltre la fine dell'anno scolastico corrente, in modo che il prossimo anno il sistema possa ripartire dal punto in cui lo studente era arrivato.

### A cosa serve

Senza questo consenso, alla fine dell'anno scolastico tutti i dati dello studente vengono cancellati e l'anno successivo il sistema riparte da zero. Con questo consenso, lo studente ritrova la sua mappa della conoscenza e il suo percorso, con la continuita' del lavoro fatto.

### Cosa conserviamo

- Mappa della conoscenza (stato di padronanza per ogni concetto)
- Cronologia delle transizioni di stato
- Profilo di adattamento
- Contenuti generati

### Per quanto tempo

I dati vengono conservati per la durata dell'intero percorso scolastico dello studente nell'istituto (fino al diploma o al trasferimento), salvo revoca del consenso.

### Cosa succede se non acconsento

Alla fine di ogni anno scolastico, tutti i dati dello studente nel sistema MAESTRO vengono cancellati. L'anno successivo si riparte da zero.

### Base giuridica

Art. 6(1)(a) GDPR -- consenso dell'interessato.

### Dichiarazione di consenso

```
Io sottoscritto/a (genitore/tutore legale):

Cognome: ________________________  Nome: ________________________

Documento di identita': __________________  n. __________________

in qualita' di genitore/tutore legale dello/a studente:

Cognome: ________________________  Nome: ________________________

Classe: _________  Data di nascita: ____/____/________

Dichiaro di aver letto e compreso l'informativa privacy e le informazioni
sopra riportate relative alla conservazione dello storico cross-anno.

[ ] ACCONSENTO alla conservazione dei dati oltre la fine dell'anno
    scolastico corrente, per la durata del percorso scolastico
    dello studente.

[ ] NON ACCONSENTO alla conservazione cross-anno. I dati saranno
    cancellati alla fine dell'anno scolastico.

Data: ____/____/________

Firma genitore/tutore: _____________________________________________

Firma studente (se >= 14 anni): ____________________________________
```

### Revoca del consenso

```
Il consenso puo' essere revocato in qualsiasi momento. Alla revoca, i dati
dello studente degli anni scolastici precedenti saranno cancellati entro
30 giorni. I dati dell'anno in corso saranno mantenuti fino alla fine
dell'anno e poi cancellati. Comunicare la revoca all'admin IT della scuola
(nome: ____________, email: ____________) o al Dirigente Scolastico.
```

---

## Modulo E -- Consenso all'uso per ricerca aggregata anonimizzata

### Intestazione

```
ISTITUTO: ________________________________________________
CLASSE: ____________  ANNO SCOLASTICO: ____________________
DOCENTE: _________________________________________________
```

### Cosa chiediamo

Chiediamo il consenso per utilizzare i dati dello studente -- dopo averli resi completamente anonimi e non riconducibili a nessun individuo -- per analisi statistiche e ricerca educativa.

### Cosa significa "dati anonimi"

I dati vengono trasformati in modo che sia **impossibile** risalire allo studente:
- Il nome viene sostituito con un codice casuale non invertibile
- I dati vengono aggregati con quelli di molti altri studenti
- Nessun dato singolo viene pubblicato; solo statistiche di gruppo

Esempio di dato anonimo: "Il 40% degli studenti ha superato la lacuna su Sessioni PHP dopo il primo tentativo di recupero."

### A cosa serve

Queste statistiche aiutano a:
- Capire quali concetti sono piu' difficili per gli studenti
- Migliorare i contenuti generati dal sistema
- Valutare l'efficacia del sistema nel chiudere le lacune
- Contribuire alla ricerca sulla didattica dell'Informatica

### Cosa succede se non acconsento

Se la famiglia richiede la cancellazione dei dati dello studente (diritto all'oblio), tutti i dati -- compresi quelli che sarebbero stati anonimizzati -- vengono cancellati completamente. Se il consenso (e) era stato dato, i dati gia' anonimizzati prima della richiesta di cancellazione restano (essendo non identificabili).

### Cosa succede se acconsento ma poi cambio idea

I dati gia' anonimizzati non possono essere cancellati perche' non e' piu' possibile identificare a quali dati corrispondeva lo studente (sono irriconoscibili). I dati non ancora anonimizzati saranno esclusi dal processo.

### Base giuridica

Art. 6(1)(a) GDPR -- consenso dell'interessato. Nota: i dati una volta anonimizzati non sono piu' dati personali ai sensi del GDPR (Considerando 26).

### Dichiarazione di consenso

```
Io sottoscritto/a (genitore/tutore legale):

Cognome: ________________________  Nome: ________________________

Documento di identita': __________________  n. __________________

in qualita' di genitore/tutore legale dello/a studente:

Cognome: ________________________  Nome: ________________________

Classe: _________  Data di nascita: ____/____/________

Dichiaro di aver letto e compreso l'informativa privacy e le informazioni
sopra riportate relative all'uso dei dati anonimizzati per ricerca.

[ ] ACCONSENTO all'anonimizzazione e all'uso dei dati per ricerca
    aggregata come descritto nel presente modulo.

[ ] NON ACCONSENTO all'uso dei dati per ricerca aggregata.

Data: ____/____/________

Firma genitore/tutore: _____________________________________________

Firma studente (se >= 14 anni): ____________________________________
```

### Revoca del consenso

```
Il consenso puo' essere revocato in qualsiasi momento per i dati non ancora
anonimizzati. I dati gia' anonimizzati non sono piu' identificabili e
pertanto non possono essere cancellati o esclusi. Comunicare la revoca
all'admin IT della scuola (nome: ____________, email: ____________) o al
Dirigente Scolastico.
```

---

## Riepilogo per la famiglia

```
RIEPILOGO CONSENSI -- STUDENTE: ____________________________________

+-----+---------------------------------------------+--------+--------+
| Mod.| Trattamento                                 | SI     | NO     |
+-----+---------------------------------------------+--------+--------+
|  A  | Profilazione per adattamento contenuti       | [ ]    | [ ]    |
|  B  | Lingua nativa (dato sensibile Art. 9)        | [ ]    | [ ]    |
|  C  | Comunicazioni periodiche alla famiglia       | [ ]    | [ ]    |
|  D  | Storico cross-anno                           | [ ]    | [ ]    |
|  E  | Ricerca aggregata anonimizzata               | [ ]    | [ ]    |
+-----+---------------------------------------------+--------+--------+

Data: ____/____/________

Firma genitore/tutore: _____________________________________________

Firma studente (se >= 14 anni): ____________________________________

Note:
- Tutti i consensi sono INDIPENDENTI: potete acconsentire a uno, alcuni o tutti.
- Nessun consenso e' obbligatorio per frequentare le lezioni.
- Ogni consenso puo' essere revocato in qualsiasi momento.
- Per informazioni e revoche: admin IT _________________ (email: ____________)
  oppure DPO della scuola: _________________ (email: ____________)
```

---

## Note per l'admin IT

1. **Archiviazione**: i moduli cartacei firmati devono essere conservati in luogo sicuro (armadio chiuso a chiave) per l'intera durata dell'iscrizione dello studente + 10 anni per accountability.
2. **Registrazione nel sistema**: dopo aver raccolto i moduli firmati, l'admin IT registra i consensi nel sistema MAESTRO tramite l'endpoint `POST /api/v1/students/{id}/consent`, compilando il campo `paper_reference` con il riferimento al modulo cartaceo (es. "Modulo_A_Rossi_Mario_20260920").
3. **Revoche**: quando una famiglia comunica la revoca di un consenso, l'admin IT aggiorna il sistema entro 7 giorni lavorativi e annota la revoca sul modulo cartaceo con data e firma.
4. **Moduli per studenti < 14 anni**: verificare che sia presente la firma del genitore/tutore. La firma dello studente non e' richiesta.
5. **Moduli per studenti 14-17 anni**: verificare che siano presenti entrambe le firme (genitore/tutore + studente).

---

*Documento prodotto per il task T6.3 del DAG MAESTRO. I moduli vanno adattati all'intestazione dell'istituto scolastico ospitante il pilot.*
