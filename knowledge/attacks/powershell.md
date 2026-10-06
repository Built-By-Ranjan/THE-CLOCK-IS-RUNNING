# PowerShell Execution

## Description
Adversaries may abuse the PowerShell command-line interface and scripting environment for data discovery, execution of malicious scripts, and persistence.

## Common Indicators
- Obfuscated, Base64-encoded command line flags (`-EncodedCommand`, `-enc`, `-w hidden`, `-nop`)
- Script block logging events with suspicious download cradles (`DownloadString`, `IEX`, `Invoke-WebRequest`)
- Unusual parent-child process relationships (e.g., Office application, web server spawning powershell.exe)
- High volume or unauthorized execution in restricted security contexts

## Typical Evidence / Logs
- Windows Event Log: Security (Event ID 4688 - Process Creation)
- Microsoft-Windows-PowerShell/Operational (Event ID 4104 - Script Block Logging, Event ID 4103)
- Sysmon Event ID 1 (Process Create), Event ID 3 (Network Connection)
- Endpoint Detection & Response (EDR) telemetry

## MITRE ATT&CK Mapping
Technique ID: T1059.001
Technique Name: Command and Scripting Interpreter: PowerShell

## Related NIST Phases
- Detection & Analysis
- Containment, Eradication & Recovery

## Investigation Steps
- Decode obfuscated script blocks or command line arguments
- Identify caller/parent process and executing user account
- Inspect network connections initiated by the PowerShell process
- Determine whether secondary payloads were downloaded or executed
- Scope affected endpoints and credentials

## AI Guidance
AI suggestions require human verification.

## Human Verification
Final NIST phase, severity, ATT&CK mapping, and response decisions are human-reviewed.
