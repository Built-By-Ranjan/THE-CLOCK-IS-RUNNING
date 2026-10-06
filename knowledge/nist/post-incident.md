**The Clock Is Running - Incident Response Helper Phase 4 — Post-Incident Activity** 

### **Backend / AI Implementation Documentation** 

Phase 4 - Post-Incident Activity 

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

Backend function API / code reference Phase 4 Trigger 

Supplied Phase 4 Functional Specification §1.1 and supplied Phase 3 specification; manual progression after response completion. validate_phase4_entry() POST /api/incidents/{id}/p hases/4/validate-entry Final Incident Review Supplied Phase 4 Functional Specification §1.2; assembles detection, analysis, response, evidence, decisions and unresolved items. build_final_review() GET /api/incidents/{id}/fi nal-review; GET /api/incid ents/{id}/timeline Reporting and Compliance Preparation Supplied Phase 4 Functional Specification §1.3; structured report and notification-trigger evaluation without replacing human legal/compliance decisions. prepare_final_report() POST /api/incidents/{id}/r eport/generate; POST /api/ incidents/{id}/notificatio n-check Lessons Learned and Improvement Supplied Phase 4 Functional Specification §1.4; actionable improvements feeding future preparation. capture_lessons_learned( ) POST /api/incidents/{id}/l essons-learned; POST /api/ knowledge-base/change-prop osals Closure Supplied Phase 4 Functional Specification §1.5; required checks plus explicit responder sign-off. close_incident() POST /api/incidents/{id}/c losure/validate; POST /api /incidents/{id}/closure/co nfirm 

Source-derived Functional Specification 

The following pages preserve the supplied phase specification content. No project requirement is presented as a direct NIST requirement unless the 

source alignment explicitly says so. 

Page 1 

Functional Specification: Phase 4 - Post-Incident 

Activity 

# **Purpose** 

Phase 4 closes the response loop by reviewing the complete incident, producing the final report, checking configured notification triggers, recording lessons learned, and converting validated improvements into future preparation work. 

# **Scope and Objectives** 

I Create a traceable final incident record from the complete timeline. 

I Generate a compliance-ready report draft from verified structured data. 

I Evaluate configured notification triggers and deadlines without replacing human compliance decisions. 

I Capture lessons learned as actionable improvement records. 

I Preserve report versions and closure decisions. 

I Feed validated improvements back into Preparation. 

# **System Position in the Four-Phase Flow** 

This document defines the expected system behaviour for this phase. The phase must consume the structured incident state produced by the previous phase, perform only the responsibilities assigned to this phase, record all meaningful state changes in the central incident timeline, and produce a structured output that can be consumed by the next phase. 

The project follows the four-phase incident-response structure used in the supplied challenge and Phase 3 specification: Preparation -> Detection & Analysis -> Containment, Eradication & Recovery -> Post-Incident Activity. The supplied Phase 3 specification requires human review, simulated execution, centralized timeline logging, evidence protection, and explicit phase progression. 

Implementation note: NIST published SP 800-61 Rev. 3 in April 2025 and it supersedes Rev. 2. The challenge material, however, explicitly asks the project to use the NIST four-phase structure; therefore this project documentation keeps that four-phase structure for consistency with the supplied problem statement and existing Phase 3 document. 

# **Phase Entry / Exit Contract** 

Item 

Requirement Entry 

Incident exists with a unique incident ID and the minimum required metadata for this phase. Processing 

The platform evaluates the incident using deterministic rules plus AI assistance where configured. Human control 

AI recommendations are advisory. A responder remains responsible for confirmation, edits, rejection, and phase advancement. 

Audit 

Every meaningful action, recommendation decision, evidence change, and status transition creates a timeline event. 

Exit 

A structured phase-complete record is created only when required checks are satisfied. 

Page 2 

### 1. Operational Workflow & System Behaviour 

## **1.1 Phase 4 Trigger** 

Phase 4 begins only after the responder confirms that containment, eradication, and recovery work has reached the required completion state. The supplied Phase 3 specification explicitly requires manual progression into Phase 4 rather than automatic phase shifting. 

## **1.2 Final Incident Review** 

The platform assembles the complete incident record: initial detection, analysis findings, containment/eradication/recovery actions, evidence references, responder decisions, timestamps, and unresolved items. The purpose is to create one consistent source for the final incident report. 

## **1.3 Reporting and Compliance Preparation** 

The system generates a structured incident report containing executive summary, technical timeline, impact, root-cause or contributing-factor findings, actions taken, evidence references, notification status, and lessons learned. Regulatory triggers are shown as status and evidence-backed conditions; the system must not claim that a legal obligation is satisfied merely because a rule matched. 

## **1.4 Lessons Learned and Improvement** 

The responder records what worked, what failed, what data was missing, and what changes should be made to playbooks, 

controls, logging, training, or notification procedures. These outputs become inputs to future preparation. 

## **1.5 Closure** 

An incident may be closed only when required reporting, evidence references, action review, and responder sign-off conditions are satisfied. The system preserves the final state and prevents silent modification of the closed record. 

2. Feature Matrix & MVP Scope 

Feature / Component 

Operational Purpose 

Backend / MVP Behaviour 

Final Incident Summary 

Creates a consistent human-readable account of the 

incident. 

Build from structured records; clearly separate facts, findings 

and unresolved items. 

Compliance / Notification Check 

Flags configured notification triggers and deadlines. 

Evaluate stored rules against verified incident timestamps; 

show TRIGGERED / NOT_TRIGGERED / 

REVIEW_REQUIRED. 

Report Generator 

Produces a compliance-ready incident report draft. 

Generate structured Markdown/HTML/PDF-ready content from 

database records. 

Lessons Learned 

Captures improvement actions for future incidents. 

Store action, owner, priority, due date and linked incident. 

### Closure Gate 

Prevents premature incident closure. 

Require explicit responder confirmation and required-field 

validation. 

Post-Incident Timeline 

Preserves final audit history. 

Append report generation, review, notification status and 

closure events. 

Knowledge Base Feedback 

Feeds validated lessons into future preparation. 

Create proposed playbook/knowledge-base changes for 

human review before publication. 

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

Object 

Minimum fields 

# **Purpose** 

IncidentReport 

report_id, incident_id, version, generated_at, status Versioned final report draft. NotificationCheck 

rule_id, evaluated_at, result, evidence_refs, reviewer Audit of notification trigger evaluation. 

LessonLearned 

lesson_id, statement, action, owner, due_date, status Improvement record. 

ClosureDecision 

status, decided_by, decided_at, rationale 

Explicit closure authorization. 

ReportSection 

report_id, section, content, source_refs 

Traceable report content. 

## **4.2 AI Input / Output Contract** 

The AI layer should receive normalized incident context rather than raw UI text. The prompt/context builder should provide only the fields needed for the current phase, together with previous verified timeline events and evidence references. The model output 

must be machine-readable so the backend can validate it before displaying it. 

ication_status":"...","lessons_learned":"..."},"unresolved_items":["..."],"source_refs":[]} y":false,"blocking_items":["..."]} 

## **4.3 Output Rules** 

I The report generator must cite or reference the structured records from which important statements were derived. 

I AI-generated narrative must not invent dates, assets, users, impact, notification status, or evidence. 

I Notification checks are implementation rules and review flags, not legal advice. A human compliance/legal process remains responsible for the final determination. 

I Lessons learned must be stored as actionable records rather than only as free-form report text. 

I Closure is a state transition controlled by backend validation plus explicit responder confirmation. 

## **4.4 Timeline Event Requirements** 

Every event should be append-only and attributable to either a human responder, the application, or the AI recommendation layer. 

The supplied Phase 3 design uses structured timeline events and treats the audit timeline as the central record for responder actions and compliance reporting. 

Recommended fields: event_id, incident_id, timestamp_utc, actor_type, actor_id, phase, event_type, action_code, status, 

description, evidence_refs, previous_state, new_state, and correlation_id. 

{"phase":"POST_INCIDENT","incident":{},"timeline":[],"evidence":[],"notification_rules":[],"recovery_summary":{}} 

{"report_sections":{"executive_summary":"...","timeline_summary":"...","impact":"...", 

"actions_taken":"...","evidence_summary":"...","notification_status":"...","lessons_learned":"..."}, 

"unresolved_items":["..."],"source_refs":[]} 

{"notification_review":[{"rule_id":"...","status":"TRIGGERED|NOT_TRIGGERED|REVIEW_REQUIRED", 

"reason":"...","source_refs":[]}],"closure_ready":false,"blocking_items":["..."]} 

Page 4 

### 5. Examples, Edge Cases & Acceptance Criteria 

## **5.1 Concrete Examples** 

Example A - Final report: The platform combines the verified timeline with containment, eradication and recovery events. 

The report states what happened, what was done, what evidence supports each major statement, and which items remain unresolved. 

Example B - Notification trigger: A configured rule matches a verified incident timestamp. The system records 

NOTIFICATION_REVIEW_REQUIRED with the rule ID, trigger reason, deadline and source references. It does not claim that a notification was legally required or already sent unless the corresponding verified record exists. 

Example C - Lessons learned: The incident showed that a required log source was unavailable during analysis. The 

responder creates a lesson: enable/retain the log source, assigns an owner and due date, and links the improvement item to the incident. 

## **5.2 Edge Cases** 

I A report contains a statement with no source record -> mark it unresolved or remove it; never fabricate a source. 

I Notification rule configuration is missing -> status REVIEW_REQUIRED and record the configuration gap. 

I The incident is reopened after closure -> create a new version/state transition rather than overwriting the closed record. 

I A lesson learned changes a playbook -> create a proposed knowledge-base change and require review before publication. 

I A report is regenerated after new evidence -> increment the report version and preserve the earlier version. 

## **5.3 Acceptance Criteria** 

I The final report can be regenerated from stored structured records without depending on conversational memory. 

I Every major report section has traceable source references. 

I Notification checks are stored as auditable evaluations with rule IDs and timestamps. 

I Lessons learned are linked to concrete improvement actions. 

I Closure cannot occur while required blocking items remain unresolved. 

I Closed incidents retain immutable historical versions of reports and key timeline events. 

### 6. Implementation Notes for Backend Team 

I Generate the report from PostgreSQL records and the Git-versioned knowledge base; do not use the LLM as the source of truth. 

I Store report versions so regenerated documents can be compared without losing prior versions. 

I Keep notification rule definitions separate from incident results; the same rule can be evaluated against multiple incidents. 

I Use a structured report schema first, then render to Markdown/HTML/PDF. 

I Send only approved, minimal incident context to the AI layer and retain source references for every generated section. 

I Feed lessons learned back into Preparation through a review queue rather than silently modifying production playbooks. 

### 7. Source Alignment 

Primary project source: supplied Phase 3 Functional Specification, which defines the project’s operational style: automated trigger, human review, simulated execution, central audit timeline, evidence protection, and manual phase gate. Challenge source: the supplied Problem Statement 27, “The Clock Is Running,” which asks for an assistant that suggests steps structured by the NIST four phases, maintains a timeline, drafts a compliance-ready incident report, maps actions to ATT&CK, preserves evidence-chain information, and flags regulatory notification triggers. 

NIST reference: SP 800-61 Rev. 2 describes the four-phase incident-handling lifecycle used in the supplied challenge; SP 800-61 Rev. 3 is the current NIST revision and supersedes Rev. 2. The project should document its chosen version explicitly in the implementation repository. 

