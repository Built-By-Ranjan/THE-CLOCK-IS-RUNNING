# API Contract: THE CLOCK IS RUNNING

The interactive OpenAPI/Swagger documentation is served at `/docs` (and ReDoc at `/redoc`).
The OpenAPI JSON schema is available at `/openapi.json`.

---

## 1. System & Health

### `GET /health`
- **Description:** Verifies service availability.
- **Authentication:** None
- **Request:** None
- **Response (200 OK):**
  ```json
  {
    "status": "ok"
  }
  ```

---

## 2. Authentication & MFA

### `POST /auth/register`
- **Description:** Registers a new local analyst account with bcrypt-hashed credentials.
- **Authentication:** None
- **Request Body (JSON):**
  ```json
  {
    "username": "analyst1",
    "email": "analyst1@defense.internal",
    "password": "SecurePassword123!"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "id": 1,
    "username": "analyst1",
    "email": "analyst1@defense.internal",
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2026-10-06T08:00:00Z"
  }
  ```
- **Status Codes:** `201 Created`, `409 Conflict` (username or email taken), `422 Unprocessable Entity`.

### `POST /auth/login`
- **Description:** Authenticates user and issues a signed JWT Bearer token. If MFA is active, an OTP code is required.
- **Authentication:** None
- **Request Body (JSON):**
  ```json
  {
    "username": "analyst1",
    "password": "SecurePassword123!",
    "otp_code": "123456" // Required only if mfa_enabled is true
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "analyst1",
      "email": "analyst1@defense.internal",
      "is_active": true,
      "mfa_enabled": true,
      "created_at": "2026-10-06T08:00:00Z"
    }
  }
  ```
- **Status Codes:** `200 OK`, `401 Unauthorized` (bad credentials or missing/invalid OTP), `403 Forbidden` (inactive account).

### `GET /auth/me`
- **Description:** Returns profile information for the authenticated user.
- **Authentication:** Bearer Token (`Authorization: Bearer <token>`)
- **Request:** None
- **Response (200 OK):** `UserResponse`
- **Status Codes:** `200 OK`, `401 Unauthorized`.

### `POST /auth/mfa/setup`
- **Description:** Generates a new TOTP base32 secret and provisioning URI. The secret is encrypted before storage.
- **Authentication:** Bearer Token
- **Request:** None
- **Response (200 OK):**
  ```json
  {
    "secret": "JBSWY3DPEHPK3PXP",
    "provisioning_uri": "otpauth://totp/THE%20CLOCK%20IS%20RUNNING:analyst1@defense.internal?secret=JBSWY3DPEHPK3PXP&issuer=THE%20CLOCK%20IS%20RUNNING"
  }
  ```
- **Status Codes:** `200 OK`, `401 Unauthorized`.

### `POST /auth/mfa/enable`
- **Description:** Verifies an OTP code against the configured secret and activates MFA for the account.
- **Authentication:** Bearer Token
- **Request Body (JSON):**
  ```json
  {
    "otp_code": "654321"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "MFA has been successfully enabled.",
    "mfa_enabled": true
  }
  ```
- **Status Codes:** `200 OK`, `400 Bad Request` (invalid OTP or MFA not setup), `401 Unauthorized`.

### `POST /auth/mfa/disable`
- **Description:** Disables MFA upon verification of current OTP or password.
- **Authentication:** Bearer Token
- **Request Body (JSON):**
  ```json
  {
    "otp_code": "654321",
    "password": "SecurePassword123!"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "MFA has been disabled.",
    "mfa_enabled": false
  }
  ```
- **Status Codes:** `200 OK`, `400 Bad Request`, `401 Unauthorized`.

---

## 3. Incident Management

### `POST /incidents`
- **Description:** Creates an incident. Calculates 72-hour regulatory deadline: `deadline_at = detected_at + 72 hours`. Appends initial audit events and NIST history.
- **Authentication:** Optional (inherits actor identity from JWT if present)
- **Request Body (JSON):**
  ```json
  {
    "title": "Unauthorized Access Attempt",
    "description": "Volumetric anomaly observed on gateway.",
    "attack_type": "Brute Force",
    "priority": "P2", // P1, P2, P3, P4
    "source": "human",
    "current_nist_phase": "Detection & Analysis",
    "detected_at": "2026-10-06T08:30:00Z", // Optional, defaults to UTC now
    "affected_assets": ["auth-server-01"],
    "affected_users": ["admin"]
  }
  ```
- **Response (201 Created):** Full `IncidentResponse` object.
- **Status Codes:** `201 Created`, `422 Unprocessable Entity`.

### `GET /incidents`
- **Description:** Lists incidents with pagination and filtering.
- **Authentication:** None
- **Query Parameters:**
  - `skip` (default 0)
  - `limit` (default 50, max 100)
  - `attack_type` (optional filter)
  - `status` (optional filter: `Open`, `Under Investigation`, `Contained`, `Eradicated`, `Recovered`, `Closed`)
- **Response (200 OK):**
  ```json
  {
    "items": [ /* IncidentResponse objects */ ],
    "total": 1
  }
  ```

### `GET /incidents/{incident_id}`
- **Description:** Retrieves full incident object with indicators, timeline, NIST history, affected assets, affected users, and evidence.
- **Authentication:** None
- **Response (200 OK):** Full `IncidentResponse`
- **Status Codes:** `200 OK`, `404 Not Found`.

### `PATCH /incidents/{incident_id}`
- **Description:** Updates incident fields. Validates lifecycle transitions (`Open` → `Under Investigation` → `Contained` → `Eradicated` → `Recovered` → `Closed`). Audits changes to timeline.
- **Authentication:** Optional
- **Request Body (JSON):**
  ```json
  {
    "title": "Updated Title",
    "status": "Under Investigation",
    "priority": "P1",
    "current_nist_phase": "Containment, Eradication & Recovery",
    "rationale": "Quarantine rules deployed successfully."
  }
  ```
- **Response (200 OK):** Updated `IncidentResponse`
- **Status Codes:** `200 OK`, `400 Bad Request` (illegal state transition), `404 Not Found`, `422 Unprocessable Entity`.

### `DELETE /incidents/{incident_id}`
- **Description:** Deletes incident and cascades associated records.
- **Authentication:** None
- **Response:** `204 No Content`
- **Status Codes:** `204 No Content`, `404 Not Found`.

### `GET /incidents/{incident_id}/clock`
- **Description:** Provides real-time countdown status against the 72-hour regulatory clock.
- **Response (200 OK):**
  ```json
  {
    "detected_at": "2026-10-06T08:30:00+00:00",
    "deadline_at": "2026-10-09T08:30:00+00:00",
    "current_time": "2026-10-06T08:35:00+00:00",
    "remaining_seconds": 258900.0,
    "elapsed_seconds": 300.0,
    "is_expired": false,
    "formatted_remaining": "71h 55m 00s"
  }
  ```

---

## 4. Controlled Simulations

### `POST /simulations/brute-force`
- **Description:** Triggers a safe, controlled Brute Force incident simulation in PostgreSQL. Does NOT perform any actual network attack.
  - Generates safe documentation IP (RFC 5737 TEST-NET-2 `198.51.100.42`), username targets, and command strings.
  - Automatically establishes UTC `detected_at` and computes `deadline_at = detected_at + 72 hours`.
  - Appends timeline events and initializes NIST phase `Detection & Analysis`.
- **Authentication:** Optional
- **Request Body (JSON, Optional):**
  ```json
  {
    "source_ip": "198.51.100.42",
    "target_user": "admin"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "incident_id": 1,
    "attack_type": "Brute Force",
    "status": "Open",
    "detected_at": "2026-10-06T08:30:00+00:00",
    "deadline_at": "2026-10-09T08:30:00+00:00",
    "message": "Controlled Brute Force simulation successfully initiated with Incident ID #1.",
    "incident": { /* IncidentResponse */ }
  }
  ```
- **Status Codes:** `201 Created`.

### `POST /simulations/phishing`
- **Description:** Triggers a safe, controlled Phishing incident simulation in PostgreSQL. Does NOT send external emails.
  - Generates safe domain (`fake-identity-verification.example`), mock landing page URL, email address, and sample SHA-256 payload hash.
  - Automatically establishes UTC `detected_at` and computes `deadline_at = detected_at + 72 hours`.
  - Appends timeline events and initializes NIST phase `Detection & Analysis`.
- **Authentication:** Optional
- **Request Body (JSON, Optional):**
  ```json
  {
    "target_user": "sarah.connor@organization.internal"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "incident_id": 2,
    "attack_type": "Phishing",
    "status": "Open",
    "detected_at": "2026-10-06T08:30:00+00:00",
    "deadline_at": "2026-10-09T08:30:00+00:00",
    "message": "Controlled Phishing simulation successfully initiated with Incident ID #2.",
    "incident": { /* IncidentResponse */ }
  }
  ```
- **Status Codes:** `201 Created`.

---

## 5. Indicators of Compromise (IoC)

### `GET /incidents/{incident_id}/indicators`
- **Description:** Retrieves all indicators for an incident.
- **Allowed Types:** `IP`, `Domain`, `URL`, `Email`, `File Hash`, `Username`, `Process`, `Command`, `Other`.
- **Response (200 OK):** `List[IndicatorResponse]`
- **Status Codes:** `200 OK`, `404 Not Found`.

### `POST /incidents/{incident_id}/indicators`
- **Description:** Adds an indicator and records an "Indicator Added" timeline event.
- **Request Body (JSON):**
  ```json
  {
    "type": "IP",
    "value": "198.51.100.99",
    "description": "Secondary relay IP",
    "source": "firewall"
  }
  ```
- **Response (201 Created):** `IndicatorResponse`
- **Status Codes:** `201 Created`, `404 Not Found`, `422 Unprocessable Entity`.

### `PATCH /incidents/{incident_id}/indicators/{indicator_id}`
- **Description:** Modifies an existing indicator and logs an audit timeline event.
- **Request Body (JSON):**
  ```json
  {
    "value": "198.51.100.100",
    "description": "Updated IP description"
  }
  ```
- **Response (200 OK):** `IndicatorResponse`
- **Status Codes:** `200 OK`, `404 Not Found`.

### `DELETE /incidents/{incident_id}/indicators/{indicator_id}`
- **Description:** Deletes an indicator and logs an "Indicator Removed" timeline event.
- **Response:** `204 No Content`
- **Status Codes:** `204 No Content`, `404 Not Found`.

---

## 6. Timeline / Audit Log

### `GET /incidents/{incident_id}/timeline`
- **Description:** Retrieves the chronological audit events for an incident.
- **Allowed Sources:** `simulator`, `system`, `human`, `AI`.
- **Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "incident_id": 1,
      "timestamp": "2026-10-06T08:30:00+00:00",
      "event": "Incident Detected",
      "actor": "siem-monitor",
      "source": "system",
      "description": "Threshold alert triggered.",
      "previous_value": null,
      "new_value": null
    }
  ]
  ```
- **Status Codes:** `200 OK`, `404 Not Found`.

---

## 7. NIST IR Lifecycle & History

### `GET /incidents/{incident_id}/nist-history`
- **Description:** Retrieves NIST IR phase progression history.
- **Supported Phases:**
  - `Preparation`
  - `Detection & Analysis`
  - `Containment, Eradication & Recovery`
  - `Post-Incident Activity`
- **Response (200 OK):** `List[NISTHistoryResponse]`
- **Status Codes:** `200 OK`, `404 Not Found`.

### `POST /incidents/{incident_id}/nist-phase`
- **Description:** Transitions an incident to a new NIST phase and records rationale and timeline event.
- **Request Body (JSON):**
  ```json
  {
    "phase": "Containment, Eradication & Recovery",
    "rationale": "Compromised credential revoked and bastion firewall rule updated."
  }
  ```
- **Response (200 OK):** `NISTHistoryResponse`
- **Status Codes:** `200 OK`, `400 Bad Request`, `404 Not Found`.

---

## 8. Evidence Metadata

### `GET /incidents/{incident_id}/evidence`
- **Description:** Retrieves all evidence records logged for an incident.
- **Response (200 OK):** `List[EvidenceResponse]`
- **Status Codes:** `200 OK`, `404 Not Found`.

### `POST /incidents/{incident_id}/evidence`
- **Description:** Logs evidence metadata (file type, collector, SHA-256 integrity hash) and writes an audit event to the timeline.
- **Request Body (JSON):**
  ```json
  {
    "type": "Network PCAP",
    "name": "brute_force_traffic.pcap",
    "source": "Suricata IDS",
    "collector": "netsec-admin",
    "sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
    "status": "collected",
    "details": "Raw packets captured during 60-second burst."
  }
  ```
- **Response (201 Created):** `EvidenceResponse`
- **Status Codes:** `201 Created`, `404 Not Found`, `422 Unprocessable Entity`.

---

## 9. Affected Assets & Users

### `POST /incidents/{incident_id}/assets`
- **Description:** Links an affected asset/system to the incident.
- **Request Body (JSON):**
  ```json
  {
    "asset_name": "database-cluster-primary",
    "asset_type": "PostgreSQL Server",
    "description": "Production database receiving elevated queries"
  }
  ```
- **Response (201 Created):** `AssetResponse`
- **Status Codes:** `201 Created`, `404 Not Found`.

### `POST /incidents/{incident_id}/affected-users`
- **Description:** Links an affected user account to the incident.
- **Request Body (JSON):**
  ```json
  {
    "username": "victim.user",
    "email": "victim.user@organization.internal",
    "department": "Engineering",
    "impact": "Account locked due to brute force attempts"
  }
  ```
- **Response (201 Created):** `AffectedUserResponse`
- **Status Codes:** `201 Created`, `404 Not Found`.
