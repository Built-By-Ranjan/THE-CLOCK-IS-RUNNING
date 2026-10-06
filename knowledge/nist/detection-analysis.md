**The Clock Is Running - Incident Response Helper Phase 2 — Detection & Analysis** 

### **Backend / AI Implementation Documentation** 

Phase 2 - Detection & Analysis 

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

Supplied Phase 2 Functional Specification 

Operational workflow, phase entry/exit, human review, state transitions, AI contracts, evidence 

references, acceptance criteria and backend behaviour. 

Project implementation design 

API endpoints, backend function names, PostgreSQL storage, Gemini/API assistance, Git-versioned 

Markdown knowledge base and controlled AI/backend separation. 

# **Function -> Source -> Backend/API Code Mapping** 

Function 

Source / where taken from 

Backend function 

API / code reference Detection Intake 

Supplied Phase 2 Functional Specification §1.1; alert/signal intake, raw-source preservation and stable incident ID. intake_detection() POST /api/alerts/intake; POST /api/incidents; POST /api/incidents/{id}/alerts Normalization and Triage Supplied Phase 2 Functional Specification §1.2; 

normalization into common fields while preserving raw observations. normalize_and_triage() POST /api/incidents/{id}/n ormalize; GET /api/inciden ts/{id}/observations Analysis and Correlation Supplied Phase 2 Functional Specification §1.3 and feature matrix; deterministic correlation, timeline and ATT&CK; candidates. analyze_and_correlate() POST /api/incidents/{id}/c orrelate; POST /api/incide nts/{id}/analysis; POST /a pi/incidents/{id}/attack-m appings Severity and Scope Supplied Phase 2 Functional Specification §1.4; structured severity, affected scope and evidence-backed responder decision. review_severity_and_scop e() POST /api/incidents/{id}/s everity; GET /api/incidents/{id}/scope Handoff to Phase 3 Supplied Phase 2 Functional Specification §1.5; structured analysis package and explicit responder confirmation. confirm_phase3_handoff() POST /api/incidents/{id}/h andoffs/phase3; POST /api/ incidents/{id}/handoffs/ph 

ase3/confirm 

Source-derived Functional Specification 

The following pages preserve the supplied phase specification content. No project requirement is presented as a direct NIST requirement unless the 

source alignment explicitly says so. 

Page 1 

Functional Specification: Phase 2 - Detection & 

Analysis 

# **Purpose** 

Phase 2 converts incoming security signals into a structured incident record, determines what is known and unknown, correlates indicators, supports ATT&CK mapping, records severity decisions, and prepares a verified handoff to Phase 3. 

# **Scope and Objectives** 

I Preserve original detection data while creating normalized incident fields. 

I Build a chronological, append-only timeline of observations and decisions. 

I Separate verified facts from hypotheses and AI suggestions. 

I Support ATT&CK; mapping with evidence references. 

I Capture severity and scope as explicit, auditable decisions. 

I Produce a structured handoff that Phase 3 can use directly. 

# **System Position in the Four-Phase Flow** 

This document defines the expected system behaviour for this phase. The phase must consume the structured incident state produced by the previous phase, perform only the responsibilities assigned to this phase, record all meaningful state changes in the central incident timeline, and produce a structured output that can be consumed by the next phase. 

The project follows the four-phase incident-response structure used in the supplied challenge and Phase 3 specification: Preparation -> Detection & Analysis -> Containment, Eradication & Recovery -> Post-Incident Activity. The supplied Phase 3 specification requires human review, simulated execution, centralized timeline logging, evidence protection, and explicit phase progression. 

Implementation note: NIST published SP 800-61 Rev. 3 in April 2025 and it supersedes Rev. 2. The challenge material, however, explicitly asks the project to use the NIST four-phase structure; therefore this project documentation keeps that four-phase structure for consistency with the supplied problem statement and existing Phase 3 document. 

# **Phase Entry / Exit Contract** 

Item 

Requirement Entry 

Incident exists with a unique incident ID and the minimum required metadata for this phase. Processing 

The platform evaluates the incident using deterministic rules plus AI assistance where configured. 

Human control 

AI recommendations are advisory. A responder remains responsible for confirmation, edits, rejection, and phase advancement. 

Audit 

Every meaningful action, recommendation decision, evidence change, and status transition creates a timeline event. 

Exit 

A structured phase-complete record is created only when required checks are satisfied. 

### Page 2 

### 1. Operational Workflow & System Behaviour 

## **1.1 Detection Intake** 

Detection & Analysis begins when a signal, alert, user report, or other incident indicator enters the platform. The system creates or links the signal to an incident record, preserves the original source information, and assigns a stable incident ID. 

## **1.2 Normalization and Triage** 

Incoming data is normalized into common fields such as source, timestamp, affected asset, user/account, indicator type, severity hints, and raw reference. The platform should separate raw observations from analyst conclusions so that later reasoning can be traced back to evidence. 

## **1.3 Analysis and Correlation** 

The system groups related indicators, checks available playbooks, maps relevant observations to ATT&CK techniques where supported, and builds an incident timeline. AI may summarize patterns and propose hypotheses, but hypotheses must remain clearly distinct from verified facts. 

## **1.4 Severity and Scope** 

The responder reviews affected assets, accounts, services, and business impact. The platform records severity as a structured 

value and stores the reason/evidence supporting the decision. If the evidence is incomplete, the incident can remain in an analysis state. 

## **1.5 Handoff to Phase 3** 

When the incident has sufficient verified information for response planning, the platform produces a structured analysis package: incident summary, confirmed indicators, affected assets, current severity, evidence references, ATT&CK mappings, unresolved questions, and recommended containment actions. The responder explicitly confirms the handoff. 

2. Feature Matrix & MVP Scope 

Feature / Component 

Operational Purpose 

Backend / MVP Behaviour 

Detection Intake 

Creates or updates incidents from alerts and reports. 

Accept structured alert payload; preserve raw source 

reference. 

Indicator Normalization 

Creates consistent fields for analysis. 

Normalize IP/domain/hash/user/host/event types without 

deleting source values. 

Timeline Builder 

Maintains chronological incident history. 

Append timestamped events; distinguish observed vs 

analyst/AI-derived information. 

Correlation Engine 

Groups related observations. 

Link indicators to incident/assets/accounts using deterministic 

rules and confidence metadata. 

AI Analysis Assistant 

Produces structured summaries and hypotheses. 

Return schema-valid summary, likely phase, severity 

considerations, ATT&CK candidates and next actions. 

Severity Review 

Captures responder assessment. 

Store severity, rationale, reviewer, timestamp and supporting 

evidence refs. 

Phase 3 Handoff 

Packages analysis for 

containment/eradication/recovery. 

Generate structured handoff object and require explicit 

responder confirmation. 

3. Required State Model 

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

### COMPLETE 

Phase requirements have been confirmed. 

COMPLETE -> next phase 

### RETURNED 

Review found missing, invalid, or conflicting information. 

RETURNED -> IN_PROGRESS 

Important: phase advancement must not be inferred only from an AI response. The backend should enforce required conditions and preserve an explicit responder confirmation, consistent with the supplied Phase 3 manual phase gate. 

Page 3 

4. Data Model & AI Contract 

## **4.1 Minimum Data Objects** 

Object Minimum fields 

# **Purpose** 

Alert 

alert_id, source, observed_at, raw_ref, normalized_type Original detection input. Indicator indicator_id, type, value_ref, first_seen, last_seen Structured observable used in analysis. Asset asset_id, hostname, service, owner, criticality Affected or related system context. AnalysisFinding 

finding_id, statement, evidence_refs, confidence, author_type Separates findings from raw observations. SeverityDecision severity, rationale, decided_by, decided_at 

Auditable severity decision. 

## **4.2 AI Input / Output Contract** 

The AI layer should receive normalized incident context rather than raw UI text. The prompt/context builder should provide only the fields needed for the current phase, together with previous verified timeline events and evidence references. The model output must be machine-readable so the backend can validate it before displaying it. 

onsiderations":["..."],"attack_mappings":[{"technique_id":"...","evidence_refs":[]}],"next_actions":["..."]} 

## **4.3 Output Rules** 

I Never convert an AI hypothesis into a confirmed fact automatically. 

I Every ATT&CK; mapping must include evidence references or be explicitly marked as a candidate mapping. 

I Severity recommendations are advisory; the backend stores the responder’s final severity decision separately. 

I The phase handoff must contain enough structured context for Phase 3 to generate containment/eradication/recovery tasks without rereading raw alert text. 

## **4.4 Timeline Event Requirements** 

Every event should be append-only and attributable to either a human responder, the application, or the AI recommendation layer. 

The supplied Phase 3 design uses structured timeline events and treats the audit timeline as the central record for responder actions and compliance reporting. 

Recommended fields: event_id, incident_id, timestamp_utc, actor_type, actor_id, phase, event_type, action_code, status, description, evidence_refs, previous_state, new_state, and correlation_id. "recommended_phase3_actions":["..."]},"human_review_required":true} 

{"phase":"DETECTION_ANALYSIS","incident":{},"observations":[],"timeline":[],"available_playbooks":[]} 

{"summary":"...","confirmed_facts":["..."], 

"hypotheses":[{"statement":"...","confidence":"LOW|MEDIUM|HIGH","evidence_refs":[]}], 

"severity_considerations":["..."], 

"attack_mappings":[{"technique_id":"...","evidence_refs":[]}],"next_actions":["..."]} 

{"handoff":{"ready":false,"blocking_questions":["..."], 

"recommended_phase3_actions":["..."]},"human_review_required":true} 

Page 4 

### 5. Examples, Edge Cases & Acceptance Criteria 

## **5.1 Concrete Examples** 

Example A - Suspicious PowerShell activity: The alert is normalized with host, user, timestamp and command reference. The AI identifies a possible PowerShell-related ATT&CK technique and explains which observed fields support the candidate mapping. The responder confirms or rejects the mapping. 

Example B - Multiple related alerts: Five alerts referencing the same host and account are linked to one incident. The timeline preserves each original event and the correlation decision. The system does not delete the underlying alerts. Example C - Incomplete evidence: An alert suggests account compromise but there is no verified authentication 

evidence. The incident remains under analysis, the missing evidence is listed, and no containment action is marked as completed. 

## **5.2 Edge Cases** 

I Duplicate alert arrives -> link it to the existing incident while preserving the original alert record. 

I Timestamp is missing or inconsistent -> preserve the raw timestamp and flag normalization uncertainty. 

I AI suggests an ATT&CK; technique without supporting evidence -> store it as CANDIDATE, not VERIFIED. 

I Severity changes after new evidence -> preserve both decisions with timestamps and rationale. 

I One incident affects multiple assets -> maintain separate asset references rather than flattening them into one text field. 

## **5.3 Acceptance Criteria** 

I Every incident has a stable ID and every source alert can be traced back to that incident. 

I Raw observations remain distinguishable from analysis findings. 

I Timeline events are append-only and ordered by UTC timestamp plus event ID. 

I AI output validates against the defined schema before being stored or shown as structured data. 

I A responder can review and explicitly approve the Phase 3 handoff. 

I The handoff contains evidence references, severity, affected assets, candidate/verified ATT&CK; mappings, and unresolved questions. 

### 6. Implementation Notes for Backend Team 

I Store raw alert payloads separately from normalized incident fields so the source is never overwritten. 

I Use PostgreSQL for incident, alert, indicator, timeline, evidence-reference and decision records. 

I Expose a single analysis context object to the AI layer to reduce prompt ambiguity and improve reproducibility. 

I Use deterministic correlation rules first; use AI to explain, summarize and suggest relationships rather than silently changing links. 

I Keep evidence references stable even if an evidence file is moved in storage. 

### 7. Source Alignment 

Primary project source: supplied Phase 3 Functional Specification, which defines the project’s operational style: automated trigger, human review, simulated execution, central audit timeline, evidence protection, and manual phase gate. Challenge source: the supplied Problem Statement 27, “The Clock Is Running,” which asks for an assistant that suggests steps structured by the NIST four phases, maintains a timeline, drafts a compliance-ready incident report, maps actions to ATT&CK, preserves evidence-chain information, and flags regulatory notification triggers. 

NIST reference: SP 800-61 Rev. 2 describes the four-phase incident-handling lifecycle used in the supplied challenge; SP 800-61 Rev. 3 is the current NIST revision and supersedes Rev. 2. The project should document its chosen version explicitly in the implementation repository. 

