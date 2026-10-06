# Distributed Denial of Service (DDoS)

## Description
Adversaries conduct Distributed Denial of Service (DDoS) attacks to degrade or block the availability of targeted services, networks, or applications to legitimate users.

## Common Indicators
- Extreme surges in inbound network traffic exceeding operational baseline
- Service degradation, HTTP 502/503/504 errors, or complete network interface saturation
- High rate of SYN requests, UDP amplification reflections, or DNS amplification packets
- Massive volumes of anomalous HTTP GET/POST requests directed at specific application endpoints

## Typical Evidence / Logs
- Edge firewall, router NetFlow/IPFIX flow statistics
- Web Application Firewall (WAF) and reverse proxy access logs
- Cloud CDN / DDoS mitigation provider telemetry
- Server resource monitoring metrics (CPU, memory, socket exhaustion)

## MITRE ATT&CK Mapping
Technique ID: T1498
Technique Name: Network Denial of Service

## Related NIST Phases
- Detection & Analysis
- Containment, Eradication & Recovery

## Investigation Steps
- Determine the attack vector (Volume-based, Protocol/SYN flood, or Application Layer 7)
- Identify target IP addresses, ports, and URLs experiencing saturation
- Evaluate upstream transit health and ISP traffic metrics
- Coordinate with CDN/upstream DDoS scrubbers for filtering rules
- Assess system availability and integrity

## AI Guidance
AI suggestions require human verification.

## Human Verification
Final NIST phase, severity, ATT&CK mapping, and response decisions are human-reviewed.
