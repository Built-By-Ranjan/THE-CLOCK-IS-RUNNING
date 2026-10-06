**The Clock Is Running - Incident Response Helper Phase 1 — Preparation** 

**Backend / AI Implementation Documentation** 

Phase 1 - Preparation 

Submission-ready backend / AI implementation documentation 

# **NIST Version / Revision Note** 

Current NIST reference: NIST SP 800-61 Rev. 3 (published April 2025; it supersedes Rev. 2). The supplied challenge and project documents retain 

the earlier four-phase lifecycle for project consistency. Therefore, the four-phase structure in this document is a project/challenge structure aligned to 

the supplied NIST lifecycle framing; the FastAPI, PostgreSQL, Gemini API, Git knowledge base and endpoint design are project implementation 

choices, not direct NIST requirements. 

# **Source Alignment - Where the content comes from** 

Source 

What is taken from it 

NIST SP 800-61 Rev. 2 (as used by the 

supplied challenge) 

Four-phase incident-handling lifecycle framing retained by the project: Preparation; Detection & Analysis; Containment, Eradication & Recovery; Post-Incident Activity. 

NIST SP 800-61 Rev. 3 (current) 

Current NIST revision/version reference. Rev. 3 supersedes Rev. 2; this document records that distinction 

explicitly. 

Problem Statement 27 - “The Clock Is 

Running” 

Project-level requirements such as phase-structured assistance, timeline, compliance-ready reporting, 

ATT&CK; mapping, evidence-chain information and regulatory-trigger flagging. 

Supplied Phase 3 Functional Specification 

Operational workflow, phase entry/exit, human review, state transitions, AI contracts, evidence 

references, acceptance criteria and backend behaviour. 

Project implementation design 

API endpoints, backend function names, PostgreSQL storage, Gemini/API assistance, Git-versioned 

Markdown knowledge base and controlled AI/backend separation. 

# **Function -> Source -> Backend/API Code Mapping** 

Function 

Source / where taken from 

Backend function 

API / code reference Preparation Trigger 

Supplied Phase 1 Functional Specification §1.1; aligned to the preparation/readiness phase structure retained by 

the supplied challenge. preparation_trigger() GET /api/incidents/{incide nt_id}/preparation; POST / api/incidents/{incident_id }/preparation/check Readiness Assessment Supplied Phase 1 Functional Specification §1.2 and its readiness checklist/profile requirements. evaluate_readiness() GET /api/incidents/{incide nt_id}/readiness; POST /ap i/incidents/{incident_id}/ readiness/evaluate Playbook and Scenario Preparation Supplied Phase 1 Functional Specification §1.3; playbook examples and versioning requirements. prepare_playbook() GET /api/playbooks?type={i ncident_type}; POST /api/playbooks; POST /api/ playbooks/{id}/versions Evidence Readiness Supplied Phase 1 Functional Specification §1.4; evidence metadata, hash and custody requirements. validate_evidence_readin ess() GET /api/evidence/policy; POST /api/incidents/{incid ent_id}/readiness/evidence Phase Completion Supplied Phase 1 Functional Specification §1.5; readiness completion and explicit responder acceptance of documented gaps. complete_preparation_pha se() POST /api/incidents/{incid ent_id}/phases/preparation /complete 

Source-derived Functional Specification 

The following pages preserve the supplied phase specification content. No project requirement is presented as a direct NIST requirement unless the 

source alignment explicitly says so. 

Page 1 

Functional Specification: Phase 1 - Preparation 

# **Purpose** 

Phase 1 establishes the operational readiness required before and around incident handling. It prepares the people, procedures, playbooks, evidence controls, notification rules, knowledge base, and system configuration that later phases depend on. 

# **Scope and Objectives** 

I Establish the incident-response baseline before an incident requires it. 

I Maintain reusable, versioned playbooks and response scenarios. 

I Define evidence-handling and chain-of-custody expectations before evidence is collected. 

I Define notification and escalation rules so later phases can evaluate them consistently. 

I Provide a readiness checklist that the backend can evaluate deterministically. 

I Produce a structured handoff context for Detection & Analysis. 

# **System Position in the Four-Phase Flow** 

This document defines the expected system behaviour for this phase. The phase must consume the structured incident state 

produced by the previous phase, perform only the responsibilities assigned to this phase, record all meaningful state changes in the central incident timeline, and produce a structured output that can be consumed by the next phase. 

The project follows the four-phase incident-response structure used in the supplied challenge and Phase 3 specification: Preparation -> Detection & Analysis -> Containment, Eradication & Recovery -> Post-Incident Activity. The supplied Phase 3 specification requires human review, simulated execution, centralized timeline logging, evidence protection, and explicit phase progression. 

Implementation note: NIST published SP 800-61 Rev. 3 in April 2025 and it supersedes Rev. 2. The challenge material, however, explicitly asks the project to use the NIST four-phase structure; therefore this project documentation keeps that four-phase structure for consistency with the supplied problem statement and existing Phase 3 document. 

# **Phase Entry / Exit Contract** 

Item Requirement Entry 

Incident exists with a unique incident ID and the minimum required metadata for this phase. 

Processing Human control 

The platform evaluates the incident using deterministic rules plus AI assistance where configured. 

AI recommendations are advisory. A responder remains responsible for confirmation, edits, rejection, and phase advancement. 

### Audit 

Every meaningful action, recommendation decision, evidence change, and status transition creates a timeline event. Exit 

A structured phase-complete record is created only when required checks are satisfied. 

### Page 2 

### 1. Operational Workflow & System Behaviour 

## **1.1 Preparation Trigger** 

Preparation is the baseline readiness state. The system should make required response resources, playbooks, evidence-handling rules, notification rules, and incident metadata available before an incident requires them. Preparation may also be revisited after lessons learned or configuration changes. 

## **1.2 Readiness Assessment** 

When a new incident workspace is created, the platform checks whether the required response profile is available: incident categories, severity rules, contact/escalation data, playbooks, evidence storage, audit logging, notification rules, ATT&CK mapping references, and report templates. Missing items are shown as readiness gaps rather than silently assumed to exist. 

## **1.3 Playbook and Scenario Preparation** 

The platform stores reusable playbooks for common incident types such as phishing, brute-force activity, PowerShell abuse, malware, and denial-of-service. A playbook contains ordered tasks, prerequisites, expected evidence, responsible role, and completion criteria. Playbooks are versioned so that an incident can be traced to the exact version used. 

## **1.4 Evidence Readiness** 

The evidence subsystem must be available before active response. Evidence records should support a unique evidence ID, source, acquisition time, hash where applicable, owner/custodian, storage reference, and chain-of-custody events. Preparation does not invent evidence; it defines how future evidence will be captured and protected. 

## **1.5 Phase Completion** 

Preparation is complete when the minimum readiness checklist passes or a responder explicitly accepts documented gaps. The 

system creates a phase-complete timeline event and makes the prepared configuration available to Detection & Analysis. 

2. Feature Matrix & MVP Scope 

Feature / Component 

Operational Purpose 

Backend / MVP Behaviour 

Incident Readiness Profile 

Stores the minimum configuration needed to respond 

consistently. 

Create/read/update readiness profile; show READY / 

INCOMPLETE status. 

Playbook Library 

Provides reusable response procedures. 

Versioned Markdown/structured playbooks with incident type, 

tasks, prerequisites and outputs. 

Evidence Configuration 

Defines how evidence will be captured and protected. 

Evidence metadata schema, storage reference, hash field, 

custody events. 

### Notification Rules 

Defines conditions that require escalation or 

regulatory review. 

Rule records with trigger condition, deadline, owner and 

status. 

### ATT&CK Reference Mapping 

Makes technique mapping available to later analysis 

and reporting. 

Store technique IDs/descriptions and allow playbook tasks to 

reference them. 

### Readiness Checklist 

Prevents missing prerequisites from being hidden. 

Checklist with PENDING / VERIFIED / BLOCKED states. 

### Audit Timeline 

Provides an auditable record of preparation changes. 

Append-only event records for configuration and checklist 

decisions. 

### 3. Required State Model 

State 

Meaning 

Allowed transition 

### OPEN 

Incident is active and awaiting phase work. 

OPEN -> phase-specific processing 

IN_PROGRESS 

Responder or system is actively working on tasks. 

IN_PROGRESS -> READY_FOR_REVIEW 

READY_FOR_REVIEW 

Required tasks/results are present and awaiting human confirmation. 

READY_FOR_REVIEW -> COMPLETE / 

### RETURNED 

COMPLETE 

Phase requirements have been confirmed. 

COMPLETE -> next phase 

### RETURNED 

Review found missing, invalid, or conflicting information. 

RETURNED -> IN_PROGRESS 

Important: phase advancement must not be inferred only from an AI response. The backend should enforce required conditions and preserve an explicit responder confirmation, consistent with the supplied Phase 3 manual phase gate. 

Page 3 

4. Data Model & AI Contract 

## **4.1 Minimum Data Objects** 

Object 

Minimum fields 

# **Purpose** 

Incident 

incident_id, type, severity, created_at, status 

Stable identity and high-level case context. 

Playbook 

playbook_id, version, type, tasks, owner, updated_at 

Versioned response procedure. 

ReadinessCheck 

check_id, incident_id, item, status, verified_by, verified_at 

Tracks readiness prerequisites. 

NotificationRule 

rule_id, trigger, deadline, jurisdiction, owner, active 

Stores notification trigger logic. 

EvidencePolicy 

policy_id, hash_required, custody_required, retention 

Defines evidence-handling expectations. 

## **4.2 AI Input / Output Contract** 

The AI layer should receive normalized incident context rather than raw UI text. The prompt/context builder should provide only the fields needed for the current phase, together with previous verified timeline events and evidence references. The model output must be machine-readable so the backend can validate it before displaying it. 

ps":["..."],"assumptions":[]} 

## **4.3 Output Rules** 

I AI may identify missing preparation items and recommend a playbook, but it must not mark a prerequisite as verified unless the 

backend has a corresponding verified record. 

I Recommendations should include reason, source record, priority, and expected evidence/result where applicable. 

I All checklist and configuration changes must be timestamped and attributable to a user or service. 

I A preparation summary should be reusable as context for Detection & Analysis. 

## **4.4 Timeline Event Requirements** 

Every event should be append-only and attributable to either a human responder, the application, or the AI recommendation layer. 

The supplied Phase 3 design uses structured timeline events and treats the audit timeline as the central record for responder 

actions and compliance reporting. 

Recommended fields: event_id, incident_id, timestamp_utc, actor_type, actor_id, phase, event_type, action_code, status, 

description, evidence_refs, previous_state, new_state, and correlation_id. 

{"phase":"PREPARATION","incident_type":"","context":{},"known_assets":[],"available_playbooks":[]} 

{"required_checks":[{"check_id":"...","reason":"...","priority":"HIGH"}], 

"recommended_playbooks":[{"playbook_id":"...","reason":"..."}],"gaps":["..."], 

"assumptions":[]} 

{"next_phase_ready":false,"blocking_items":["..."],"human_review_required":true} 

Page 4 

### 5. Examples, Edge Cases & Acceptance Criteria 

## **5.1 Concrete Examples** 

Example A - New banking phishing incident: The system selects the phishing response profile, checks that the evidence 

policy and notification rules exist, and presents the responder with the preparation checklist. If the playbook is missing, the incident remains blocked for that item rather than pretending the playbook exists. 

Example B - Evidence configuration: A responder verifies that the evidence store is available and that hash/custody fields 

are enabled. The system records a READINESS_CHECK_VERIFIED event with the responder identity and timestamp. 

Example C - Notification readiness: A regulatory notification rule is configured with a trigger condition and deadline. The 

system stores the rule as configuration; it does not claim that the notification clock has started until an actual incident event satisfies the trigger. 

## **5.2 Edge Cases** 

I No playbook matches the incident type -> show an explicit gap and allow a responder to create/select a fallback procedure. 

I Required configuration is unavailable -> block only the dependent workflow and record the reason. 

I Two playbook versions exist -> bind the incident to one explicit version and preserve that version ID. 

I AI recommends a check that has already been verified -> do not duplicate the check; reference the existing verification event. 

I A readiness record is edited after an incident begins -> preserve the previous version and record the change in the timeline. 

## **5.3 Acceptance Criteria** 

I A newly created incident can retrieve its preparation profile deterministically. 

I Every readiness check has a stable ID and explicit status. 

I The backend can distinguish VERIFIED, PENDING, and BLOCKED without parsing natural-language AI output. 

I Playbook versions are immutable once attached to an active incident. 

I Preparation completion produces a structured event consumable by the next phase. 

I The AI response is schema-valid and rejected safely when required fields are missing. 

### 6. Implementation Notes for Backend Team 

I Keep playbooks in the project’s Git-versioned Markdown knowledge base and store a stable playbook/version reference in PostgreSQL. 

I Expose preparation data through explicit API endpoints rather than requiring the AI layer to read database tables directly. 

I Use UTC timestamps internally and convert to local display time only at the UI layer. 

I Use deterministic backend validation for readiness and phase advancement; use Gemini/API output only for recommendations and summarization. 

I Design the schema so later phases can reference preparation records without copying their full content. 

### 7. Source Alignment 

Primary project source: supplied Phase 3 Functional Specification, which defines the project’s operational style: automated trigger, human review, simulated execution, central audit timeline, evidence protection, and manual phase gate. Challenge source: the supplied Problem Statement 27, “The Clock Is Running,” which asks for an assistant that suggests steps structured by the NIST four phases, maintains a timeline, drafts a compliance-ready incident report, maps actions to ATT&CK, preserves evidence-chain information, and flags regulatory notification triggers. 

NIST reference: SP 800-61 Rev. 2 describes the four-phase incident-handling lifecycle used in the supplied challenge; SP 800-61 Rev. 3 is the current NIST revision and supersedes Rev. 2. The project should document its chosen version explicitly in the implementation repository. 

