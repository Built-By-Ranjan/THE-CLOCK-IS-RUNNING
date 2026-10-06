# **Brute Force Attack Documentation (brute_force.md)** 

#### **1. Attack Overview** 

- **Attack Name:** Brute Force Attack 

**Category:** Credential Access / Authentication Abuse 

**Concise Definition:** Systematic attempt to obtain valid account credentials by repeatedly submitting combinations of passwords, passphrases, or guessing logic against authentication mechanisms. 

**Purpose:** To gain unauthorized initial access, escalate privileges, or validate compromised credential sets. 

**Typical Target / Context:** Publicly accessible or internal authentication endpoints, including SSH, RDP, VPN portals, web login forms, Active Directory/Kerberos, API gateways, and cloud IAM portals. 

**Typical Entry Point:** External-facing exposed services (such as port 22/SSH, 3389/RDP, and HTTPS login pages) or compromised internal staging jump boxes targeting Active Directory domain controllers. 

**Likely Impact:** Account takeover, unauthorized access to sensitive internal systems, lateral movement vector, operational disruption via account lockout policies, and downstream privilege escalation. 

### **2. Attack Scenario** 

- **Project Scenario:** An automated botnet script targets an organization's public-facing SSH jump host (192.168.10.15) and secure web portal ([https://portal.company.com/login](https://portal.company.com/login)). Over a span of 15 minutes, the external source IP (198.51.100.42) executes high-frequency authentication attempts against hundreds of domain username variants. 

- **Incident Entry:** The attack enters at the network interface perimeter where public-facing authentication services accept ingress TLS/TCP connections on ports 443 and 22. 

- **Expected Observations:** 

   1. Spikes in authentication failure events (Event ID 4625 on Windows, PAM / sshd failure logs on Linux, HTTP 401/403 status codes on web servers). 

   2. Distinct failure patterns (e.g., hundreds of failures for a single account from one IP, or single password attempts across hundreds of accounts). 

   3. High-volume login requests sharing identical User-Agent strings or missing TLS handshake details. 

   4. Account lockout notifications triggered across multiple active accounts. 

   5. A potential successful login event (Event ID 4624 or SSH Accepted password) immediately following a cluster of failure events from the same source IP. 

#### **3. Attack Behaviour / Lifecycle** 

**Reconnaissance & Service Identification:** The attacker scans external IP ranges to locate open ports hosting interactive login prompts (SSH, RDP, web forms). 

**Credential / Wordlist Selection:** The attacker selects target accounts (e.g., admin, root, administrator, or harvested domain usernames) and configures dictionary files or password spraying scripts. 

###### **Execution Phase:** 

- **Direct Brute Force:** Automated submission of high-volume password attempts against a single target account. 

- **Password Spraying:** Automated submission of a small set of common passwords across many target accounts to evade threshold lockouts. 

- **Credential Stuffing:** Replaying leaked email/password pairs across targeted web login endpoints. 

###### **Account Lockout or Access Success:** 

- _Path A:_ System triggers account lockouts; legitimate users are impacted. 

- _Path B:_ A valid combination is identified; system records a successful authentication event. 

**Post-Authentication Activity:** Attacker uses newly authenticated session to execute commands, stage tools, or pivot internally. 

#### **4. Indicators** 

Network & Endpoint Indicators 

- **Source IP Address:** External IP (198.51.100.42) generating anomalous request volume. 

- **Target Port:** Port 22 (SSH), Port 3389 (RDP), Port 443 (HTTPS), Port 88 (Kerberos). 

- **Traffic Pattern / Request Rates:** Burst rates exceeding >20 authentication requests per minute from a single source or targeting a single identity. 

- **Protocol & TLS Handshake Characteristics:** Incomplete TLS handshakes, non-standard cipher suites, or missing SNI (Server Name Indication) extensions during TCP connection establishment. 

Endpoint Indicators 

- **Security Event Spikes:** Rapid accumulation of authentication failure log entries (Event ID 4625 on Windows Security Event Log, sshd failure messages in Linux /var/log/auth.log). 

- **Process Lineage Anomalies:** Post-authentication execution of shells or administrative utilities directly spawned by login services immediately following logon (e.g., sshd spawning bash -> curl, or lsass.exe spawning unexpected secondary processes). 

- **LSASS Memory Dumping Signals:** Access handles or process memory reads against lsass.exe following success/failure authentication sequences (e.g., Sysmon Event ID 10). 

- **Local Group Modification:** Unauthorized additions to local sensitive groups (e.g., Administrators, Remote Desktop Users) immediately following successful authentication bursts. 

###### Account / Identity Indicators 

- **Target Account Scope:** High-frequency access attempts against default administrative accounts (root, admin, administrator) or sequential domain accounts (jdoe, jsmith). 

- **Account Lockout Events:** Mass triggering of active directory account lockout policies across multiple distinct identities (Event ID 4740) within a narrow timeframe. 

- **Authentication Outcome Ratios:** Unusually high ratio of explicit authentication failure codes followed by a single successful authentication code (Event ID 4624 or SSH Accepted password). 

- **Impossible Travel / Anomaly Signals:** Consecutive login attempts or successes for the same user identity originating from geographically distant source locations within impossible travel timeframes. 

###### Application Indicators 

- **User-Agent Header Patterns:** Automated or default HTTP client useragent strings (e.g., `python-requests/2.28.1` , `Hydra` , `Go-http-client` , or empty/missing User-Agent headers). 

- **HTTP Endpoint Target URIs:** Repeated high-volume `POST` requests targeted specifically at authentication paths such as `/login` , `/api/v1/auth` , `/xmlrpc.php` , or OAuth token endpoints. 

- **HTTP Response Status Distribution:** Excessive volume of HTTP `401 Unauthorized` or `403 Forbidden` response status codes, followed by a single `200 OK` or `302 Found` response. 

- **MFA Application Telemetry:** High volumes of rejected Multi-Factor Authentication push notifications, rapid push resend requests, or userreported "MFA Fatigue" prompts. 

###### Behavioural Indicators 

- **Off-Hours Activity Patterns:** Authentication request bursts occurring outside standard business hours, maintenance windows, or user baseline schedules. 

- **Password Spraying Cadence:** Low-and-slow execution patterns designed to evade single-IP rate limits (e.g., exactly 1 failed attempt per account every 30 minutes across hundreds of users). 

- **Automated Dictionary Progression:** Sequential pattern of failed credentials exhibiting alphabetical, numerical, or dictionary-based password variations. 

- **Immediate Post-Access Reconnaissance:** Rapid execution of discovery commands (e.g., whoami, net group "Domain Admins" /domain, id, ipconfig /all) within seconds of successful authentication. 

#### **5. MITRE ATT&CK Mapping** 

- **Mapping Entry 1:** 

   - **Tactic:** Credential Access 

   - **Technique:** Brute Force (T1110) 

   - **Sub-Technique:** Password Guessing (T1110.001) 

   - **Mapping Rationale:** Attacker systematically iterates through password dictionaries against known target usernames. 

   - **Evidence Supporting Mapping:** Repeated failed authentication logs (Event ID 4625) containing systematic password pattern attempts from a single IP. 

   - **Status:** VERIFIED 

- **Mapping Entry 2:** 

   - **Tactic:** Credential Access 

   - **Technique:** Brute Force (T1110) 

   - **Sub-Technique:** Password Spraying (T1110.002) 

   - **Mapping Rationale:** Attacker tests a single common password against a wide list of target usernames to avoid account lockout. 

   - `o` **Evidence Supporting Mapping:** Auth logs showing 1-2 failed login attempts across 100+ distinct user accounts originating from the same source IP within a narrow window. 

   - **Status:** CANDIDATE 

- **Mapping Entry 3:** 

   - **Tactic:** Credential Access 

   - **Technique:** Brute Force (T1110) 

   - **Sub-Technique:** Credential Stuffing (T1110.004) 

   - **Mapping Rationale:** Attacker uses compromised credentials from external breaches to gain unauthorized access. 

   - **Evidence Supporting Mapping:** Automated HTTP POST auth requests using disparate username/password combinations at high frequency with mismatched User-Agents. 

   - **Status:** CANDIDATE 

- **Mapping Entry 4:** 

   - **Tactic:** Initial Access 

   - **Technique:** Valid Accounts (T1078) 

   - **Sub-Technique:** External Remote Services (T1078.002) 

   - **Mapping Rationale:** Attacker successfully logs into an external service (SSH/VPN) after brute-force guessing valid credentials. 

   - **Evidence Supporting Mapping:** Successful login log (Event ID 4624 or SSH Accepted publickey/password) from a previously flagged bruteforce source IP. 

   - **Status:** VERIFIED 

## **6. Detection** 

Detection Signals & Data Sources 

- **Windows Event Logs:** Security Log (Event ID 4625 - Failed Logon, Event ID 4624 - Successful Logon, Event ID 4740 - Account Lockout). 

- **Linux Security Logs:** /var/log/auth.log or /var/log/secure (sshd[PID]: Failed password for..., sshd[PID]: Accepted password for...). 

- **Web Server Logs:** Nginx/Apache access logs (POST /login returning 401 Unauthorized or 403 Forbidden). 

- **IAM / Cloud Identity Logs:** AWS CloudTrail / Azure AD Sign-in Logs (ResultType: 50126 - Invalid username or password). 

Normalized Fields 

- src_ip: Source IPv4/IPv6 address. 

- dest_ip: Target host destination IP. 

- user: Target username string. 

- event_id: Normalized event type code (e.g., authentication_failure, authentication_success, account_lockout). 

- app: Authentication service (sshd, active_directory, web_app). 

- http_user_agent: HTTP header value. 

Correlation Logic & Rule Hypotheses 

- **Hypothesis 1 (Direct Brute Force):** IF count(event_id = 'authentication_failure') > 20 grouped by src_ip and user within 5 minutes THEN flag ALERT_BRUTE_FORCE_DIRECT. 

- **Hypothesis 2 (Password Spraying):** IF count(distinct user) > 15 AND count(event_id = 'authentication_failure') > 15 grouped by src_ip within 10 minutes THEN flag ALERT_PASSWORD_SPRAY. 

- **Hypothesis 3 (Brute Force Success):** IF ALERT_BRUTE_FORCE_DIRECT OR ALERT_PASSWORD_SPRAY is TRUE for src_ip AND followed by event_id = 'authentication_success' from same src_ip within 30 minutes THEN flag ALERT_BRUTE_FORCE_SUCCESSFUL_COMPROMISE (High Severity) 

False Positive & Validation Checks 

- **Internal Service Account Validation:** Check if src_ip belongs to a known internal IP range associated with vulnerability scanners, legitimate automated batch processes, or service accounts using cached expired credentials. 

- **User Credential Cache Check:** Analyze if authentication failures originate from a single user identity across multiple internal endpoints, 

indicating an updated domain password not yet synced to mobile clients or persistent network mounts. 

- **Geographic & ISP Baseline Verification:** Cross-reference src_ip against ASN and threat intelligence feeds to distinguish malicious TOR exit nodes / commercial proxy services from legitimate corporate VPN gateways. 

- **Time-Window & Cadence Analysis:** Verify request intervals; nonuniform, high-velocity bursts confirm automated tooling, whereas periodic fixed-interval failures (e.g., exactly every 15 minutes) point to misconfigured local cron jobs or software services. 

#### **7. Evidence Requirements** 

Primary Required Evidence 

1. **Raw Authentication Log Exports:** Unaltered log lines capturing timestamps, source IP, target identity, and explicit failure/success status codes. 

2. **Target System Identification:** Hostnames, domain names, and exact service ports subjected to the login attempts. 

3. **Verified Success Record:** Confirmation from backend database or central auth broker verifying whether any attempt resulted in an active session state. 

Supporting Evidence 

- **Network Flow Records / PCAP:** Network capture showing TCP handshake details, payload length, and connection frequencies from src_ip. 

- **Multi-Factor Authentication (MFA) Logs:** MFA push notification logs showing rejected pushes or MFA exhaustion attempts (MFA fatigue). 

- **Post-Authentication Endpoint Telemetry:** EDR execution logs (Sysmon Event ID 1, process creation) for the targeted host within 1 hour postsuccessful authentication. 

Evidence-to-Claim Relationship 

- **To Claim "Brute Force / Spray Attempt in Progress":** Requires raw authentication log records demonstrating failure counts exceeding defined thresholds (>20 failures/5 min or >15 distinct accounts/10 min) from a common source IP or directed at a common target service. 

- **To Claim "Successful Account Compromise":** Requires a verified authentication success record (Event ID 4624 or SSH Accepted password) originating from the same source IP (src_ip) that previously generated the brute-force failure pattern. 

- **To Claim "Post-Compromise Activity / Lateral Movement":** Requires post-authentication endpoint telemetry (process lineage, command-line arguments, secondary network connections) linked by timestamp and user session ID directly to the verified successful login event. 

Preservation & Reference Consideration 

- **Cryptographic Integrity & Chain of Custody:** Log files and PCAPs must be exported from central log storage and hashed using SHA-256 immediately upon collection to preserve evidence integrity and maintain chain-of-custody standards. 

- **Time Synchronization & Clock Skew Verification:** All log timestamps across endpoints, domain controllers, and firewalls must be normalized against a reliable Network Time Protocol (NTP) reference, with allowable clock skew documented (target threshold within $\pm 100\text{ ms}$). 

- **Retention & Storage Isolation:** Primary evidence artifacts must be written to write-once-read-many (WORM) storage or secure, isolated evidence repositories with restricted access controls to prevent accidental deletion, alteration, or overwrite during active investigation. 

### **8. Incident Response Lifecycle** 

Phase 1 - Preparation 

- **Playbook Requirements:** Active Playbook-BF-01: Credential Access and Brute Force Response. 

- **Readiness Checks:** Verify Central Log Management (SIEM) ingest rate for domain controllers, SSH bastions, and edge web proxy logs. 

- **Logging/Evidence Configuration:** Ensure Windows Audit Policy has Audit Logon set to Success and Failure. Ensure Linux sshd_config has LogLevel VERBOSE. 

- **Notification / Escalation Matrix:** Pre-configured alert routing to Tier-1 SOC analysts for failure bursts, and Tier-2 / Incident Commander for successful brute-force compromises. 

- **Expected Preparation Output:** Configured correlation rules, operational SIEM dashboards, and active IP blocklists ready at perimeter firewalls. 

##### Phase 2 - Detection & Analysis 

- **Intake & Normalization:** Ingest auth failure logs; map fields to src_ip, user, event_id, and timestamp. 

- **Triage & Analysis:** 

   - Validate if src_ip is a known internal scanner, VPN exit node, or authorized automated testing tool (exclude false positives). 

   - Check scope: Determine how many accounts were targeted and whether the attack was concentrated or distributed. 

- **Correlation & Candidates:** Correlate src_ip with threat intelligence sources; assign MITRE ATT&CK candidate tags (T1110.001 or T1110.002). 

- **Confirmed Facts vs. Hypotheses:** 

   - _Fact:_ 198.51.100.42 generated 450 failed logins against user admin between 14:00:00 and 14:10:00 UTC. 

   - _Hypothesis:_ The source is an automated external botnet script attempting brute-force entry. 

- **Phase 3 Handoff Requirements:** Handoff requires a confirmed scope of targeted accounts, identified source IP(s), and absolute confirmation whether a successful authentication occurred (Event ID 4624 / Accepted password). 

#### Phase 3 - Containment, Eradication & Recovery 

##### _Attack-Specific Containment_ 

- **Network Blocking:** Dynamically apply drop rules for src_ip (198.51.100.42) at perimeter firewalls / WAF. 

- **Account Action:** Temporarily disable or enforce immediate lockout on affected target user accounts. 

- **Session Termination:** Force-terminate active sessions associated with compromised or targeted user accounts across all endpoints and identity providers. 

- **Host Isolation:** If post-login lateral movement is detected, isolate the compromised target host from the network 

#### _Eradication_ 

- **Password Reset:** Execute forced password reset across all targeted and potentially compromised user accounts using strong entropy requirements. 

- **Token / Session Revocation:** Invalidate all active OAuth tokens, Kerberos tickets (TGT), and Web session cookies for affected identities. 

- **SSH / Access Key Audit:** Inspect /home/<user>/.ssh/authorized_keys and enterprise IAM API keys to ensure the attacker did not establish persistent secondary access mechanisms. 

#### _Recovery & Verification_ 

- **Prerequisites:** All containment IP blocks active; forced password resets verified in Identity Provider database; host EDR scan clean. 

- **Recovery Verification Steps:** 

   1. Verify zero inbound traffic from blocked src_ip at perimeter firewalls. 

   2. Execute backend check verifying user accounts are restored to Active status with newly generated passwords. 

   3. Monitor target host authentication logs for 24 hours to confirm return to baseline activity levels. 

- **Expected Evidence/Results:** Clean auth logs, verified IP drop logs, and validated user credential updates. 

#### Phase 4 - Post-Incident Activity 

- **Final Report Information:** Timeline of attack, target accounts, source IP attributions, total failure count, successful logins (if any), and containment response duration. 

- **Notification Review:** Review whether regulatory body notifications (e.g., GDPR, HIPAA) or internal executive briefings are required if user credentials/data were compromised. 

- **Lessons Learned:** Evaluate whether account lockout thresholds were too high, if MFA was enforced on all accessed services, or if rate-limiting failed at the API/web layer. 

- **Improvement Actions:** 

   - Implement CAPTCHA or Web Application Firewall (WAF) ratelimiting on login forms. 

   - Enforce mandatory Multi-Factor Authentication (MFA) across all remote services. 

   - Adjust SIEM correlation rules to lower the threshold for alerting on password spraying. 

#### **9. Severity & Scope Considerations** 

**Target Account Privilege:** Brute-force targeting standard domain users vs. Domain Administrators or cloud system superusers (root, global-admin). 

**Authentication Outcome:** Failed brute force attempts remain **Low / Medium** severity depending on volume. Any brute force attempt followed by a confirmed **successful authentication** escalates the incident immediately to **High / Critical** severity. 

**Exposed Target Environment:** Targets located on public, perimeter-facing nodes vs. internal restricted network segments (internal brute forcing implies an existing breach inside the perimeter). 

**Account Lockout Impact:** High-volume spraying causing widespread business operational denial-of-service via automated account lockouts across critical personnel. 

#### **10. AI Recommendation Guidance** 

What AI May Recommend (Advisory) 

- Identify and present correlated log summaries showing brute-force trends. 

- Suggest candidate MITRE ATT&CK technique tags (e.g., T1110.001) based on event patterns. 

- Recommend blocking specific source IPs or applying temporary rate limits. 

- Flag anomalous User-Agent strings or geographic login anomalies for human review. 

What Must Remain a Human / Backend Decision 

- **Final Incident Severity:** The human responder must confirm final severity based on context. 

- **Verification of Facts:** AI suggestions must never automatically convert a hypothesis (e.g., "This looks like a successful login") into a verified incident fact without explicit backend confirmation. 

- **Execution of Containment Actions:** High-impact responses (disabling user accounts, applying perimeter firewall blocks, isolating servers) require human authorization or verified backend automation policy approval. 

- **Phase Progression:** Advancing the incident state from Phase 2 (Detection) to Phase 3 (Containment) requires explicit responder confirmation. 

### **11. Edge Cases & Common Ambiguities** 

**Edge Case 1: Misconfigured Internal Service** 

- **Cause / Description:** An internal service, service account, or batch script has an expired password saved in memory and repeatedly attempts authentication. 

- **Triage & Analysis Resolution:** Verify src_ip. If internal, trace the process generating requests. Check if attempts use a single static password repeatedly rather than a dictionary list. 

###### **Edge Case 2: User Password Change Propagation** 

- **Cause / Description:** A legitimate employee updates their Active Directory password, but their mobile device or secondary client continues sending old credentials. 

- **Triage & Analysis Resolution:** Analyze request frequency and UserAgent. Single user target with bursts matching standard mobile sync intervals (e.g., every 5 minutes) indicates client credential cache issues. 

###### **Edge Case 3: Distributed Password Spraying (Proxy / Botnet)** 

- **Cause / Description:** Attacker uses hundreds of distinct exit IPs to submit single password guesses, evading single-IP rate limits. 

- **Triage & Analysis Resolution:** Aggregate authentication failure logs by _target user account_ and _time window_ rather than purely by src_ip. 

###### **Edge Case 4: Incomplete / Missing Logs** 

- **Cause / Description:** Log source drops events due to buffer overflows during high-volume brute-force attacks. 

- **Triage & Analysis Resolution:** Cross-reference network flow logs (netflow packet/byte counts) with auth logs to estimate dropped connection volumes. 

###### **Edge Case 5: Duplicate Alerts** 

- **Cause / Description:** Multiple SIEM rules trigger simultaneously for the same brute-force event (e.g., rule for SSH, rule for IP, rule for User). 

- **Triage & Analysis Resolution:** Correlate and deduplicate alerts under a single primary Incident ID using src_ip and timestamp bounds in the backend incident management system. 

### **12. Fact vs. Hypothesis Separation** 

**Observed Fact:** Linux system /var/log/auth.log recorded 1,200 sshd failed authentication attempts for user root from source IP 198.51.100.42 between 10:00:00 UTC and 10:05:00 UTC. 

**Hypothesis:** The source IP 198.51.100.42 is an automated scanner performing an external brute-force dictionary attack against the SSH service. 

**Evidence Needed:** PCAP/Network flow logs confirming automated request bursts, firewall logs, and central auth records confirming whether any attempt logged an Accepted password status. 

**AI Recommendation:** Advisory: Recommend blocking IP 198.51.100.42 at perimeter firewall and verifying SSH root login policy (PermitRootLogin no). 

**Human Decision:** SOC Analyst approves perimeter IP block, confirms root direct login is disabled, and updates incident severity to Low (since all attempts failed). 

### **13. Sources / References** 

1. **MITRE ATT&CK Framework:** Technique T1110 (Brute Force) - <u>https://attack.mitre.org/techniques/T1110/</u> 

2. **NIST Special Publication 800-61 Rev. 2:** Computer Security Incident Handling Guide - <u>https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.80061r2.pdf</u> 

3. **Microsoft Security Operations Documentation:** Monitoring Windows Security Event Log for Credential Access (Event IDs 4625, 4624, 4740). 

4. **OWASP Foundation:** Credential Stuffing and Automated Threat Handbook (OAT-008, OAT-011). 

5. **Project Technical Specification:** System Logging and Incident Response Requirements v2.4. 

