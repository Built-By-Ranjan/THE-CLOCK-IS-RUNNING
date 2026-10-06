**The Clock Is Running - Incident Response Helper Phase 3 — Containment, Eradication & Recovery** 

### **Backend / AI Implementation Documentation** 

Phase 3 - Containment, Eradication & Recovery 

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

Supplied Phase 2 and Phase 4 Functional 

Specifications; Phase 3 specification itself 

defines the phase workflow 

Operational workflow, phase entry/exit, human review, state transitions, AI contracts, evidence 

references, acceptance criteria and backend behaviour. 

Project implementation design 

API endpoints, backend function names, PostgreSQL storage, Gemini/API assistance, Git-versioned 

Markdown knowledge base and controlled AI/backend separation. 

# **Function -> Source -> Backend/API Code Mapping** 

Function 

Source / where taken from 

Backend function 

API / code reference 

Phase 3 Trigger Supplied Phase 3 Functional Specification §1.1; requires explicit Phase 2 handoff confirmation and backend entry validation. validate_phase3_entry() POST /api/incidents/{id}/p hases/3/validate-entry Response Planning Supplied Phase 3 Functional Specification §1.2; structured containment/eradication/recovery tasks from verified findings. generate_response_plan() POST /api/incidents/{id}/r esponse-tasks/generate; GET /api/incidents/{id}/re sponse-tasks Containment Supplied Phase 3 Functional Specification §1.3; proposed/approved/simulated/executed action states. handle_containment_actio n() POST /api/incidents/{id}/a ctions; POST /api/actions/ {action_id}/approve; /simulate; /execute Eradication Supplied Phase 3 Functional Specification §1.4; removal of confirmed cause/persistence with evidence/result. record_eradication_resul t() POST /api/incidents/{id}/e radication-tasks; POST /ap i/actions/{action_id}/resu lt Recovery & Verification Supplied Phase 3 Functional Specification §1.5; recovery checks, evidence and explicit verification. verify_recovery() POST /api/incidents/{id}/r ecovery-checks; POST /api/ recovery-checks/{check_id} 

/verify 

Handoff to Phase 4 

Supplied Phase 3 Functional Specification §1.6; 

structured response handoff and explicit confirmation. 

confirm_phase4_handoff() 

POST /api/incidents/{id}/h 

andoffs/phase4; POST /api/ 

incidents/{id}/handoffs/ph 

ase4/confirm 

### Source-derived Functional Specification 

The following pages preserve the supplied phase specification content. No project requirement is presented as a direct NIST requirement unless the 

source alignment explicitly says so. 

Page 1 

Functional Specification: Phase 3 - Containment, Eradication & 

Recovery 

# **Purpose** 

Phase 3 converts verified analysis findings into controlled response actions, covering containment, eradication, and recovery. It ensures 

response actions are 

planned, reviewed, simulated where appropriate, executed through controlled workflows, evidence is protected, and recovery status is 

verified before progression 

to Post-Incident Activity. 

# **Scope and Objectives** 

I Create structured containment, eradication, and recovery tasks from the verified Phase 2 handoff. 

I Limit ongoing impact or spread while preserving evidence and the incident timeline. 

I Remove confirmed malicious artifacts, persistence, or compromised access identified during analysis. 

I Restore affected systems or services and verify that required recovery conditions are satisfied. 

I Separate AI recommendations from responder approvals, simulations, execution results, and verification. 

I Produce a structured handoff that Phase 4 can consume directly. 

# **System Position in the Four-Phase Flow** 

This document defines the expected system behaviour for this phase. The phase must consume the structured incident state produced 

by the previous phase, 

perform only the responsibilities assigned to this phase, record all meaningful state changes in the central incident timeline, and produce 

a structured output that 

can be consumed by the next phase. 

The project follows the four-phase incident-response structure used in the supplied challenge and existing documentation: Preparation 

-> Detection & Analysis -> 

Containment, Eradication & Recovery -> Post-Incident Activity. The supplied Phase 2 document requires a verified handoff to Phase 3, 

while Phase 4 begins only 

after containment, eradication and recovery reach the required completion state. 

Implementation note: the supplied project documents state that NIST SP 800-61 Rev. 3 supersedes Rev. 2, while the challenge retains 

the four-phase structure 

for consistency. The implementation repository should document the exact NIST revision selected for the project. 

# **Phase Entry / Exit Contract** 

Item 

Requirement 

Entry 

Incident exists with a unique incident ID and Phase 2 has produced verified findings, affected assets, severity, evidence references, and 

unresolved questions. 

### Processing 

The platform evaluates response work using deterministic backend rules plus AI assistance where configured. Human control 

AI recommendations are advisory. A responder remains responsible for confirmation, edits, rejection, simulation, execution authorization, and 

phase advancement. 

### Audit 

Every meaningful action, approval, simulation, evidence change, execution outcome, recovery verification, and status transition creates 

a timeline 

event. 

Exit 

A structured phase-complete record is created only when required containment, eradication, recovery verification, and responder 

confirmation 

conditions are satisfied. 

Page 2 

### 1. Operational Workflow & System Behaviour 

## **1.1 Phase 3 Trigger** 

Containment, Eradication & Recovery begins only after the responder explicitly confirms the Phase 2 handoff. The backend validates 

that the handoff contains 

sufficient verified context to generate response work; AI output alone must not trigger phase progression. 

## **1.2 Response Planning** 

The platform converts confirmed findings into structured response tasks grouped under containment, eradication, and recovery. Each 

task should identify the 

target, objective, responsible role, prerequisites, expected evidence/result, dependencies, and current status. 

## **1.3 Containment** 

Containment limits ongoing impact or spread. Depending on the verified incident, actions may include endpoint isolation, disabling a compromised account, 

blocking an indicator, restricting a service, or applying a temporary network control. Proposed, approved, simulated, and executed actions remain separate states. 

## **1.4 Eradication** 

Eradication removes the confirmed cause or persistence mechanism identified during analysis. Tasks may include removing malicious 

artifacts, rotating 

credentials, deleting persistence, correcting compromised configuration, or applying required remediation. Completion must be 

supported by an outcome or 

evidence reference. 

## **1.5 Recovery & Verification** 

Recovery restores affected assets or services to an approved operating state. The platform records recovery checks, validation 

evidence, residual risk, monitoring 

requirements where applicable, and the responder responsible for verification. 

## **1.6 Handoff to Phase 4** 

When required response work has reached acceptable terminal states, the platform produces a structured Phase 3 handoff containing 

response actions, 

outcomes, evidence references, recovery verification, unresolved items, and residual risk. The responder explicitly confirms the handoff. 

### 2. Feature Matrix & MVP Scope 

Feature / Component 

Operational Purpose 

Backend / MVP Behaviour 

Response Plan 

Creates structured containment, eradication and recovery 

work. 

Generate task records from verified Phase 2 findings and selected playbook 

procedures. 

Containment Actions 

Limits ongoing impact or spread. 

Track target, proposed action, approval, simulation/execution status, outcome 

and evidence refs. 

Eradication Actions 

Removes confirmed malicious cause or persistence. 

Track remediation, prerequisite, owner, completion evidence and result. 

### Recovery Verification 

Confirms restored systems/services operate as expected. 

Store recovery check, status, evidence refs, reviewer and verification 

timestamp. 

Action Simulation 

Allows safe review before execution. 

Record SIMULATED separately; simulation never counts as EXECUTED or COMPLETE. 

Evidence Protection 

Preserves evidence while response changes occur. 

Reference stable evidence IDs and append custody/timeline events; never 

overwrite source evidence. 

Phase 4 Handoff 

Packages response results for post-incident activity. 

Generate structured handoff and require explicit responder confirmation. 

3. Required State Model 

State 

Meaning 

Allowed transition 

OPEN 

Incident is active and awaiting phase work. 

OPEN -> phase-specific processing 

IN_PROGRESS 

Responder or system is actively working on response tasks. 

IN_PROGRESS -> READY_FOR_REVIEW 

READY_FOR_REVIEW 

Required tasks/results are present and awaiting human confirmation. 

READY_FOR_REVIEW -> COMPLETE / 

### RETURNED 

COMPLETE 

Phase requirements have been confirmed. 

COMPLETE -> next phase 

### RETURNED 

Review found missing, invalid, unsafe, or conflicting information. 

RETURNED -> IN_PROGRESS 

Important: phase advancement must not be inferred only from an AI response. The backend should enforce required conditions and preserve an explicit responder confirmation, 

consistent with the manual phase gate used across the supplied phase documents. 

Page 3 

### 4. Data Model & AI Contract 

## **4.1 Minimum Data Objects** 

Object 

Minimum fields 

# **Purpose** 

ResponseTask 

task_id, incident_id, phase3_stage, action, target_ref, owner, status, 

created_at 

Structured containment, eradication or recovery task. 

ActionApproval 

approval_id, task_id, decision, decided_by, decided_at, rationale 

Auditable responder authorization, edit, or rejection. 

ActionExecution 

execution_id, task_id, mode, started_at, completed_at, outcome, 

evidence_refs 

Records simulated or executed response activity and result. 

RecoveryCheck 

check_id, target_ref, check_type, status, evidence_refs, verified_by, 

verified_at 

Verifies that recovery conditions are satisfied. 

Phase3Handoff 

handoff_id, incident_id, status, completed_tasks, unresolved_items, 

residual_risk 

Structured output consumed by Phase 4. 

## **4.2 AI Input / Output Contract** 

The AI layer should receive normalized incident context rather than raw UI text. The prompt/context builder should provide only the fields 

needed for the current 

phase, together with verified Phase 2 findings, previous timeline events, evidence references, affected assets, and available response 

procedures. The model 

output must be machine-readable so the backend can validate it before displaying or persisting it. 

## **4.3 Output Rules** 

I Never convert an AI recommendation into an executed action automatically. 

I Every recommended action should identify its stage, target, rationale, prerequisites, expected evidence/result, and priority where 

applicable. 

I Every action affecting evidence, credentials, accounts, endpoints, network controls, or services must preserve related evidence and 

timeline references. 

I Simulation must remain distinct from execution and must never satisfy an execution or completion condition. 

I Responder decisions must be stored separately from AI recommendations. 

I Recovery verification must be based on a recorded backend check and evidence/result, not an AI summary. 

I The Phase 4 handoff must contain completed actions, outcomes, evidence references, unresolved items, and residual risk. 

## **4.4 Timeline Event Requirements** 

Every event should be append-only and attributable to either a human responder, the application, or the AI recommendation layer. Recommended fields: 

event_id, incident_id, timestamp_utc, actor_type, actor_id, phase, event_type, action_code, status, description, evidence_refs, 

previous_state, new_state, and 

correlation_id. 

Suggested AI input: 

{"phase":"CONTAINMENT_ERADICATION_RECOVERY","incident":{},"verified_findings":[],"affected_assets":[],"evidence_refs":[],"a vail 

able_playbooks":[ 

]} 

Suggested AI output: 

{"recommended_actions":[{"stage":"CONTAINMENT|ERADICATION|RECOVERY","action":"...","target_ref":"...","reason":"...","priorit y":" 

HIGH|MEDIUM|LOW 

","prerequisites":[]}],"recovery_checks":[],"unresolved_items":[],"human_review_required":true} 

## **4.5 Phase 3 Handoff Object** 

Field 

Required content 

incident_id 

Stable incident identifier carried from Phase 2. 

response_summary 

Structured summary of containment, eradication and recovery work. 

completed_actions 

Action/task IDs with final status and outcome. 

evidence_refs 

Evidence IDs supporting response outcomes and recovery verification. 

unresolved_items 

Blocking or non-blocking items that remain open. 

residual_risk 

Remaining risk after response and recovery verification. 

human_review_required 

True until responder explicitly confirms the Phase 4 handoff. 

Page 4 

### 5. Examples, Edge Cases & Acceptance Criteria 

## **5.1 Concrete Examples** 

Example A - Compromised endpoint: The verified finding indicates suspicious execution on a workstation. The system proposes 

endpoint isolation as 

containment, removal of the confirmed malicious artifact as eradication, and a post-remediation health check as recovery. The responder confirms the actions and 

the backend records each result separately. 

Example B - Compromised account: Verified authentication evidence indicates account compromise. The system proposes disabling the 

account, rotating 

credentials, reviewing active sessions, and verifying successful recovery. The AI explains the sequence; the backend records approval, 

execution and verification. 

Example C - Simulation before execution: A proposed network block is simulated to identify expected impact. The simulation creates a 

timeline event and 

remains SIMULATED until a responder authorizes actual implementation. 

## **5.2 Edge Cases** 

I Action recommended without sufficient evidence -> keep it RECOMMENDED and flag the evidence gap; do not mark it executed. 

I Containment succeeds but eradication fails -> preserve the successful containment and return the failed remediation task to IN_PROGRESS or RETURNED. 

I Recovery check fails -> keep the phase incomplete and create a blocking item. 

I One task affects multiple assets -> maintain separate target references and outcomes rather than flattening them into one text field. 

I Same action is recommended twice -> reference the existing task unless the second execution is materially distinct. 

I New evidence is generated during response -> create a stable evidence record and link it to the relevant action and timeline events. 

I Responder edits an AI recommendation -> preserve the original recommendation and store the responder-approved version separately. 

I Incident reopens after completion -> create a new state transition/version; do not overwrite historical response records. 

## **5.3 Acceptance Criteria** 

I Phase 3 consumes a verified Phase 2 handoff without rereading raw alert text. 

I Every response action has a stable task ID, phase-3 stage, target, owner/status, and traceable outcome. 

I Backend distinguishes RECOMMENDED, APPROVED, SIMULATED, EXECUTED, FAILED, VERIFIED, and BLOCKED without parsing natural-language AI 

output. 

I Simulation never counts as execution or completion. 

I Completed containment, eradication, and recovery actions have required evidence/outcome references. 

I Recovery verification is explicit and cannot be inferred from an AI summary. 

I Phase 4 handoff contains response summary, completed actions, evidence references, unresolved items, and residual risk. 

I AI output validates against the defined schema and is safely rejected when required fields are missing. 

6. Implementation Notes for Backend Team 

I Store response tasks, approvals, executions, recovery checks, and phase handoffs in PostgreSQL with stable foreign-key references 

to the incident. 

I Expose explicit Phase 3 APIs for planning, approval, simulation, execution/result recording, recovery verification, and phase 

completion. 

I Use UTC timestamps internally and convert to local display time only at the UI layer. 

I Use deterministic backend validation for action status, evidence requirements, recovery checks, and phase advancement; use 

Gemini/API output only for 

recommendations, sequencing, explanations, and summarization. 

I Keep evidence references stable even if an evidence object moves in storage. 

I Do not let an LLM directly execute privileged actions; execution should occur through controlled backend integrations or a clearly 

recorded simulated/manual 

### workflow. 

I Design the schema so Phase 4 references Phase 3 records without copying their full content. 

### 7. Source Alignment 

Primary project source: supplied Phase 2 and Phase 4 Functional Specifications, which establish the project’s operational style: structured phase entry/exit, 

human review, machine-readable AI contracts, centralized append-only timeline, evidence references, explicit state transitions, and manual phase progression. 

Challenge source: the supplied “The Clock Is Running” project structure, which asks for an assistant that suggests steps structured by 

the NIST four phases, 

maintains a timeline, drafts a compliance-ready incident report, maps actions to ATT&CK;, preserves evidence-chain information, and 

### flags regulatory notification 

### triggers. 

NIST reference: the supplied project documents state that SP 800-61 Rev. 2 describes the four-phase incident-handling lifecycle used in 

### the challenge, while SP 

800-61 Rev. 3 is the current revision and supersedes Rev. 2. The repository should explicitly record which NIST revision is being implemented. 

