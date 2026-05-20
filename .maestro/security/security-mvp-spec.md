# T3.5 -- Specifica Architettura di Sicurezza MVP

**Status**: Proposed
**Data**: 2026-05-20
**Autore**: MSTR-13 (Security Engineer)
**Revisori**: MSTR-02 (CTA), MSTR-12 (DevOps), MSTR-16 (Privacy & Compliance)
**Task**: T3.5
**Dipendenze**: ADR-001 (Tech Stack), ADR-004 (Data Model), HLD-001 (Multi-Agent System), HLD-004 (Data & Mastery State)
**Scope**: MVP -- 1 scuola, 1 classe, ~25 studenti minori (13-19 anni)

---

## 1. Principi di Sicurezza

### 1.1 Defence in Depth

La sicurezza MAESTRO e' stratificata su quattro livelli:

1. **Perimetro**: firewall Hetzner, TLS 1.3, HSTS
2. **Applicazione**: autenticazione Keycloak, RBAC, input validation, CSP
3. **Dati**: crittografia at rest (pgcrypto), pseudonimizzazione LLM, audit immutabile
4. **Infrastruttura**: SSH key-only, fail2ban, automatic updates, full-disk encryption

Ogni livello mitiga indipendentemente. La compromissione di un livello non espone automaticamente i dati.

### 1.2 Least Privilege

- 3 ruoli PostgreSQL con GRANT minimali (sezione 8)
- 3 ruoli Keycloak con scope di accesso distinti (sezione 3)
- L'applicazione usa `maestro_app` che non puo' eseguire DROP, ALTER, TRUNCATE
- L'erasure usa `maestro_erasure` con accesso limitato alla stored procedure dedicata

### 1.3 Privacy by Design per Minori

- **GDPR Art. 8**: tutti gli studenti sono minori. Il consenso genitoriale e' obbligatorio e gestito fuori sistema (cartaceo) nel MVP.
- **GDPR Art. 9**: la lingua nativa e' dato sensibile. Mai inviata a LLM esterni, mai associata all'identita' dello studente nei prompt.
- **Data minimisation**: solo i dati strettamente necessari vengono raccolti. `birth_year` anziche' data di nascita completa. Nessun dato biometrico.
- **Pseudonimizzazione al boundary LLM**: nessun PII raggiunge servizi esterni (N1).
- **Right to erasure**: stored procedure atomica gia' nel DDL (HLD-004 sezione 4.6).
- **Audit di ogni accesso a dati di minori**: ogni operazione su dati studente e' loggata con attore, timestamp, valore precedente e nuovo.

### 1.4 Riferimenti Normativi

| Norma | Applicazione MAESTRO |
|---|---|
| GDPR Art. 5 (principi) | Data minimisation, storage limitation, integrity/confidentiality |
| GDPR Art. 6 (base giuridica) | Legittimo interesse educativo + consenso per profilazione |
| GDPR Art. 8 (consenso minori) | Consenso genitoriale obbligatorio |
| GDPR Art. 9 (dati sensibili) | Lingua nativa trattata come dato Art. 9 |
| GDPR Art. 17 (diritto alla cancellazione) | Stored procedure atomica `core.execute_right_to_erasure` |
| GDPR Art. 25 (privacy by design) | Pseudonimizzazione, crittografia, audit |
| GDPR Art. 32 (sicurezza trattamento) | Crittografia at rest + in transit, access control, audit |
| D.Lgs. 196/2003 (Codice Privacy italiano) | Complementare al GDPR per minori in ambito scolastico |

---

## 2. Autenticazione Keycloak

### 2.1 Realm Setup

```json
{
  "realm": "maestro",
  "enabled": true,
  "displayName": "MAESTRO - Companion di Apprendimento",
  "registrationAllowed": false,
  "registrationEmailAsUsername": false,
  "resetPasswordAllowed": true,
  "loginWithEmailAllowed": true,
  "duplicateEmailsAllowed": false,
  "editUsernameAllowed": false,
  "bruteForceProtected": true,
  "permanentLockout": false,
  "maxFailureWaitSeconds": 900,
  "minimumQuickLoginWaitSeconds": 60,
  "waitIncrementSeconds": 60,
  "quickLoginCheckMilliSeconds": 1000,
  "maxDeltaTimeSeconds": 43200,
  "failureFactor": 5,
  "sslRequired": "all",
  "passwordPolicy": "length(12) and upperCase(1) and lowerCase(1) and digit(1) and specialChars(1) and notUsername and passwordHistory(3)",
  "accessTokenLifespan": 3600,
  "accessTokenLifespanForImplicitFlow": 900,
  "ssoSessionIdleTimeout": 1800,
  "ssoSessionMaxLifespan": 36000,
  "offlineSessionIdleTimeout": 2592000,
  "accessCodeLifespan": 60,
  "accessCodeLifespanUserAction": 300,
  "accessCodeLifespanLogin": 1800,
  "defaultSignatureAlgorithm": "RS256",
  "revokeRefreshToken": true,
  "refreshTokenMaxReuse": 0,
  "internationalizationEnabled": true,
  "supportedLocales": ["it"],
  "defaultLocale": "it"
}
```

### 2.2 Ruoli

| Ruolo | Descrizione | MFA | Popolazione MVP |
|---|---|---|---|
| `admin` | IT admin scuola. Gestione utenti, configurazione, audit export, erasure. | Obbligatorio (TOTP) | 1-2 persone |
| `teacher` | Docente. Upload lezioni, verifiche, override, dashboard classe. | Facoltativo (raccomandato) | 1 docente |
| `student` | Studente. Accesso alla propria mappa, missioni, quiz, contenuti. | Non richiesto | ~25 studenti |

### 2.3 Client Configuration

**Client: `maestro-student-app` (React Native)**

```json
{
  "clientId": "maestro-student-app",
  "protocol": "openid-connect",
  "publicClient": true,
  "standardFlowEnabled": true,
  "directAccessGrantsEnabled": false,
  "implicitFlowEnabled": false,
  "serviceAccountsEnabled": false,
  "authorizationServicesEnabled": false,
  "rootUrl": "maestro://",
  "redirectUris": ["maestro://callback", "http://localhost:8081/callback"],
  "webOrigins": ["+"],
  "attributes": {
    "pkce.code.challenge.method": "S256"
  },
  "defaultClientScopes": ["openid", "profile", "maestro-roles"],
  "optionalClientScopes": ["offline_access"]
}
```

**Client: `maestro-teacher-dashboard` (Next.js)**

```json
{
  "clientId": "maestro-teacher-dashboard",
  "protocol": "openid-connect",
  "publicClient": false,
  "secret": "<generato-al-deploy>",
  "standardFlowEnabled": true,
  "directAccessGrantsEnabled": false,
  "implicitFlowEnabled": false,
  "rootUrl": "https://dashboard.maestro.example",
  "redirectUris": ["https://dashboard.maestro.example/api/auth/callback/keycloak"],
  "webOrigins": ["https://dashboard.maestro.example"],
  "attributes": {
    "pkce.code.challenge.method": "S256"
  },
  "defaultClientScopes": ["openid", "profile", "maestro-roles"],
  "optionalClientScopes": ["offline_access"]
}
```

**Client: `maestro-admin` (Dashboard admin)**

```json
{
  "clientId": "maestro-admin",
  "protocol": "openid-connect",
  "publicClient": false,
  "secret": "<generato-al-deploy>",
  "standardFlowEnabled": true,
  "directAccessGrantsEnabled": false,
  "implicitFlowEnabled": false,
  "rootUrl": "https://admin.maestro.example",
  "redirectUris": ["https://admin.maestro.example/api/auth/callback/keycloak"],
  "webOrigins": ["https://admin.maestro.example"],
  "defaultClientScopes": ["openid", "profile", "maestro-roles"],
  "optionalClientScopes": ["offline_access"],
  "attributes": {
    "pkce.code.challenge.method": "S256"
  }
}
```

### 2.4 JWT Claims

Il token JWT emesso da Keycloak include i seguenti claims custom tramite un Protocol Mapper:

```json
{
  "sub": "keycloak-user-uuid",
  "preferred_username": "mario.rossi",
  "email": "mario.rossi@scuola.it",
  "realm_access": {
    "roles": ["student"]
  },
  "maestro": {
    "role": "student",
    "school_id": "uuid-scuola",
    "class_id": "uuid-classe",
    "student_id": "uuid-interno-maestro"
  },
  "iat": 1716200000,
  "exp": 1716203600,
  "iss": "https://auth.maestro.example/realms/maestro",
  "aud": "maestro-student-app"
}
```

**Keycloak Protocol Mapper** per i claims custom `maestro.*`:

```json
{
  "name": "maestro-claims",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-script-based-protocol-mapper",
  "config": {
    "multivalued": "false",
    "claim.name": "maestro",
    "jsonType.label": "JSON",
    "id.token.claim": "true",
    "access.token.claim": "true",
    "userinfo.token.claim": "true",
    "script": "// Script che legge gli attributi utente Keycloak\n// role, school_id, class_id, student_id sono attributi utente\nvar role = user.getFirstAttribute('maestro_role');\nvar schoolId = user.getFirstAttribute('maestro_school_id');\nvar classId = user.getFirstAttribute('maestro_class_id');\nvar studentId = user.getFirstAttribute('maestro_student_id');\nexports = { role: role, school_id: schoolId, class_id: classId, student_id: studentId };"
  }
}
```

### 2.5 Token Lifetime

| Parametro | Valore | Rationale |
|---|---|---|
| Access token | 1 ora (3600s) | Bilanciamento tra sicurezza e UX per sessioni scolastiche |
| Refresh token | 24 ore (86400s) | Copre una giornata scolastica senza re-login |
| SSO session idle | 30 minuti (1800s) | Timeout inattivita' ragionevole per contesto scolastico |
| SSO session max | 10 ore (36000s) | Copre giornata scolastica completa |
| Refresh token reuse | 0 (single-use) | Ogni refresh produce un nuovo refresh token. Detect token theft. |

### 2.6 MFA Admin (TOTP)

Configurazione TOTP obbligatoria per ruolo `admin`:

1. Al primo login, l'admin viene forzato a configurare un TOTP authenticator
2. Keycloak mostra QR code per Google Authenticator / Authy / FreeOTP
3. L'admin inserisce il codice di verifica a 6 cifre
4. Recovery codes (8 codici monouso) generati e mostrati una sola volta

**Enforcement via Keycloak Authentication Flow**:

- Creare un flow `maestro-admin-mfa` che richiede TOTP dopo username/password
- Assegnare il flow come "Browser Flow" per il client `maestro-admin`
- In alternativa (piu' semplice per MVP): usare "Conditional OTP" con condizione `role == admin`

**Configurazione nel realm**:

```json
{
  "otpPolicyType": "totp",
  "otpPolicyAlgorithm": "HmacSHA256",
  "otpPolicyDigits": 6,
  "otpPolicyPeriod": 30,
  "otpPolicyInitialCounter": 0,
  "otpPolicyLookAheadWindow": 1
}
```

### 2.7 Password Policy per MVP

| Regola | Valore | Applicazione |
|---|---|---|
| Lunghezza minima | 12 caratteri | Tutti i ruoli |
| Complessita' | Maiuscola + minuscola + numero + carattere speciale | Tutti i ruoli |
| Storico | Ultime 3 password non riutilizzabili | Tutti i ruoli |
| Username not in password | Si' | Tutti i ruoli |
| Brute force | Lock dopo 5 tentativi, wait 15 minuti | Tutti i ruoli |

**Per studenti (MVP)**: l'admin IT crea l'account con una password temporanea. Al primo login Keycloak forza il cambio password. La password deve rispettare la policy sopra.

---

## 3. Matrice RBAC

### 3.1 Regola Generale

Ogni endpoint REST e' protetto da JWT Keycloak. Il middleware FastAPI:

1. Valida la firma JWT (chiave pubblica dal JWKS endpoint Keycloak)
2. Verifica `exp` (scadenza)
3. Estrae `maestro.role`, `maestro.school_id`, `maestro.student_id`
4. Applica la matrice RBAC seguente

### 3.2 Matrice Completa

#### Student API

| Endpoint | `student` | `teacher` | `admin` | Scope |
|---|---|---|---|---|
| `GET /api/v1/students/{id}/knowledge-map` | SI (own) | SI (class) | SI (school) | Student: solo i propri dati. Teacher: studenti della propria classe. Admin: tutti nella scuola. |
| `GET /api/v1/students/{id}/missions` | SI (own) | SI (class) | SI (school) | Come sopra |
| `POST /api/v1/students/{id}/missions/{nodeId}/start` | SI (own) | NO | NO | Solo lo studente avvia le proprie missioni |
| `GET /api/v1/students/{id}/content/{contentId}` | SI (own) | SI (class) | NO | Student: propri contenuti. Teacher: contenuti della classe. |
| `POST /api/v1/students/{id}/quizzes/{quizId}/submit` | SI (own) | NO | NO | Solo lo studente sottomette i propri quiz |
| `GET /api/v1/students/{id}/retention-checks` | SI (own) | SI (class) | NO | Come knowledge-map |
| `GET /api/v1/students/{id}/notifications` | SI (own) | NO | NO | Solo le proprie notifiche |
| `GET /api/v1/students/{id}/profile` | SI (own) | SI (class) | NO | Student: proprio profilo. Teacher: profili della classe (lettura). |
| `PUT /api/v1/students/{id}/profile` | SI (own) | NO | NO | Solo lo studente modifica il proprio profilo |

#### Teacher API

| Endpoint | `student` | `teacher` | `admin` | Scope |
|---|---|---|---|---|
| `GET /api/v1/courses/{id}/class-heatmap` | NO | SI (own courses) | SI (school) | Teacher: solo i propri corsi |
| `POST /api/v1/courses/{id}/verifications` | NO | SI (own courses) | NO | Solo il docente del corso |
| `GET /api/v1/courses/{id}/verifications/{id}/transitions` | NO | SI (own courses) | SI (school) | Preview transizioni |
| `POST /api/v1/courses/{id}/verifications/{id}/transitions/confirm` | NO | SI (own courses) | NO | Solo il docente conferma |
| `POST /api/v1/courses/{id}/overrides` | NO | SI (own courses) | NO | F11.12: override con motivazione |
| `GET /api/v1/courses/{id}/overrides` | NO | SI (own courses) | SI (school) | Storico override |
| `POST /api/v1/courses/{id}/lessons` | NO | SI (own courses) | NO | Upload materiale |
| `GET /api/v1/courses/{id}/coverage` | NO | SI (own courses) | SI (school) | Report copertura |
| `GET /api/v1/courses/{id}/materials/{id}/mappings` | NO | SI (own courses) | NO | Review concept mapping |
| `POST /api/v1/courses/{id}/materials/{id}/mappings` | NO | SI (own courses) | NO | Conferma mapping |

#### KG API

| Endpoint | `student` | `teacher` | `admin` | Scope |
|---|---|---|---|---|
| `GET /api/v1/courses/{id}/kg/nodes` | SI (own courses) | SI (own courses) | SI (school) | Lettura nodi KG |
| `GET /api/v1/courses/{id}/kg/nodes/macro` | SI (own courses) | SI (own courses) | SI (school) | Lettura macro-nodi |
| `POST /api/v1/courses/{id}/kg/nodes` | NO | SI (own courses) | NO | Creazione nodi |
| `PUT /api/v1/courses/{id}/kg/nodes/{id}` | NO | SI (own courses) | NO | Modifica nodi |
| `DELETE /api/v1/courses/{id}/kg/nodes/{id}` | NO | SI (own courses) | NO | Disattivazione nodi |
| `POST /api/v1/courses/{id}/kg/edges` | NO | SI (own courses) | NO | Creazione archi |
| `DELETE /api/v1/courses/{id}/kg/edges/{id}` | NO | SI (own courses) | NO | Rimozione archi |

#### Admin API

| Endpoint | `student` | `teacher` | `admin` | Scope |
|---|---|---|---|---|
| `POST /api/v1/students` | NO | NO | SI | Creazione account studente |
| `POST /api/v1/students/{id}/consent` | NO | NO | SI | Registrazione consenso |
| `POST /api/v1/students/{id}/enrol` | NO | SI (own courses) | SI | Iscrizione a corso |
| `POST /api/v1/students/{id}/erasure` | NO | NO | SI | Diritto alla cancellazione |

#### Audit & Export API

| Endpoint | `student` | `teacher` | `admin` | Scope |
|---|---|---|---|---|
| `GET /api/v1/audit/export` | NO | NO | SI | Export CSV/JSON dell'audit log |
| `GET /api/v1/audit/students/{id}` | NO | NO | SI | Audit trail specifico per studente |

### 3.3 Implementazione FastAPI

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from functools import wraps

security = HTTPBearer()

KEYCLOAK_JWKS_URL = "https://auth.maestro.example/realms/maestro/protocol/openid-connect/certs"
KEYCLOAK_ISSUER = "https://auth.maestro.example/realms/maestro"

# Cache JWKS con refresh ogni 6 ore
_jwks_cache = None
_jwks_cache_time = None

async def get_current_user(credentials = Depends(security)) -> dict:
    """Valida il JWT e restituisce i claims dell'utente."""
    token = credentials.credentials
    try:
        jwks = await _get_jwks()  # Cached JWKS fetch
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=KEYCLOAK_ISSUER,
            options={"verify_aud": False}  # Verificato manualmente per flessibilita' multi-client
        )
        return {
            "sub": payload["sub"],
            "role": payload.get("maestro", {}).get("role"),
            "school_id": payload.get("maestro", {}).get("school_id"),
            "student_id": payload.get("maestro", {}).get("student_id"),
            "class_id": payload.get("maestro", {}).get("class_id"),
        }
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(*allowed_roles: str):
    """Decorator per verificare il ruolo dell'utente."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: dict = Depends(get_current_user), **kwargs):
            if user["role"] not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accesso non autorizzato per il ruolo corrente"
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

def require_own_data_or_role(student_id_param: str = "student_id", allowed_roles: tuple = ("teacher", "admin")):
    """
    Middleware: lo studente accede solo ai propri dati.
    Teacher e admin accedono ai dati della propria scuola/classe.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: dict = Depends(get_current_user), **kwargs):
            target_student_id = kwargs.get(student_id_param)

            if user["role"] == "student":
                if user["student_id"] != target_student_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Accesso negato: puoi accedere solo ai tuoi dati"
                    )
            elif user["role"] == "teacher":
                # Verificare che lo studente sia nella classe del docente
                # (query DB: enrolment + course.teacher_id == user.sub)
                if not await _is_student_in_teacher_class(target_student_id, user["sub"]):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Accesso negato: studente non nella tua classe"
                    )
            elif user["role"] == "admin":
                # Verificare che lo studente sia nella scuola dell'admin
                if not await _is_student_in_school(target_student_id, user["school_id"]):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Accesso negato: studente non nella tua scuola"
                    )
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator
```

---

## 4. Crittografia At Rest

### 4.1 Campi PII Crittografati

Conformemente a HLD-004, i seguenti campi sono crittografati con `pgcrypto` (`pgp_sym_encrypt` / `pgp_sym_decrypt`):

| Tabella | Campo | Tipo originale | Tipo storage |
|---|---|---|---|
| `core.student` | `name_encrypted` | TEXT | BYTEA |
| `core.student` | `surname_encrypted` | TEXT | BYTEA |
| `core.student` | `email_encrypted` | TEXT (nullable) | BYTEA (nullable) |
| `core.teacher` | `name_encrypted` | TEXT | BYTEA |
| `core.teacher` | `surname_encrypted` | TEXT | BYTEA |
| `core.teacher` | `email_encrypted` | TEXT (nullable) | BYTEA (nullable) |

### 4.2 Funzioni SQL di Encrypt/Decrypt

```sql
-- Funzione wrapper per crittografia
CREATE OR REPLACE FUNCTION core.encrypt_pii(p_plaintext TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(
        p_plaintext,
        current_setting('app.encryption_key'),
        'compress-algo=0, cipher-algo=aes256'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funzione wrapper per decrittografia
CREATE OR REPLACE FUNCTION core.decrypt_pii(p_ciphertext BYTEA)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(
        p_ciphertext,
        current_setting('app.encryption_key')
    );
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Decryption failed: %', SQLERRM;
        RETURN '[DECRYPTION_ERROR]';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Esempio di utilizzo: inserimento studente
INSERT INTO core.student (school_id, name_encrypted, surname_encrypted, email_encrypted, school_year)
VALUES (
    'uuid-scuola',
    core.encrypt_pii('Mario'),
    core.encrypt_pii('Rossi'),
    core.encrypt_pii('mario.rossi@example.com'),
    3
);

-- Esempio di utilizzo: lettura studente (solo dall'applicazione, mai in query di ricerca)
SELECT
    id,
    core.decrypt_pii(name_encrypted) AS name,
    core.decrypt_pii(surname_encrypted) AS surname,
    core.decrypt_pii(email_encrypted) AS email,
    school_year,
    status
FROM core.student
WHERE id = 'uuid-studente';
```

### 4.3 Gestione Chiave

**MVP**: la chiave di crittografia e' una variabile d'ambiente, mai nel codice sorgente.

```bash
# Sul server applicativo (in /etc/environment o equivalente)
MAESTRO_DB_ENCRYPTION_KEY="<chiave-generata-con-openssl-rand-base64-32>"

# Nella configurazione PostgreSQL (postgresql.conf o via ALTER SYSTEM)
# La chiave viene impostata come custom GUC parameter
# In alternativa, passata alla connessione dall'applicazione
```

**Impostazione nel codice Python (all'avvio dell'applicazione)**:

```python
import os
from sqlalchemy import text

ENCRYPTION_KEY = os.environ["MAESTRO_DB_ENCRYPTION_KEY"]

async def set_encryption_key(connection):
    """Imposta la chiave di crittografia per la sessione PostgreSQL corrente."""
    await connection.execute(
        text("SET app.encryption_key = :key"),
        {"key": ENCRYPTION_KEY}
    )
```

### 4.4 Procedura di Rotazione Chiave (Manuale, MVP)

La rotazione della chiave richiede la re-crittografia di tutti i campi PII. Per MVP (~25 studenti + 1 docente) questa operazione e' rapida.

```sql
-- 1. Impostare la vecchia chiave
SET app.encryption_key = '<vecchia-chiave>';

-- 2. Creare tabella temporanea con dati decriptati
CREATE TEMP TABLE temp_student_pii AS
SELECT
    id,
    pgp_sym_decrypt(name_encrypted, current_setting('app.encryption_key')) AS name_plain,
    pgp_sym_decrypt(surname_encrypted, current_setting('app.encryption_key')) AS surname_plain,
    pgp_sym_decrypt(email_encrypted, current_setting('app.encryption_key')) AS email_plain
FROM core.student
WHERE status != 'deleted';

-- 3. Impostare la nuova chiave
SET app.encryption_key = '<nuova-chiave>';

-- 4. Re-crittografare con la nuova chiave
UPDATE core.student s
SET
    name_encrypted = pgp_sym_encrypt(t.name_plain, current_setting('app.encryption_key'), 'compress-algo=0, cipher-algo=aes256'),
    surname_encrypted = pgp_sym_encrypt(t.surname_plain, current_setting('app.encryption_key'), 'compress-algo=0, cipher-algo=aes256'),
    email_encrypted = pgp_sym_encrypt(t.email_plain, current_setting('app.encryption_key'), 'compress-algo=0, cipher-algo=aes256')
FROM temp_student_pii t
WHERE s.id = t.id;

-- 5. Ripetere per core.teacher (stessa struttura)

-- 6. Eliminare tabella temporanea
DROP TABLE temp_student_pii;

-- 7. Aggiornare la variabile d'ambiente sul server con la nuova chiave
-- 8. Riavviare l'applicazione per caricare la nuova chiave
```

**Frequenza MVP**: rotazione manuale ogni 6 mesi o in caso di sospetta compromissione.

---

## 5. Crittografia In Transit

### 5.1 TLS 1.3 -- Configurazione Reverse Proxy

MAESTRO usa Caddy come reverse proxy per la terminazione TLS. Caddy gestisce automaticamente i certificati Let's Encrypt.

**Caddyfile**:

```caddyfile
{
    email admin@scuola.it
    acme_ca https://acme-v02.api.letsencrypt.org/directory
    # Solo TLS 1.3 (non serve backward compatibility per MVP)
}

# API backend (FastAPI)
api.maestro.example {
    reverse_proxy localhost:8000

    header {
        # HSTS: 1 anno, include sottodomini
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        # Impedisci embedding in iframe esterni
        X-Frame-Options "DENY"
        # Impedisci MIME type sniffing
        X-Content-Type-Options "nosniff"
        # Referrer policy restrittiva
        Referrer-Policy "strict-origin-when-cross-origin"
        # Permessi restrittivi
        Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"
        # Rimuovi header del server
        -Server
    }

    tls {
        protocols tls1.3 tls1.3
        curves x25519 secp256r1
    }
}

# Dashboard docente (Next.js)
dashboard.maestro.example {
    reverse_proxy localhost:3000

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"
        -Server
    }

    tls {
        protocols tls1.3 tls1.3
        curves x25519 secp256r1
    }
}

# Keycloak auth
auth.maestro.example {
    reverse_proxy localhost:8080

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        -Server
    }

    tls {
        protocols tls1.3 tls1.3
        curves x25519 secp256r1
    }
}
```

### 5.2 Certificate Management

| Aspetto | Configurazione |
|---|---|
| CA | Let's Encrypt (produzione), Let's Encrypt staging (test) |
| Protocollo ACME | HTTP-01 challenge (Caddy automatico) |
| Rinnovo | Automatico (Caddy rinnova 30 giorni prima della scadenza) |
| Algoritmo chiave | ECDSA P-256 (default Caddy) |
| Lifetime certificato | 90 giorni (standard Let's Encrypt) |
| Monitoring scadenza | Alert Grafana se il certificato scade entro 14 giorni |

### 5.3 Connessioni Interne

| Connessione | TLS | Note |
|---|---|---|
| Caddy -> FastAPI | No (localhost) | Stesso server, connessione loopback |
| Caddy -> Next.js | No (localhost) | Stesso server, connessione loopback |
| FastAPI -> PostgreSQL | Si' (sslmode=require) | Self-signed cert PG accettabile per localhost MVP |
| FastAPI -> Redis | No (localhost) | Stesso server. V1: TLS o Unix socket |
| FastAPI -> Keycloak | HTTPS | Tramite Caddy |
| FastAPI -> Claude/OpenAI API | HTTPS | Endpoint esterni, TLS obbligatorio |

---

## 6. Pseudonimizzazione LLM

### 6.1 Architettura

Il LLM Gateway (modulo Python interno a FastAPI, come da HLD-001 sezione 6.1) intercetta tutte le chiamate LLM e applica pseudonimizzazione bidirezionale.

```
[Agent Node]
    |
    v
[LLMGateway.call()]
    |
    v
[PseudonymisationService.pseudonymise(prompt)]
    |   - Sostituisce PII con pseudonimi
    |   - Crea mappa session-scoped in memoria
    |
    v
[ModelRouter.route(request)]
    |
    v
[Claude API / OpenAI API]  (riceve solo prompt pseudonimizzato)
    |
    v
[PseudonymisationService.de_pseudonymise(response)]
    |   - Sostituisce pseudonimi con valori reali
    |   - Distrugge la mappa
    |
    v
[Agent Node]  (riceve risposta con dati reali)
```

### 6.2 Regole di Pseudonimizzazione

```python
import hashlib
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PseudonymMap:
    """Mappa session-scoped. Vive solo in memoria durante una richiesta."""
    _forward: dict[str, str] = field(default_factory=dict)   # PII -> pseudonimo
    _reverse: dict[str, str] = field(default_factory=dict)   # pseudonimo -> PII

    def add(self, pii: str, pseudonym: str) -> None:
        self._forward[pii] = pseudonym
        self._reverse[pseudonym] = pii

    def pseudonymise(self, text: str) -> str:
        """Sostituisce tutti i PII noti con pseudonimi."""
        result = text
        # Ordina per lunghezza decrescente per evitare sostituzioni parziali
        for pii in sorted(self._forward.keys(), key=len, reverse=True):
            result = result.replace(pii, self._forward[pii])
        return result

    def de_pseudonymise(self, text: str) -> str:
        """Sostituisce pseudonimi con PII reali nella risposta LLM."""
        result = text
        for pseudonym in sorted(self._reverse.keys(), key=len, reverse=True):
            result = result.replace(pseudonym, self._reverse[pseudonym])
        return result

    def clear(self) -> None:
        """Distrugge la mappa. Chiamato dopo de-pseudonimizzazione."""
        self._forward.clear()
        self._reverse.clear()


PSEUDONYMISATION_RULES = {
    "student_name":    "STUDENTE_{hash8}",
    "teacher_name":    "DOCENTE_{hash8}",
    "school_name":     "SCUOLA_PILOTA",
    "class_name":      "CLASSE_A",
    "email":           "[RIMOSSO]",
    "native_language": "[RIMOSSO]",   # Art. 9: MAI inviata a LLM
    "registry_id":     "[RIMOSSO]",
    "phone":           "[RIMOSSO]",
    "birth_year":      "[RIMOSSO]",
}


def _hash8(value: str) -> str:
    """Genera hash a 8 caratteri per pseudonimizzazione."""
    return hashlib.sha256(value.encode()).hexdigest()[:8]


def build_pseudonym_map(
    student_name: Optional[str] = None,
    student_surname: Optional[str] = None,
    teacher_name: Optional[str] = None,
    teacher_surname: Optional[str] = None,
    school_name: Optional[str] = None,
    class_name: Optional[str] = None,
    email: Optional[str] = None,
    native_language: Optional[str] = None,
) -> PseudonymMap:
    """
    Costruisce la mappa di pseudonimizzazione per una richiesta.

    La mappa e' session-scoped: vive in memoria solo per la durata
    della chiamata LLM. Mai persistita su disco o inviata esternamente.
    """
    pmap = PseudonymMap()

    if student_name:
        full = f"{student_name} {student_surname}" if student_surname else student_name
        h = _hash8(full)
        pmap.add(full, f"STUDENTE_{h}")
        if student_surname:
            pmap.add(student_name, f"STUDENTE_{h}_NOME")
            pmap.add(student_surname, f"STUDENTE_{h}_COGNOME")

    if teacher_name:
        full = f"{teacher_name} {teacher_surname}" if teacher_surname else teacher_name
        h = _hash8(full)
        pmap.add(full, f"DOCENTE_{h}")
        if teacher_surname:
            pmap.add(teacher_name, f"DOCENTE_{h}_NOME")
            pmap.add(teacher_surname, f"DOCENTE_{h}_COGNOME")

    if school_name:
        pmap.add(school_name, "SCUOLA_PILOTA")

    if class_name:
        pmap.add(class_name, "CLASSE_A")

    if email:
        pmap.add(email, "[RIMOSSO]")

    if native_language:
        # La lingua nativa NON viene MAI inclusa nei prompt LLM.
        # Se per errore fosse presente, viene rimossa.
        pmap.add(native_language, "[RIMOSSO]")

    return pmap
```

### 6.3 Integrazione nel LLM Gateway

```python
class LLMGateway:
    """Gateway per tutte le chiamate LLM. Applica pseudonimizzazione."""

    async def call(
        self,
        request: "LLMRequest",
        student_context: Optional[dict] = None,
    ) -> "LLMResponse":
        # 1. Costruisci mappa pseudonimizzazione
        pmap = PseudonymMap()
        if student_context:
            pmap = build_pseudonym_map(
                student_name=student_context.get("name"),
                student_surname=student_context.get("surname"),
                teacher_name=student_context.get("teacher_name"),
                teacher_surname=student_context.get("teacher_surname"),
                school_name=student_context.get("school_name"),
                class_name=student_context.get("class_name"),
                email=student_context.get("email"),
                native_language=student_context.get("native_language"),
            )

        # 2. Pseudonimizza il prompt
        safe_system = pmap.pseudonymise(request.system_prompt)
        safe_context = pmap.pseudonymise(request.context_block)
        safe_task = pmap.pseudonymise(request.task_block)

        # 3. Verifica post-pseudonimizzazione: nessun PII residuo
        if not self._verify_no_pii_residual(safe_system + safe_context + safe_task, student_context):
            # FAIL-SAFE: se la verifica fallisce, blocca la chiamata
            raise PseudonymisationError(
                "PII residuo rilevato nel prompt dopo pseudonimizzazione. "
                "Chiamata LLM bloccata."
            )

        # 4. Chiamata LLM (tramite model router)
        raw_response = await self._model_router.call(
            system_prompt=safe_system,
            context_block=safe_context,
            task_block=safe_task,
            model_preference=request.model_preference,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        # 5. De-pseudonimizza la risposta
        real_response = pmap.de_pseudonymise(raw_response.content)

        # 6. Distruggi la mappa
        pmap.clear()

        # 7. Log audit (prompt hash, non prompt testo)
        await self._audit_logger.log_llm_call(
            request_id=request.correlation_id,
            agent_name=request.agent_name,
            model_id=raw_response.model_id,
            prompt_hash=hashlib.sha256(
                (safe_system + safe_context + safe_task).encode()
            ).hexdigest(),
            input_tokens=raw_response.input_tokens,
            output_tokens=raw_response.output_tokens,
            latency_ms=raw_response.latency_ms,
            cache_hit=raw_response.cache_hit,
        )

        return LLMResponse(
            content=real_response,
            model_id=raw_response.model_id,
            input_tokens=raw_response.input_tokens,
            output_tokens=raw_response.output_tokens,
            latency_ms=raw_response.latency_ms,
            cache_hit=raw_response.cache_hit,
            prompt_hash=hashlib.sha256(
                (safe_system + safe_context + safe_task).encode()
            ).hexdigest(),
        )

    def _verify_no_pii_residual(self, text: str, context: Optional[dict]) -> bool:
        """
        Verifica che nel testo pseudonimizzato non siano rimasti PII.
        Controllo difensivo: confronta con i valori noti del context.
        """
        if not context:
            return True
        pii_values = [
            v for v in [
                context.get("name"), context.get("surname"),
                context.get("email"), context.get("native_language"),
            ] if v
        ]
        text_lower = text.lower()
        for pii in pii_values:
            if pii.lower() in text_lower:
                return False
        return True
```

### 6.4 Gestione Fallimento Pseudonimizzazione

Se la pseudonimizzazione fallisce (`PseudonymisationError`):

1. La chiamata LLM viene **bloccata** (fail-closed)
2. L'errore viene loggato nell'audit log con dettaglio
3. L'agente che ha richiesto la chiamata riceve un errore
4. L'orchestratore attiva il fallback: contenuto dal materiale del docente (non generato da LLM)
5. Il docente riceve una notifica che la generazione di contenuto e' temporaneamente degradata

Questo approccio garantisce che **nessun PII raggiunge mai un LLM esterno**, anche in caso di bug nel codice di pseudonimizzazione.

---

## 7. Audit Log

### 7.1 Trigger di Immutabilita' PostgreSQL

La funzione `audit.deny_modify()` e' definita in HLD-004. Viene applicata a tutte le tabelle di audit.

```sql
-- Funzione condivisa per impedire UPDATE e DELETE su tabelle append-only
CREATE OR REPLACE FUNCTION audit.deny_modify()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION
        'Operazione % non consentita sulla tabella append-only %.%. '
        'Le tabelle di audit sono immutabili.',
        TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME
    USING ERRCODE = 'restrict_violation';
END;
$$ LANGUAGE plpgsql;

-- Applicazione a tutte le tabelle di audit

-- audit.audit_log
CREATE TRIGGER trg_audit_no_update
    BEFORE UPDATE ON audit.audit_log
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

CREATE TRIGGER trg_audit_no_delete
    BEFORE DELETE ON audit.audit_log
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

-- audit.llm_audit_log
CREATE TRIGGER trg_llm_audit_no_update
    BEFORE UPDATE ON audit.llm_audit_log
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

CREATE TRIGGER trg_llm_audit_no_delete
    BEFORE DELETE ON audit.llm_audit_log
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

-- audit.deletion_certificate
CREATE TRIGGER trg_delcert_no_update
    BEFORE UPDATE ON audit.deletion_certificate
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

CREATE TRIGGER trg_delcert_no_delete
    BEFORE DELETE ON audit.deletion_certificate
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

-- kmm.state_transition_log
CREATE TRIGGER trg_stl_no_update
    BEFORE UPDATE ON kmm.state_transition_log
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

CREATE TRIGGER trg_stl_no_delete
    BEFORE DELETE ON kmm.state_transition_log
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

-- kmm.teacher_override
CREATE TRIGGER trg_override_no_update
    BEFORE UPDATE ON kmm.teacher_override
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

CREATE TRIGGER trg_override_no_delete
    BEFORE DELETE ON kmm.teacher_override
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

-- core.consent_history
CREATE TRIGGER trg_consent_history_no_update
    BEFORE UPDATE ON core.consent_history
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();

CREATE TRIGGER trg_consent_history_no_delete
    BEFORE DELETE ON core.consent_history
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();
```

**Eccezione**: la stored procedure `core.execute_right_to_erasure` disabilita temporaneamente i trigger su `audit.audit_log` e `kmm.state_transition_log` per pseudonimizzare i record dello studente cancellato. Questa e' l'unica eccezione, documentata in HLD-004 sezione 5.4, ed e' essa stessa loggata nell'audit.

### 7.2 Eventi da Loggare (Lista Completa)

| Categoria | Evento | `action` field | Dettagli in `new_value` |
|---|---|---|---|
| **Autenticazione** | Login riuscito | `auth.login_success` | `{client_id, ip_hash}` |
| | Login fallito | `auth.login_failure` | `{client_id, ip_hash, reason}` |
| | Logout | `auth.logout` | `{client_id}` |
| | Password cambiata | `auth.password_change` | `{method: "self"|"admin_reset"}` |
| | MFA configurato | `auth.mfa_setup` | `{type: "totp"}` |
| **Identita'** | Studente creato | `student.create` | `{school_id, school_year}` (no PII) |
| | Studente attivato | `student.activate` | `{keycloak_user_id}` |
| | Studente sospeso | `student.suspend` | `{reason, expires_at}` |
| | Studente cancellato (erasure) | `student.erase` | `{deletion_certificate_id}` |
| | Docente creato | `teacher.create` | `{school_id, role}` |
| **Consenso** | Consenso concesso | `consent.grant` | `{consent_type, granted_by, legal_basis}` |
| | Consenso revocato | `consent.revoke` | `{consent_type, revoked_by}` |
| **Iscrizione** | Studente iscritto a corso | `enrolment.create` | `{course_id, academic_year}` |
| | Iscrizione ritirata | `enrolment.withdraw` | `{course_id, reason}` |
| **KMM** | Transizione di stato | `kmm.transition` | `{node_id, prev_state, new_state, trigger_type, quiz_score}` |
| | Override docente | `kmm.override` | `{node_id, prev_state, new_state, motivation}` |
| | Retention check completato | `kmm.retention_check` | `{node_id, result, score}` |
| **Contenuto** | Contenuto generato | `content.generate` | `{content_type, model_id, prompt_hash}` |
| | Contenuto consegnato a studente | `content.deliver` | `{content_id, channel}` |
| | Contenuto bloccato da safeguarding | `content.safeguarding_block` | `{reason, category, severity}` |
| **Lezione** | Materiale caricato | `lesson.upload` | `{material_id, file_type, size_bytes}` |
| | Concept mapping confermato | `lesson.mapping_confirm` | `{material_id, node_ids}` |
| **Verifica** | Verifica sottomessa | `verification.submit` | `{verification_id, student_count}` |
| | Transizioni confermate | `verification.transitions_confirm` | `{verification_id, transition_count}` |
| **Quiz** | Quiz sottomesso | `quiz.submit` | `{quiz_id, node_id, score}` |
| **Profilo** | Profilo aggiornato | `profile.update` | `{source, prev_profile, new_profile}` |
| **Admin** | Export audit | `admin.audit_export` | `{format, date_range, record_count}` |
| | Configurazione sistema | `admin.config_change` | `{setting, prev_value, new_value}` |
| **LLM** | Chiamata LLM | (in `audit.llm_audit_log`) | `{agent_name, model_id, prompt_hash, tokens, latency}` |
| **Wellbeing** | Alert wellbeing | `wellbeing.alert` | `{type, student_pseudo_id, recommended_action}` |

### 7.3 Formato Record

Ogni record in `audit.audit_log` ha la seguente struttura (come da HLD-004 sezione 5.2):

```sql
-- Struttura del record
{
    id:              BIGINT (auto-incremento),
    actor_id:        TEXT,          -- UUID dell'attore (o hash post-erasure)
    actor_type:      TEXT,          -- 'student' | 'teacher' | 'admin' | 'system' | 'parent'
    action:          TEXT,          -- Dall'elenco sopra (es. 'kmm.transition')
    entity_type:     TEXT,          -- Tipo entita' (es. 'student', 'node_state', 'consent')
    entity_id:       TEXT,          -- ID dell'entita' coinvolta
    previous_value:  JSONB,        -- Stato precedente (nullable)
    new_value:       JSONB,        -- Stato successivo
    ip_address_hash: TEXT,         -- SHA-256 dell'IP (mai l'IP raw)
    user_agent_hash: TEXT,         -- SHA-256 dello user agent
    created_at:      TIMESTAMPTZ   -- Timestamp con timezone
}
```

### 7.4 Export API

```python
@app.get("/api/v1/audit/export")
@require_role("admin")
async def export_audit_log(
    format: Literal["csv", "json"] = "json",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    entity_type: Optional[str] = None,
    actor_id: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    """
    Export dell'audit log. Solo admin.
    L'export stesso viene loggato nell'audit.
    """
    # Costruisci query con filtri
    query = select(AuditLog)
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if actor_id:
        query = query.where(AuditLog.actor_id == actor_id)

    results = await db.execute(query)
    records = results.all()

    # Log dell'export nell'audit
    await log_audit_event(
        actor_id=user["sub"],
        actor_type="admin",
        action="admin.audit_export",
        entity_type="audit_log",
        entity_id="export",
        new_value={
            "format": format,
            "date_range": f"{start_date} - {end_date}",
            "record_count": len(records),
        }
    )

    if format == "csv":
        return StreamingResponse(
            _generate_csv(records),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_export.csv"}
        )
    return {"data": [_serialize_audit_record(r) for r in records]}
```

### 7.5 Retention e Partitioning

| Aspetto | Configurazione |
|---|---|
| Retention | 5 anni (conservativo, allineamento normativa scolastica italiana) |
| Partitioning | Mensile (RANGE su `created_at`) |
| Gestione partizioni | pg_partman crea partizioni automaticamente |
| Eliminazione vecchie partizioni | Dopo 5 anni, `DROP PARTITION` delle partizioni scadute |
| Backup | Le partizioni di audit sono incluse nei backup WAL giornalieri |

```sql
-- Configurazione pg_partman per audit_log
SELECT partman.create_parent(
    p_parent_table := 'audit.audit_log',
    p_control := 'created_at',
    p_type := 'range',
    p_interval := '1 month',
    p_premake := 3,                -- Crea 3 mesi in anticipo
    p_start_partition := '2026-09-01'  -- Inizio anno scolastico
);

-- Stessa configurazione per llm_audit_log e state_transition_log
SELECT partman.create_parent(
    p_parent_table := 'audit.llm_audit_log',
    p_control := 'created_at',
    p_type := 'range',
    p_interval := '1 month',
    p_premake := 3,
    p_start_partition := '2026-09-01'
);

-- Job pg_cron per manutenzione partizioni
SELECT cron.schedule(
    'partition_maintenance',
    '0 3 * * 0',  -- Ogni domenica alle 3:00
    $$SELECT partman.run_maintenance()$$
);
```

---

## 8. Database Roles

### 8.1 Definizione Ruoli

```sql
-- Ruolo applicativo principale: usato dal backend FastAPI
CREATE ROLE maestro_app LOGIN PASSWORD '<password-complessa-generata>';
COMMENT ON ROLE maestro_app IS
    'Ruolo applicativo principale. SELECT, INSERT su tutte le tabelle. '
    'UPDATE limitato ai campi necessari. Nessun DROP, ALTER, TRUNCATE.';

-- Ruolo di sola lettura: usato per dashboard, monitoring, export
CREATE ROLE maestro_readonly LOGIN PASSWORD '<password-complessa-generata>';
COMMENT ON ROLE maestro_readonly IS
    'Ruolo di sola lettura. SELECT su tutte le tabelle. '
    'Usato per dashboard Grafana, export audit, query analitiche.';

-- Ruolo per erasure: usato solo dalla stored procedure di cancellazione
CREATE ROLE maestro_erasure LOGIN PASSWORD '<password-complessa-generata>';
COMMENT ON ROLE maestro_erasure IS
    'Ruolo per right-to-erasure. Puo eseguire solo la stored procedure '
    'core.execute_right_to_erasure. Nessun accesso diretto alle tabelle.';
```

### 8.2 GRANT Statements

```sql
-- ============================================================
-- SCHEMA GRANTS
-- ============================================================
GRANT USAGE ON SCHEMA core TO maestro_app, maestro_readonly, maestro_erasure;
GRANT USAGE ON SCHEMA kmm TO maestro_app, maestro_readonly;
GRANT USAGE ON SCHEMA content TO maestro_app, maestro_readonly;
GRANT USAGE ON SCHEMA audit TO maestro_app, maestro_readonly;
GRANT USAGE ON SCHEMA kg TO maestro_app, maestro_readonly;

-- ============================================================
-- maestro_app: SELECT + INSERT su tutto, UPDATE limitato
-- ============================================================

-- core.*
GRANT SELECT, INSERT ON core.student TO maestro_app;
GRANT UPDATE (status, consent_completed_at, activated_at, suspended_at,
              adaptation_profile, adaptation_profile_source, tone_preference,
              content_length_preference, native_language, bilingualism_active,
              accessibility_prefs, keycloak_user_id, suspension_expires_at)
    ON core.student TO maestro_app;
-- NOTA: name_encrypted, surname_encrypted, email_encrypted, birth_year, school_registry_ref
-- sono aggiornabili SOLO dalla stored procedure di erasure

GRANT SELECT, INSERT ON core.teacher TO maestro_app;
GRANT SELECT, INSERT ON core.school TO maestro_app;
GRANT SELECT, INSERT ON core.course TO maestro_app;
GRANT UPDATE (status, kg_graph_name) ON core.course TO maestro_app;
GRANT SELECT, INSERT ON core.enrolment TO maestro_app;
GRANT UPDATE (status) ON core.enrolment TO maestro_app;
GRANT SELECT, INSERT ON core.consent TO maestro_app;
GRANT UPDATE (revoked_at) ON core.consent TO maestro_app;
GRANT SELECT, INSERT ON core.consent_history TO maestro_app;
GRANT SELECT, INSERT ON core.notification TO maestro_app;
GRANT UPDATE (status, read_at) ON core.notification TO maestro_app;

-- kmm.*
GRANT SELECT, INSERT ON kmm.student_node_state TO maestro_app;
GRANT UPDATE (current_state, state_since, attempt_count, last_quiz_score,
              last_quiz_at, next_retention_check, retention_checks_passed,
              fsrs_stability, fsrs_difficulty, last_seen, last_reinforced)
    ON kmm.student_node_state TO maestro_app;
GRANT SELECT, INSERT ON kmm.state_transition_log TO maestro_app;
-- NO UPDATE, NO DELETE su state_transition_log (trigger lo impedisce comunque)
GRANT SELECT, INSERT ON kmm.teacher_override TO maestro_app;
GRANT SELECT, INSERT ON kmm.retention_schedule TO maestro_app;
GRANT UPDATE (status, completed_at, quiz_score, response_time_ms)
    ON kmm.retention_schedule TO maestro_app;

-- content.*
GRANT SELECT, INSERT ON content.generated_content TO maestro_app;
GRANT SELECT, INSERT ON content.question_bank TO maestro_app;
GRANT SELECT, INSERT ON content.bilingual_glossary TO maestro_app;
GRANT SELECT, INSERT ON content.lesson_material TO maestro_app;
GRANT SELECT, INSERT ON content.lesson_transcript TO maestro_app;
GRANT SELECT, INSERT ON content.lesson_chunk TO maestro_app;

-- audit.*
GRANT SELECT, INSERT ON audit.audit_log TO maestro_app;
-- NO UPDATE, NO DELETE (trigger + GRANT)
GRANT SELECT, INSERT ON audit.llm_audit_log TO maestro_app;
GRANT SELECT ON audit.deletion_certificate TO maestro_app;
-- INSERT su deletion_certificate solo dalla stored procedure di erasure

-- kg.*
GRANT SELECT, INSERT, UPDATE ON kg.node TO maestro_app;
GRANT SELECT, INSERT, UPDATE ON kg.edge TO maestro_app;
GRANT SELECT, INSERT ON kg.node_embedding TO maestro_app;
GRANT SELECT, INSERT, UPDATE ON kg.concept_node_link TO maestro_app;
GRANT SELECT, INSERT ON kg.error_node_mapping TO maestro_app;

-- Sequenze
GRANT USAGE ON ALL SEQUENCES IN SCHEMA core TO maestro_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA kmm TO maestro_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA content TO maestro_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA audit TO maestro_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA kg TO maestro_app;

-- ============================================================
-- maestro_readonly: solo SELECT
-- ============================================================
GRANT SELECT ON ALL TABLES IN SCHEMA core TO maestro_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA kmm TO maestro_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA content TO maestro_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA audit TO maestro_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA kg TO maestro_readonly;

-- Applicare anche a tabelle future
ALTER DEFAULT PRIVILEGES IN SCHEMA core GRANT SELECT ON TABLES TO maestro_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA kmm GRANT SELECT ON TABLES TO maestro_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA content GRANT SELECT ON TABLES TO maestro_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT SELECT ON TABLES TO maestro_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA kg GRANT SELECT ON TABLES TO maestro_readonly;

-- ============================================================
-- maestro_erasure: solo la stored procedure
-- ============================================================
GRANT EXECUTE ON FUNCTION core.execute_right_to_erasure(UUID, UUID, TEXT) TO maestro_erasure;
-- La stored procedure e' SECURITY DEFINER (gira con i permessi del proprietario, non del chiamante).
-- maestro_erasure non ha accesso diretto a nessuna tabella.

-- Il proprietario della stored procedure deve avere permessi completi
-- (tipicamente il superuser o un ruolo owner dedicato):
ALTER FUNCTION core.execute_right_to_erasure(UUID, UUID, TEXT) OWNER TO maestro_owner;
```

### 8.3 Principio Least Privilege

| Ruolo | SELECT | INSERT | UPDATE | DELETE | DROP/ALTER | Stored Proc |
|---|---|---|---|---|---|---|
| `maestro_app` | SI (tutto) | SI (tutto) | Solo campi specifici | NO | NO | NO |
| `maestro_readonly` | SI (tutto) | NO | NO | NO | NO | NO |
| `maestro_erasure` | NO (diretto) | NO (diretto) | NO (diretto) | NO (diretto) | NO | Solo `execute_right_to_erasure` |

Il ruolo `maestro_app` non puo' mai:
- Eliminare dati (DELETE su nessuna tabella)
- Modificare lo schema (DROP, ALTER, TRUNCATE)
- Aggiornare campi PII crittografati (eccetto via erasure)
- Accedere ad audit log in scrittura UPDATE/DELETE

---

## 9. Input Validation

### 9.1 Strategia Complessiva

La validazione input e' stratificata su tre livelli:

1. **Pydantic (FastAPI)**: validazione di tipo, formato, lunghezza su ogni request body
2. **SQLAlchemy ORM**: query parametrizzate (mai string concatenation in SQL)
3. **PostgreSQL CHECK constraints**: invarianti a livello di schema (es. stati validi)

### 9.2 Pydantic Validation (FastAPI)

```python
from pydantic import BaseModel, Field, validator
from uuid import UUID
import re

class StudentCreateRequest(BaseModel):
    """Validazione per creazione studente."""
    school_id: UUID
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    school_year: int = Field(ge=1, le=5)
    birth_year: int | None = Field(default=None, ge=2006, le=2013)

    @validator("name", "surname")
    def no_control_chars(cls, v):
        """Impedisci caratteri di controllo nei nomi."""
        if re.search(r'[\x00-\x1f\x7f]', v):
            raise ValueError("Caratteri di controllo non consentiti")
        return v.strip()

    @validator("email")
    def valid_email(cls, v):
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("Formato email non valido")
        return v.lower().strip()


class TeacherOverrideRequest(BaseModel):
    """Validazione per override docente (F11.12)."""
    student_id: UUID
    node_id: str = Field(min_length=1, max_length=255)
    course_id: UUID
    forced_state: str = Field(pattern=r'^(non_introdotto|introdotto|lacuna|in_recupero|da_consolidare|consolidato)$')
    motivation: str = Field(min_length=20, max_length=1000)

    @validator("motivation")
    def no_empty_motivation(cls, v):
        """La motivazione deve avere contenuto reale, non solo spazi."""
        if len(v.strip()) < 20:
            raise ValueError("La motivazione deve contenere almeno 20 caratteri significativi")
        return v.strip()


class QuizSubmitRequest(BaseModel):
    """Validazione per sottomissione quiz."""
    answers: list[dict] = Field(min_length=1, max_length=20)
    total_time_ms: int = Field(ge=0, le=3600000)  # Max 1 ora

    @validator("answers")
    def validate_answers(cls, v):
        for answer in v:
            if "question_id" not in answer or "selected" not in answer:
                raise ValueError("Ogni risposta richiede question_id e selected")
        return v
```

### 9.3 SQLAlchemy ORM (Parameterized Queries)

```python
# CORRETTO: query parametrizzata tramite ORM
result = await session.execute(
    select(StudentNodeState)
    .where(
        StudentNodeState.student_id == student_id,
        StudentNodeState.course_id == course_id,
    )
)

# CORRETTO: query parametrizzata tramite text()
result = await session.execute(
    text("SELECT * FROM kmm.student_node_state WHERE student_id = :sid AND course_id = :cid"),
    {"sid": student_id, "cid": course_id}
)

# VIETATO: mai string concatenation in SQL
# result = await session.execute(f"SELECT * FROM ... WHERE id = '{student_id}'")  # SQL INJECTION!
```

### 9.4 CSP Headers (Next.js Dashboard)

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval'",  // Next.js richiede unsafe-eval in dev; in prod usare nonce
      "style-src 'self' 'unsafe-inline'",  // CSS-in-JS richiede unsafe-inline; V1: migrare a nonce
      "img-src 'self' data: blob:",
      "font-src 'self'",
      "connect-src 'self' https://api.maestro.example https://auth.maestro.example wss://api.maestro.example",
      "frame-ancestors 'none'",
      "form-action 'self'",
      "base-uri 'self'",
      "object-src 'none'",
    ].join('; '),
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), payment=()',
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};
```

### 9.5 Output Escaping

- **React (Next.js)**: React esegue escape automatico di JSX. Non usare mai `dangerouslySetInnerHTML` per contenuti generati da LLM.
- **React Native**: il rendering testuale e' sicuro per default. Le WebView (se usate) devono avere `javaScriptEnabled={false}` a meno che strettamente necessario.
- **API JSON**: FastAPI serializza automaticamente in JSON. Mai costruire JSON manualmente con string concatenation.
- **Markdown**: il contenuto generato da LLM viene renderizzato come markdown. Usare un renderer markdown che sanifica l'HTML (es. `markdown-it` con `html: false`).

---

## 10. Hardening Infrastruttura

### 10.1 Hetzner Cloud -- Firewall Rules

```
# Regole firewall Hetzner Cloud (applicate al server principale)

# Inbound
ALLOW TCP 443  FROM 0.0.0.0/0     # HTTPS (Caddy)
ALLOW TCP 80   FROM 0.0.0.0/0     # HTTP (redirect a HTTPS, ACME challenge)
ALLOW TCP 22   FROM <IP-admin>/32  # SSH solo da IP admin
DENY  ALL      FROM 0.0.0.0/0     # Blocca tutto il resto

# Outbound
ALLOW TCP 443  TO 0.0.0.0/0       # HTTPS verso API LLM, Let's Encrypt
ALLOW TCP 53   TO 0.0.0.0/0       # DNS
ALLOW UDP 53   TO 0.0.0.0/0       # DNS
ALLOW TCP 587  TO 0.0.0.0/0       # SMTP (notifiche email, se abilitato)
DENY  ALL      TO 0.0.0.0/0       # Blocca tutto il resto
```

**Note**:
- PostgreSQL (5432), Redis (6379), FastAPI (8000), Next.js (3000), Keycloak (8080) NON sono esposti a Internet
- Tutto il traffico esterno passa tramite Caddy (443)
- SSH limitato all'IP dell'amministratore di sistema

### 10.2 SSH Hardening

```bash
# /etc/ssh/sshd_config

# Autenticazione solo via chiave
PasswordAuthentication no
ChallengeResponseAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# Disabilitare root login
PermitRootLogin no

# Solo utente dedicato
AllowUsers maestro-admin

# Protocollo e crittografia
Protocol 2
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# Timeout
ClientAliveInterval 300
ClientAliveCountMax 2
LoginGraceTime 30

# Logging
LogLevel VERBOSE

# Disabilitare forwarding (non necessario per MVP)
AllowTcpForwarding no
X11Forwarding no
AllowAgentForwarding no
```

### 10.3 Fail2ban

```ini
# /etc/fail2ban/jail.local

[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200

[caddy-auth]
enabled = true
port = 443
logpath = /var/log/caddy/access.log
filter = caddy-auth
maxretry = 10
findtime = 300
bantime = 3600
```

```ini
# /etc/fail2ban/filter.d/caddy-auth.conf
[Definition]
failregex = ^.*"remote_ip":"<HOST>".*"status":401.*$
            ^.*"remote_ip":"<HOST>".*"status":403.*$
ignoreregex =
```

### 10.4 Automatic Updates

```bash
# Abilitare unattended-upgrades (Ubuntu/Debian)
apt install unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades

# /etc/apt/apt.conf.d/50unattended-upgrades
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";  # No reboot automatico, alert manuale
Unattended-Upgrade::Mail "admin@scuola.it";
```

### 10.5 Full-Disk Encryption

Hetzner Cloud offre full-disk encryption a livello di hypervisor per i server cloud. Per MVP questo e' sufficiente.

Per i backup su Scaleway S3, i file vengono crittografati lato server (SSE-S3) automaticamente da Scaleway.

### 10.6 Scaleway S3 -- Bucket Policy

```json
{
  "Version": "2023-04-17",
  "Statement": [
    {
      "Sid": "DenyPublicAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:scw:s3:::maestro-materials/*",
      "Condition": {
        "StringNotEquals": {
          "aws:PrincipalArn": "arn:scw:iam::maestro-project:application/maestro-backend"
        }
      }
    },
    {
      "Sid": "RequireEncryption",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:scw:s3:::maestro-materials/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

**Configurazione bucket**:
- Public access: **disabilitato**
- Versioning: abilitato (protezione da cancellazione accidentale)
- Server-side encryption: AES-256 (SSE-S3)
- Lifecycle rules: backup WAL > 30 giorni -> Glacier class (costo ridotto)
- CORS: disabilitato (nessun accesso diretto dal browser)

---

## 11. Threat Model STRIDE

### 11.1 Metodologia

Analisi STRIDE applicata ai componenti principali del sistema MVP, con focus sui 5 rischi maggiori per un sistema che gestisce dati di minori.

### 11.2 Analisi per Categoria

#### S -- Spoofing (Impersonazione)

| Componente | Minaccia | Rischio MVP | Mitigazione |
|---|---|---|---|
| Login studente | Un attaccante ottiene le credenziali di uno studente | MEDIO | Password policy robusta (12 char), brute force protection (lock 5 tentativi), Keycloak session management |
| Login admin | Impersonazione dell'admin per accedere a dati di tutti gli studenti | ALTO | MFA obbligatorio (TOTP), password policy, IP whitelisting SSH |
| JWT | Token JWT rubato (XSS, MITM) | MEDIO | TLS 1.3 (no MITM), token lifetime breve (1h), refresh token single-use, HttpOnly cookies per dashboard web |
| API inter-servizio | Un servizio malevolo invia richieste all'API interna | BASSO (MVP) | Tutti i servizi su localhost, nessuna porta esposta a Internet. V1: mTLS |

#### T -- Tampering (Manomissione)

| Componente | Minaccia | Rischio MVP | Mitigazione |
|---|---|---|---|
| Audit log | Modifica o cancellazione di record di audit per nascondere attivita' | ALTO | Trigger `deny_modify()` su tutte le tabelle di audit. Solo `execute_right_to_erasure` puo' modificare (con log). DB role `maestro_app` non ha DELETE/UPDATE su audit. |
| State transitions | Modifica diretta del database per alterare lo stato di uno studente | MEDIO | Application-level enforcement. DB role senza DELETE su `student_node_state`. `state_transition_log` immutabile. |
| Dati in transito | MITM per modificare risposte API | BASSO | TLS 1.3 su tutti gli endpoint. HSTS preload. |
| Upload materiali | Upload di file malevoli tramite la funzione di caricamento lezioni | MEDIO | Validazione MIME type, scansione antivirus (ClamAV), dimensione massima (500MB per video), storage su S3 con ACL restrittive |

#### R -- Repudiation (Ripudio)

| Componente | Minaccia | Rischio MVP | Mitigazione |
|---|---|---|---|
| Override docente | Docente nega di aver effettuato un override | MEDIO | Audit log immutabile con actor_id, timestamp, motivazione (min 20 char). JWT firmato identifica il docente. |
| Cancellazione studente | Admin nega di aver eseguito l'erasure | BASSO | `deletion_certificate` immutabile con `executed_by`, `executed_at`. Audit log dell'operazione. |
| Accesso dati | Attore nega di aver acceduto ai dati di uno studente | MEDIO | Audit log di ogni accesso. IP hash e user agent hash registrati. |

#### I -- Information Disclosure (Divulgazione)

| Componente | Minaccia | Rischio MVP | Mitigazione |
|---|---|---|---|
| PII verso LLM | Dati personali dello studente inviati a Claude/OpenAI | **CRITICO** | Pseudonimizzazione al boundary LLM Gateway. Verifica post-pseudonimizzazione. Fail-closed se PII residuo. Lingua nativa MAI inviata. |
| PII nel database | Accesso non autorizzato al database espone nomi, email | ALTO | pgcrypto encryption at rest. DB roles minimali. Full-disk encryption. SSH key-only. |
| Error messages | Messaggi di errore espongono informazioni interne | MEDIO | FastAPI exception handlers che restituiscono messaggi generici. Stack trace solo in log interni, mai nella risposta API. |
| Log applicativi | PII nei log del server | MEDIO | Logging policy: mai loggare PII. Loggare solo UUID, hash, pseudonimi. Rotazione log automatica. |
| Accesso cross-studente | Uno studente accede ai dati di un altro studente | **CRITICO** | RBAC: `require_own_data_or_role()` su ogni endpoint studente. Verifica server-side che `student_id` nel JWT corrisponda al path parameter. |

#### D -- Denial of Service (Negazione del Servizio)

| Componente | Minaccia | Rischio MVP | Mitigazione |
|---|---|---|---|
| API FastAPI | Flood di richieste | BASSO (25 utenti) | Rate limiting in Caddy (100 req/min per IP). MVP scale non giustifica DDoS protection. |
| LLM API | Costo eccessivo per chiamate LLM massive | MEDIO | Rate limiting per studente (max 20 chiamate LLM/ora). Budget alert giornaliero. Circuit breaker. |
| PostgreSQL | Connection exhaustion | BASSO | Connection pool (max 20 connections). PgBouncer se necessario. |
| Upload lezioni | Upload di file enormi per saturare lo storage | BASSO | Limite 500MB per file. Quota per corso (5GB MVP). |

#### E -- Elevation of Privilege (Escalazione)

| Componente | Minaccia | Rischio MVP | Mitigazione |
|---|---|---|---|
| JWT manipulation | Modifica del JWT per cambiare il ruolo (es. student -> admin) | ALTO | JWT firmato con RS256 (chiave privata Keycloak). Verifica firma su ogni richiesta. Mai fidarsi del client. |
| RBAC bypass | Studente accede a endpoint teacher/admin | ALTO | Middleware `require_role()` su ogni endpoint. Verifica server-side. |
| SQL injection | Iniezione SQL per ottenere accesso al database | MEDIO | SQLAlchemy ORM (parameterized). Pydantic validation. DB role senza permessi pericolosi. |
| Prompt injection | Studente inietta istruzioni nel prompt LLM per ottenere risposte non autorizzate | MEDIO | System prompt con istruzioni forti. Safeguarding Agent post-generazione. Input validation. Output validation. Separazione tra system prompt e user input. |

### 11.3 Top 5 Rischi MVP con Mitigazioni

| # | Rischio | Categoria STRIDE | Gravita' | Mitigazione Primaria | Mitigazione Secondaria |
|---|---|---|---|---|---|
| 1 | PII leak verso LLM esterno | Information Disclosure | **CRITICO** | Pseudonimizzazione al LLM Gateway con verifica post-sostituzione | Fail-closed: se la verifica fallisce, la chiamata LLM non parte |
| 2 | Accesso non autorizzato a dati di un altro studente | Information Disclosure + Elevation | **CRITICO** | RBAC con verifica server-side `own data` su ogni endpoint | Audit log di ogni accesso a dati studente |
| 3 | Manomissione audit log | Tampering | ALTO | Trigger `deny_modify()` + DB role senza DELETE/UPDATE su audit | pg_audit per logging accessi a livello PostgreSQL |
| 4 | Impersonazione admin (accesso a tutti i dati) | Spoofing | ALTO | MFA TOTP obbligatorio + brute force protection + IP whitelist SSH | Session idle timeout 30 min |
| 5 | SQL injection / XSS | Tampering + Info Disclosure | MEDIO | ORM parametrizzato + Pydantic + CSP + React auto-escape | DB role senza DROP/ALTER/TRUNCATE |

---

## 12. Incident Response MVP

### 12.1 Classificazione Incidenti

| Severita' | Descrizione | Esempio | Tempo Risposta |
|---|---|---|---|
| **P1 -- Critico** | Compromissione dati personali di minori | PII leak, accesso non autorizzato al DB, data breach | Immediato (<1 ora) |
| **P2 -- Alto** | Compromissione del sistema senza evidenza di data leak | Server compromesso, credenziali rubate, malware | <4 ore |
| **P3 -- Medio** | Vulnerabilita' sfruttabile ma non sfruttata | SQL injection trovata, dependency vulnerabile | <24 ore |
| **P4 -- Basso** | Anomalia di sicurezza senza impatto immediato | Tentativi di brute force, scan di porte | <72 ore |

### 12.2 Catena di Comunicazione

```
Rilevamento incidente
    |
    v
MSTR-12 (DevOps) + MSTR-13 (Security)  -- Valutazione iniziale
    |
    v
[P1/P2?] --SI--> MSTR-02 (CTA) + MSTR-01 (Programme Director) -- Entro 30 minuti
    |                  |
    |                  v
    |              Daniele (Human owner) -- Entro 1 ora
    |                  |
    |                  v
    |              Referente IT scuola -- Entro 2 ore
    |                  |
    |                  v
    |              [Data breach di PII?] --SI--> Garante Privacy -- Entro 72 ore (GDPR Art. 33)
    |                                            DPO scuola -- Entro 24 ore
    |
    [P3/P4?] ---> MSTR-02 (CTA) -- Entro 24 ore
                       |
                       v
                   Fix + deploy
```

### 12.3 Procedura di Isolamento

**Passo 1: Contenimento immediato (P1/P2)**

```bash
# 1. Bloccare accesso esterno al server (mantenere SSH per remediation)
# Hetzner Cloud: aggiornare il firewall tramite API o console
hcloud firewall delete-rule <firewall-id> --direction in --protocol tcp --port 443
hcloud firewall delete-rule <firewall-id> --direction in --protocol tcp --port 80

# 2. Fermare l'applicazione
systemctl stop maestro-api
systemctl stop maestro-dashboard

# 3. NON fermare PostgreSQL (preservare log e evidenze)
# 4. NON fermare il servizio di monitoring (preservare metriche)
```

**Passo 2: Preservazione evidenze**

```bash
# Snapshot del server (Hetzner Cloud)
hcloud server create-image --type snapshot --description "incident-$(date +%Y%m%d-%H%M)" <server-id>

# Export dei log
journalctl --since "24 hours ago" > /tmp/incident-journal.log
cp /var/log/caddy/access.log /tmp/incident-caddy.log

# Export audit log
psql -U maestro_readonly -d maestro -c "COPY (SELECT * FROM audit.audit_log WHERE created_at > now() - interval '7 days') TO STDOUT WITH CSV HEADER" > /tmp/incident-audit.csv
```

**Passo 3: Analisi**

- Esaminare audit log per accessi anomali
- Esaminare log Caddy per richieste sospette
- Esaminare log Keycloak per autenticazioni anomale
- Verificare integrita' dati con checksum

**Passo 4: Remediation**

- Applicare fix specifico per la vulnerabilita'
- Rotazione credenziali (password DB, chiave crittografia, secrets API)
- Re-deploy dell'applicazione
- Riaprire il firewall

### 12.4 Comunicazione alla Scuola

Template di comunicazione per il referente IT della scuola (P1):

```
Oggetto: [MAESTRO] Notifica incidente di sicurezza -- Azione richiesta

Gentile [nome referente IT],

Vi informiamo che il [data], alle ore [ora], abbiamo rilevato un incidente
di sicurezza sulla piattaforma MAESTRO.

Tipo di incidente: [descrizione sintetica]
Dati potenzialmente coinvolti: [tipologia -- es. "nomi e cognomi studenti"]
Studenti potenzialmente coinvolti: [numero]
Azioni gia' intraprese: [elenco]
Stato attuale: [contenuto / in analisi / risolto]

Azioni richieste da parte della scuola:
- [azione 1]
- [azione 2]

Prossimo aggiornamento: entro [data/ora]

Cordiali saluti,
[nome], Security Engineer
Progetto MAESTRO
```

---

## 13. Limiti MVP e Roadmap V1

### 13.1 Cosa NON Copre il MVP

| Area | Non incluso nel MVP | Previsto per V1 |
|---|---|---|
| **Pen-test** | Nessun pen-test formale. Test manuali e automatici di base. | Pen-test con scope definito, report, remediation |
| **WAF** | Nessun Web Application Firewall. Rate limiting in Caddy. | WAF (ModSecurity o Cloudflare, EU-hosted) |
| **IDS/IPS** | Nessun Intrusion Detection/Prevention. Solo fail2ban per SSH. | OSSEC o equivalente host-based IDS |
| **Vault** | Chiave crittografia in env var. API keys in env var. | HashiCorp Vault self-hosted per secrets management |
| **SPID** | Autenticazione locale Keycloak. Nessuna integrazione SPID. | SPID tramite identity provider Keycloak |
| **Secrets rotation automatica** | Rotazione manuale ogni 6 mesi. | Vault con rotation policy automatica |
| **Dependency scanning CI** | Controllo manuale periodico. | `pip-audit` + `npm audit` in CI pipeline, bloccante per merge |
| **SIEM** | Nessun Security Information and Event Management. | Integrazione log in Grafana Loki con alert rules |
| **mTLS inter-servizio** | Servizi su localhost, no mTLS. | mTLS tra servizi quando distribuiti su server separati |
| **Network segmentation** | Singolo server, nessuna segmentazione. | VLAN separate per DB, app, monitoring |
| **Backup encryption** | Backup WAL su Scaleway SSE-S3. | Backup crittografati con chiave gestita da Vault |
| **DR test** | Procedura documentata, non testata. | DR test trimestrale con restore completo |

### 13.2 Roadmap V1 Sicurezza

```
V1 (3 scuole, 6 classi, ~180 studenti)
|
+-- Secrets management (Vault self-hosted)
|   +-- Rotazione automatica chiavi DB
|   +-- Rotazione automatica API keys LLM
|   +-- Dynamic database credentials
|
+-- Pen-test formale
|   +-- Scope: API + dashboard + mobile app
|   +-- Target: no critical, <=3 high con piano remediation
|   +-- Frequenza: annuale
|
+-- CI/CD security
|   +-- pip-audit + npm audit bloccanti
|   +-- SAST (Bandit per Python, ESLint security plugin per TS)
|   +-- Container image scanning (Trivy)
|   +-- Secret detection (git-leaks)
|
+-- Infrastruttura
|   +-- WAF (ModSecurity o equivalente EU)
|   +-- IDS host-based (OSSEC)
|   +-- Network segmentation (VLAN)
|   +-- mTLS tra servizi
|
+-- Auth avanzata
|   +-- SPID integration via Keycloak IdP
|   +-- SSO con registro elettronico (SAML 2.0)
|   +-- WebAuthn/Passkey per docenti
|
+-- Monitoring sicurezza
|   +-- SIEM in Grafana Loki
|   +-- Alert automatici per anomalie (login da IP insoliti, accessi massivi)
|   +-- Dashboard security dedicata
|
+-- DR testato
    +-- Test restore trimestrale
    +-- RTO target: 4 ore
    +-- RPO target: 24 ore (backup WAL continuo)
```

---

## Appendice A: Checklist Implementazione MVP

- [ ] Keycloak realm `maestro` configurato con 3 ruoli e password policy
- [ ] MFA TOTP obbligatorio per ruolo admin
- [ ] 3 client Keycloak configurati (student-app, teacher-dashboard, admin)
- [ ] JWT claims custom `maestro.*` tramite protocol mapper
- [ ] Token lifetime: 1h access, 24h refresh, single-use refresh
- [ ] Middleware RBAC FastAPI con `require_role()` e `require_own_data_or_role()`
- [ ] pgcrypto: funzioni `core.encrypt_pii()` / `core.decrypt_pii()` create
- [ ] Chiave crittografia in variabile d'ambiente, mai nel codice
- [ ] Caddy configurato con TLS 1.3, HSTS, security headers
- [ ] Certificati Let's Encrypt automatici
- [ ] LLM Gateway: pseudonimizzazione bidirezionale implementata
- [ ] LLM Gateway: verifica post-pseudonimizzazione (fail-closed)
- [ ] Trigger `deny_modify()` su tutte le tabelle di audit
- [ ] 3 DB roles creati con GRANT minimali
- [ ] Pydantic validation su tutti gli endpoint
- [ ] CSP headers nella dashboard Next.js
- [ ] Firewall Hetzner: solo porte 80, 443, 22 (IP-restricted)
- [ ] SSH key-only, root login disabilitato
- [ ] fail2ban per SSH e Caddy
- [ ] Automatic security updates abilitati
- [ ] Scaleway S3: public access disabilitato, SSE abilitato
- [ ] Audit log: eventi completi loggati (lista sezione 7.2)
- [ ] Audit log: export API per admin
- [ ] Audit log: partitioning mensile con pg_partman
- [ ] Procedura incident response documentata e condivisa con il team

---

*Documento versione 1.0. Task T3.5. Soggetto a revisione da parte di MSTR-02 (CTA), MSTR-12 (DevOps), MSTR-16 (Privacy & Compliance).*
