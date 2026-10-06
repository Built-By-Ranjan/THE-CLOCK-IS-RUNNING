# **Phishing Attack Documentation (phishing.md)** 

## **1. Attack Overview** 

- **Attack Name:** Phishing Attack 

- **Category:** Initial Access / Social Engineering 

- **Concise Definition:** Social engineering attack technique where malicious actors send deceptive communications disguised as trustworthy entities to trick users into revealing sensitive credentials, executing malicious attachments, or granting unauthorized access. 

- **Purpose:** To obtain valid user credentials, bypass multi-factor authentication, gain initial corporate network access, or deploy secondary payloads (such as downloaders or ransomware). 

- **Typical Target / Context:** Employees across all organizational units, high-privilege administrators, finance personnel (for BEC/spearphishing), and external consumers accessing corporate SaaS/web portals. 

- **Typical Entry Point:** Inbound email perimeter (SMTP/HTTPS), direct messaging/collaboration platforms (Teams, Slack), SMS (Smishing), or voice channels (Vishing). 

- **Likely Impact:** Credential theft, account takeover, unauthorized initial entry into corporate environments, deployment of malware, financial loss via wire fraud, and compromise of sensitive data. 

## **2. Attack Scenario** 

- **Project Scenario:** An external threat actor creates a spoofed domain (portal-security-update.com) imitating the company's SSO authentication portal. The attacker distributes an automated email campaign to 200 corporate employees containing an urgent password reset link. 

- **Incident Entry:** Inbound email arrives via edge email security gateways (SEG) passing or bypassing SPF/DKIM checks using a newly registered lookalike domain over HTTPS/TLS. 

- **Expected Observations:** 

   1. Spikes in inbound emails containing similar subject lines, external link domains, or newly registered top-level domains (TLDs). 

   2. Multiple distinct users clicking the embedded link within a short time window. 

   3. Outbound web connections to external, uncategorized, or lowreputation IP addresses/domains from internal endpoints. 

   4. Authentication failures or unusual successful sign-in events (e.g., unexpected location/device) on the legitimate SSO portal immediately following the click events. 

5. Potential rapid submission of MFA prompt responses (MFA fatigue) reported by end users. 

### **3. Attack Behaviour / Lifecycle** 

1. **Reconnaissance & Setup:** Attacker gathers target organization data (employee emails, software stack) and registers lookalike domains, setting up reverse proxies (e.g., adversary-in-the-middle) or credential harvest pages. 

2. **Lure Delivery:** Automated dispatch of phishing messages containing malicious links, weaponized documents, or QR codes designed to bypass basic perimeter filters. 

3. **User Interaction:** The victim opens the message and interacts with the link or attachment due to urgency, fear, or authority cues. 

4. **Credential Harvest / Exploitation:** 

   - _Path A:_ The user submits credentials (and MFA tokens) into a clone portal, which are intercepted by the attacker. 

   - _Path B:_ The user executes a malicious attachment, triggering local code execution or script download. 

5. **Initial Access & Persistence:** Attacker uses captured active session cookies or valid credentials to access internal corporate resources, establish persistence, or pivot laterally. 

## **4. Indicators** 

Network Indicators 

- **Source IP / Sender Domain:** Inbound emails originating from lowreputation external mail servers or newly registered domain names (<30 days old). 

- **Malicious URL / Domain:** HTTP/HTTPS requests to newly observed or uncategorized domains (portal-security-update.com) or IP-based URLs. 

- **Traffic Anomalies:** Short-duration outbound TLS connections from internal hosts to external IP addresses immediately following email delivery timestamps. 

- **DNS Query Spikes:** Sudden volume spikes in DNS lookup requests across multiple hosts for a single previously unknown external domain. 

Endpoint Indicators 

- **Process Lineage Anomalies:** Office applications spawning scripting hosts or command interpreters (e.g., winword.exe spawning powershell.exe, cmd.exe, or wscript.exe). 

- **File Creation / Artifacts:** Lure attachments dropped into user temporary directories (e.g., %TEMP%, Downloads, or /tmp) containing double extensions (e.g., .pdf.exe, .invoice.xlsm). 

- **Browser Redirect Patterns:** Local web browser process history recording rapid redirects through bit.ly, tinyurl, or known proxy endpoints prior to reaching the target domain. 

- **Child Process Network Activity:** Non-standard processes (e.g., mshta.exe, certutil.exe) establishing outbound internet connections to pull secondary files. 

#### Account / Identity Indicators 

- **Anomalous Logins:** Successful authentications (Event ID 4624 or Cloud IdP logs) originating from unusual ASN ranges, unexpected countries, or TOR/VPN egress nodes within minutes of a link click. 

- **Concurrent Active Sessions:** Multiple active sessions established for the same identity across disparate geographical locations within impossible travel timeframes. 

- **MFA Prompt Surges:** High volume of pushed or rejected MFA authorization requests recorded in identity provider logs for a single user account. 

- **Inbox Rule Modifications:** Automatic creation of client-side or serverside inbox rules (e.g., moving messages with "phish", "invoice", or "security" to RSS/Deleted folders) following a successful login. 

#### Application Indicators 

- **HTTP User-Agent Header Anomalies:** Outbound POST requests containing non-standard, blank, or outdated User-Agent strings. 

- **Authentication Endpoint Status:** HTTP 200 OK or 302 Found status responses on external credential harvesting pages following an initial HTTP POST submission. 

- **Email Gateway Telemetry:** High volume of inbound emails failing SPF, DKIM, or DMARC checks, or flagged with high spam/phishing risk scores by SEGs. 

- **OAuth App Authorizations:** User authorization of unverified third-party OAuth applications granting access to email, files, or directory permissions. 

#### Behavioural Indicators 

- **Urgency & Coercion Patterns:** Email subject lines containing highurgency keywords ("Immediate Action Required", "Account Suspended", "Payroll Adjustment"). 

- **Mass Link Interaction:** Multiple users across different departments clicking the exact same unique link within a compressed time window. 

- **User Escalations:** Increase in user-submitted suspicious email reports (e.g., via PhishAlarm/Report Phishing button) targeting a specific lure template. 

**Immediate Post-Authentication Changes:** Immediate updates to user MFA methods, contact email addresses, or password reset configurations following logon. 

## **5. MITRE ATT&CK Mapping** 

- **Mapping Entry 1:** 

   - **Tactic:** Initial Access 

   - **Technique:** Phishing (T1566) 

   - **Sub-Technique:** Spearphishing Link (T1566.002) 

   - **Mapping Rationale:** Threat actor sends targeted emails containing malicious links to lure users into submitting credentials on a fake landing page. 

   - **Evidence Supporting Mapping:** Inbound email logs with external links combined with web proxy logs confirming user clicks to `portal-securityupdate.com` . 

   - **Status:** VERIFIED 

- **Mapping Entry 2:** 

   - **Tactic:** Initial Access 

   - **Technique:** Phishing (T1566) 

   - **Sub-Technique:** Spearphishing Attachment (T1566.001) 

   - **Mapping Rationale:** Email message delivered with a weaponized attachment designed to execute code upon opening. 

   - **Evidence Supporting Mapping:** Email security logs capturing `.xlsm` file attachments paired with EDR telemetry showing child process spawning. 

   - `o` **Status:** CANDIDATE 

- **Mapping Entry 3:** 

   - **Tactic:** Credential Access 

   - **Technique:** Adversary-in-the-Middle (T1556.006) 

   - **Sub-Technique:** Multi-Factor Authentication Interception 

   - **Mapping Rationale:** Attacker uses a reverse proxy landing page to capture both passwords and live MFA session tokens/cookies. 

   - **Evidence Supporting Mapping:** Proxy logs matching user interaction paired with immediate token reuse from a different external IP address. 

   - **Status:** CANDIDATE 

- **Mapping Entry 4:** 

   - **Tactic:** Defense Evasion 

   - **Technique:** Unused/Valid Domain Registration (T1583.001) 

   - **Sub-Technique:** Typosquatting / Lookalike Domains 

   - **Mapping Rationale:** Attacker registers a domain closely resembling the target organization's domain name to deceive users and bypass basic reputation checks. 

   - **Evidence Supporting Mapping:** WHOIS domain creation date showing registration <7 days prior to email campaign dispatch. 

   - **Status:** VERIFIED 

## **6. Detection** 

Detection Signals & Data Sources 

- **Secure Email Gateway (SEG) Logs:** Inbound message logs capturing sender domain, source IP, SPF/DKIM/DMARC status, subject line, attached file hashes, and embedded URLs. 

- **DNS & Web Proxy Logs:** Gateway proxy and DNS resolver logs tracking domain requests, category flags (e.g., "Newly Registered Domain"), HTTP request methods (POST), and outbound URL paths. 

- **Identity Provider (IdP) Sign-In Logs:** Azure AD / Okta logs capturing successful/failed logins, client IP, location, user ID, device info, and MFA status codes. 

- **Endpoint Detection & Response (EDR):** Endpoint process trees (Sysmon Event ID 1), network connections (Sysmon Event ID 3), and browser extension/download events. 

Normalized Fields 

- sender_email: Sender address string parsed from email headers. 

- recipient_email: Target internal user email address. 

- src_ip: Originating IP address of the email sender or client connecting to the web proxy. 

- dest_domain: Target domain extracted from embedded link or outbound web request. 

- url_path: Full path and parameters of the clicked link. 

- event_id: Normalized event type code (e.g., email_delivered, link_clicked, auth_success). 

- attachment_hash: SHA-256 hash of dropped email attachments. 

- user: Affected user identity string. 

Correlation Logic / Rule Hypotheses 

- **Hypothesis 1 — Phishing Link Click Event:** 

   - _Logic:_ IF event_id = 'email_delivered' containing dest_domain AND event_id = 'proxy_request' to same dest_domain by user within 1 hour THEN flag ALERT_PHISHING_LINK_CLICKED. 

- **Hypothesis 2 — Post-Click Credential Submission:** 

   - _Logic:_ IF ALERT_PHISHING_LINK_CLICKED is TRUE AND http_method = 'POST' to dest_domain THEN flag ALERT_PHISHING_CREDENTIAL_SUBMITTED. 

- **Hypothesis 3 — Compromise via Phishing (High Severity):** 

   - _Logic:_ IF ALERT_PHISHING_CREDENTIAL_SUBMITTED is TRUE for user AND followed by event_id = 'auth_success' from external IP (different from normal user baseline) within 30 minutes THEN flag ALERT_PHISHING_ACCOUNT_COMPROMISE (High Severity). 

False Positive & Validation Checks 

- **Legitimate Marketing / Third-Party Services:** Verify if the sender domain or URL belongs to authorized third-party marketing vendors (e.g., Mailchimp, Salesforce) or internal security awareness training platforms (e.g., KnowBe4). 

- **Password Reset Requests:** Confirm whether the user explicitly initiated a password reset flow immediately prior to the email delivery timestamp. 

- **Canonical Domain Validation:** Cross-reference destination domains against internal domain allowlists to ensure links are not pointing to legitimate corporate subdomains. 

# **7. Evidence Requirements** 

Primary Required Evidence 

- **Raw Email Headers & Message Content:** Unaltered .eml or .msg files capturing full hop headers, envelope sender, return-path, SPF/DKIM signatures, and raw HTML body content. 

- **Web Proxy & DNS Gateway Logs:** Time-stamped proxy logs confirming HTTP GET/POST requests, full destination URLs, user agent strings, and source IP addresses matching the link click. 

- **Verified Authentication Logs:** IdP sign-in records confirming subsequent logins, session creation, or token grants associated with the user account following the event time. 

#### Supporting Evidence 

- **Endpoint File & Process Telemetry:** EDR logs showing browser process activity, downloaded file artifacts, or execution of scripts/attachments on the user endpoint. 

- **User Incident Submissions:** End-user report records submitted via antiphishing plugins, including user-provided context and timestamp of discovery. 

- **WHOIS & Domain Intelligence Data:** Domain registration records, age, registrar info, and threat intelligence scores for the external domain. 

Evidence-to-Claim Relationship 

- **To Claim "Phishing Campaign Delivered":** Requires SEG logs proving message delivery containing malicious links or attachments to one or more internal mailboxes. 

- **To Claim "User Interacted with Phishing Lure":** Requires web proxy or DNS logs proving the target user endpoint initiated an outbound connection to the external phishing domain. 

- **To Claim "Account Compromise Confirmed":** Requires IdP logs showing successful authentication or active session generation from an attacker-controlled IP immediately following credential submission telemetry. 

Preservation & Reference Consideration 

- **Message Export & Quarantine:** Export raw .eml files to secure, isolated storage and hash using SHA-256 immediately upon ingest. 

- **Safe Artifact Handling:** Save phishing attachments and landing page source code inside password-protected ZIP archives (password: infected) to prevent accidental execution by responders. 

- **Clock Synchronization:** Ensure time stamps across SEG, proxy, and IdP sources are verified against an authoritative NTP reference (within $\pm 100\text{ ms}$). 

## **8. Incident Response Lifecycle** 

Phase 1 - Preparation 

- **Playbook Requirements:** Active Playbook-PH-01: Phishing and Credential Abuse Response. 

- **Readiness Checks:** Verify central mail server administrative API access (e.g., Microsoft Graph API / Google Workspace API) for automated message search and purge operations. 

- **Logging/Evidence Configuration:** Ensure SEG logs record full URL parameters and message headers. Confirm web proxies log outbound POST requests and client source IPs. 

- **Notification / Escalation Matrix:** Pre-configured notification paths to SOC Tier-1/Tier-2, Messaging Administrators, and Identity Access Management (IAM) teams. 

- **Expected Preparation Output:** Functional automated mail-purge scripts, updated domain blocklists, and active SOC dashboard tracking reported emails. 

Phase 2 - Detection & Analysis 

- **Intake & Normalization:** Process reported phishing emails or SEG alerts; normalize fields to sender_email, dest_domain, recipient_email, and src_ip. 

- **Triage & Analysis:** 

   - Determine scope: Search mail server logs to identify all mailboxes that received the same message or link. 

   - Analyze lure: Inspect destination domains for credential harvest forms or attachment execution payloads. 

- **Correlation & Candidates:** Match proxy logs against recipient mailboxes to isolate users who clicked the link; assign MITRE candidate tag T1566.002. 

- **Confirmed Facts vs. Hypotheses:** 

   - _Fact:_ Email received by 45 users; web proxy records 3 users clicked the link [http://portal-security-update.com/login](http://portal-securityupdate.com/login). 

   - _Hypothesis:_ One user submitted valid credentials and an MFA code on the cloned site. 

- **Phase 3 Handoff Requirements:** Handoff requires a confirmed list of affected recipient mailboxes, identified malicious domains/IPs, a list of users who clicked the link, and confirmation of any successful post-click logins. 

Phase 3 - Containment, Eradication & Recovery _Attack-Specific Containment_ 

- **Mailbox Purge:** Execute administrative search-and-purge commands across all organizational mailboxes to remove the phishing email. 

- **Network & Gateway Blocking:** Block the destination domain, URL, and sender IP address at perimeter web proxies, DNS sinkholes, and SEGs. 

- **Account Disabling:** Temporarily disable access or enforce immediate session revocation for users confirmed to have submitted credentials. 

_Eradication_ 

- **Credential Reset:** Execute forced password resets for all affected users across Directory Services and connected Identity Providers. 

- **Token Revocation:** Invalidate all active OAuth tokens, refresh tokens, and session cookies for impacted identities. 

- **Inbox Rule Clean-up:** Audit and remove any unauthorized forwarding rules or inbox manipulation settings created post-login. 

- **Endpoint Remediation:** If an attachment was executed, isolate the endpoint and perform full EDR quarantine and artifact removal. 

_Recovery & Verification_ 

- **Prerequisites:** Mailboxes purged; perimeter blocks verified; passwords reset; tokens revoked; endpoint scans clean. 

- **Recovery Verification Steps:** 

   1. Verify zero outbound connection attempts to the blocked domain across all network proxy logs. 

   2. Confirm affected user accounts are re-enabled with newly generated credentials and enforced FIDO2/MFA hardware tokens where applicable. 

   3. Monitor user sign-in logs for 24 hours to confirm baseline login patterns. 

- **Expected Evidence/Results:** Clean proxy logs, confirmed email deletion records, and verified user identity state updates. 

Phase 4 - Post-Incident Activity 

- **Final Report Information:** Total mailboxes targeted, click count, credential submission count, root cause analysis, timeline, and mitigation metrics. 

- **Notification Review:** Evaluate compliance requirements (e.g., GDPR, HIPAA) regarding potential unauthorized access to personal or protected data if credentials were leveraged. 

- **Lessons Learned:** Assess why the phishing email bypassed perimeter SEG filters (e.g., weak SPF checks, zero-day domain reputation) and why users interacted with the lure. 

- **Improvement Actions:** 

   - Tune SEG policies to quarantine messages from domains registered <14 days ago. 

   - Implement FIDO2 / WebAuthn phishing-resistant MFA across all corporate access portals. 

   - Conduct targeted security awareness micro-training for users who clicked the phishing link. 

# **9. Severity & Scope Considerations** 

- **Impacted Account Privilege:** Phishing targeting standard employees vs. executive staff, system administrators, or financial controllers. 

- **User Interaction Level:** Email delivered but unopened (Low) vs. link clicked without submission (Medium) vs. confirmed credential submission and MFA token capture (High/Critical). 

- **Payload Type:** Credential harvesting lure vs. automated attachment delivering ransomware/downloader payloads. 

- **Widespread Exposure:** Single targeted recipient (Spear Phishing) vs. mass distribution targeting thousands of internal endpoints simultaneously. 

# **10. AI Recommendation Guidance** 

What AI May Recommend (Advisory) 

- Identify and group emails sharing identical body structures, header hashes, or URL paths. 

- Suggest candidate MITRE ATT&CK technique tags (e.g., T1566.002) based on email artifacts. 

- Propose administrative mail-purge queries or proxy domain blocklists. 

- Summarize user-reported email trends and flag suspicious domain lookalikes. 

What Must Remain a Human / Backend Decision 

- **Final Incident Severity:** The human responder must assign and confirm the incident severity. 

- **Verification of Facts:** AI suggestions must never automatically convert hypotheses (e.g., "User likely entered credentials") into confirmed incident facts without backend log verification. 

- **Execution of High-Impact Actions:** Disabling user accounts, purging enterprise-wide mailboxes, or applying network-wide domain blocks require human authorization or explicit policy-driven backend confirmation. 

- **Phase Progression:** Moving the incident state from Detection to Containment or Recovery requires explicit responder approval. 

# **11. Edge Cases & Common Ambiguities** 

- **Edge Case 1: Authorized Security Awareness Campaign** `o` **Cause / Description:** The organization's security team or an authorized contractor executes a simulated phishing test that triggers SOC alert rules. 

   - **Triage & Analysis Resolution:** Cross-reference email headers and source IPs against the authorized simulated phishing platform server list prior to executing containment actions. 

- **Edge Case 2: Legitimate Marketing / SaaS Password Resets** `o` **Cause / Description:** A user requests a password reset from a legitimate external service, but the notification email triggers heuristics due to new external domains or URL shorteners. 

   - **Triage & Analysis Resolution:** Verify whether the recipient initiated the request and check if the destination domain belongs to a verified corporate SaaS provider. 

- **Edge Case 3: Adversary-in-the-Middle (AiTM) Reverse Proxies** `o` **Cause / Description:** Attackers proxy live traffic to the actual corporate login page, capturing session cookies and bypassing traditional MFA. 

   - **Triage & Analysis Resolution:** Look for session IP mismatches between the initial authentication request and subsequent application API calls. 

- **Edge Case 4: Email Gateway URL Rewriting / Scanning** 

   - **Cause / Description:** Automated security gateway sandbox tools click embedded URLs to analyze destination pages, creating false proxy click events. 

   - **Triage & Analysis Resolution:** Filter out proxy requests originating from known SEG sandbox IP blocks or User-Agent strings associated with security scanners. 

- **Edge Case 5: Delayed User Clicks** 

   - **Cause / Description:** A user opens and clicks a phishing link days or weeks after the initial email delivery, long after the campaign was flagged. 

- **Triage & Analysis Resolution:** Ensure perimeter blocklists for malicious domains remain active beyond the initial incident window to block delayed interactions. 

# **12. Fact vs. Hypothesis Separation** 

- **Observed Fact:** Secure Email Gateway recorded 150 inbound emails from attacker@portal-security-update.com containing link [http://portal-securityupdate.com/login](http://portal-security-update.com/login); web proxy logs confirm user jdoe accessed the link at 11:05:22 UTC. 

- **Hypothesis:** User jdoe entered domain credentials and an active MFA code on the landing page, allowing the attacker to establish an active session. 

- **Evidence Needed:** IdP sign-in records for user jdoe showing an authentication event from an external IP matching the proxy timestamp, or explicit HTTP POST request payload logs. 

- **AI Recommendation:** Advisory: Recommend initiating a password reset for user jdoe, revoking active session tokens, and purging remaining messages from mailboxes. 

- **Human Decision:** SOC Analyst confirms the IdP session anomaly, approves token revocation and password reset for user jdoe, and authorizes the global domain block. 

# **13. Sources / References** 

1. **MITRE ATT&CK Framework:** Technique T1566 (Phishing) - <u>https://attack.mitre.org/techniques/T1566/</u> 

2. **NIST Special Publication 800-61 Rev. 2:** Computer Security Incident Handling Guide - <u>https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.80061r2.pdf</u> 

3. **CISA Security Guide:** Phishing Prevention and Incident Response Best Practices - https://www.cisa.gov/phishing-guidance 

4. **OWASP Foundation:** Social Engineering Attack Prevention and Assessment Guidelines. 

5. **Project Technical Specification:** System Logging and Incident Response Requirements v2.4. 

