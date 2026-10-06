# Database Schema: THE CLOCK IS RUNNING

The application is backed by PostgreSQL using SQLAlchemy ORM with timezone-aware UTC timestamps (`UTCDateTime`).

---

## Implemented Core Tables

### 1. `users`
- `id` (Integer, Primary Key)
- `username` (VARCHAR(100), Unique, Indexed)
- `email` (VARCHAR(255), Unique, Indexed)
- `hashed_password` (VARCHAR(255), Bcrypt hash)
- `is_active` (Boolean, Default: True)
- `mfa_enabled` (Boolean, Default: False)
- `encrypted_mfa_secret` (VARCHAR(500), Fernet-encrypted TOTP secret; never plaintext)
- `created_at` (TIMESTAMPTZ, UTC)
- `updated_at` (TIMESTAMPTZ, UTC)

### 2. `incidents`
- `id` (Integer, Primary Key)
- `title` (VARCHAR(255))
- `description` (TEXT)
- `attack_type` (VARCHAR(100)) - e.g., "Brute Force", "Phishing"
- `status` (VARCHAR(50)) - "Open", "Under Investigation", "Contained", "Eradicated", "Recovered", "Closed"
- `priority` (VARCHAR(10)) - "P1", "P2", "P3", "P4"
- `source` (VARCHAR(100)) - "simulator", "system", "human", "AI"
- `current_nist_phase` (VARCHAR(100)) - "Preparation", "Detection & Analysis", "Containment, Eradication & Recovery", "Post-Incident Activity"
- `detected_at` (TIMESTAMPTZ, UTC)
- `deadline_at` (TIMESTAMPTZ, UTC) - Computed backend rule: `detected_at + 72 hours`
- `created_at` (TIMESTAMPTZ, UTC)
- `updated_at` (TIMESTAMPTZ, UTC)

### 3. `indicators`
- `id` (Integer, Primary Key)
- `incident_id` (Integer, Foreign Key `incidents.id` ON DELETE CASCADE)
- `type` (VARCHAR(50)) - "IP", "Domain", "URL", "Email", "File Hash", "Username", "Process", "Command", "Other"
- `value` (VARCHAR(500))
- `description` (TEXT, Nullable)
- `source` (VARCHAR(100))
- `created_at` (TIMESTAMPTZ, UTC)
- `updated_at` (TIMESTAMPTZ, UTC)

### 4. `timeline_events`
- `id` (Integer, Primary Key)
- `incident_id` (Integer, Foreign Key `incidents.id` ON DELETE CASCADE)
- `timestamp` (TIMESTAMPTZ, UTC)
- `event` (VARCHAR(255))
- `actor` (VARCHAR(100))
- `source` (VARCHAR(50)) - "simulator", "system", "human", "AI"
- `description` (TEXT)
- `previous_value` (TEXT, Nullable)
- `new_value` (TEXT, Nullable)

### 5. `nist_history`
- `id` (Integer, Primary Key)
- `incident_id` (Integer, Foreign Key `incidents.id` ON DELETE CASCADE)
- `phase` (VARCHAR(100))
- `timestamp` (TIMESTAMPTZ, UTC)
- `actor` (VARCHAR(100))
- `rationale` (TEXT, Nullable)

### 6. `incident_assets`
- `id` (Integer, Primary Key)
- `incident_id` (Integer, Foreign Key `incidents.id` ON DELETE CASCADE)
- `asset_name` (VARCHAR(255))
- `asset_type` (VARCHAR(100), Nullable)
- `description` (TEXT, Nullable)
- `added_at` (TIMESTAMPTZ, UTC)

### 7. `incident_users`
- `id` (Integer, Primary Key)
- `incident_id` (Integer, Foreign Key `incidents.id` ON DELETE CASCADE)
- `username` (VARCHAR(100))
- `email` (VARCHAR(255), Nullable)
- `department` (VARCHAR(100), Nullable)
- `impact` (TEXT, Nullable)
- `added_at` (TIMESTAMPTZ, UTC)

### 8. `evidence`
- `id` (Integer, Primary Key)
- `incident_id` (Integer, Foreign Key `incidents.id` ON DELETE CASCADE)
- `type` (VARCHAR(100))
- `name` (VARCHAR(255))
- `source` (VARCHAR(100))
- `collected_at` (TIMESTAMPTZ, UTC)
- `collector` (VARCHAR(100))
- `sha256` (VARCHAR(64), Nullable)
- `status` (VARCHAR(50), Default: "collected")
- `details` (TEXT, Nullable)
- `created_at` (TIMESTAMPTZ, UTC)

---

## Reserved for Future Intelligence Integrations
The following tables are planned for subsequent AI integration phases:
- `ai_analyses`
- `attack_mappings`
- `reports`
- `report_versions`
