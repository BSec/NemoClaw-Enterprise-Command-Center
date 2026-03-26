# NemoClaw Enterprise Command Center - Security Hardening Guide

## 🔐 Security Checklist for Production Deployment

### Pre-Deployment Security Audit

#### 1. Code Security
- [ ] All passwords use PBKDF2 hashing (100k+ iterations)
- [ ] Input validation implemented on all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF tokens implemented
- [ ] Session fixation protection
- [ ] Secure random token generation
- [ ] No hardcoded secrets in code
- [ ] Dependency vulnerability scan (safety, snyk)
- [ ] Static code analysis (bandit, pylint-security)

#### 2. Authentication & Authorization
- [ ] MFA enforced for admin accounts
- [ ] Password complexity requirements (12+ chars)
- [ ] Account lockout after failed attempts (5 tries)
- [ ] Session timeout after 30 min idle
- [ ] Re-authentication for sensitive operations
- [ ] Principle of least privilege for all roles
- [ ] Regular access reviews (quarterly)
- [ ] API key rotation (90 days)

#### 3. Infrastructure Security
- [ ] TLS 1.3 only (disable SSLv2/3, TLS 1.0/1.1)
- [ ] HSTS header enabled
- [ ] WAF configured (OWASP Top 10 rules)
- [ ] DDoS protection enabled
- [ ] Network segmentation (VLANs)
- [ ] Container runs as non-root user
- [ ] Read-only root filesystem
- [ ] Resource limits (CPU/memory)
- [ ] Security scanning (Trivy, Clair)

#### 4. Data Protection
- [ ] Encryption at rest (AES-256)
- [ ] Encryption in transit (TLS 1.3)
- [ ] Database encryption enabled
- [ ] Backup encryption
- [ ] Key rotation schedule (annual)
- [ ] Secure key management (KMS/Vault)
- [ ] Data classification labels
- [ ] Retention policy enforced

#### 5. Audit & Monitoring
- [ ] Centralized logging (SIEM integration)
- [ ] Immutable audit logs
- [ ] Log signing enabled
- [ ] Real-time alerting (PagerDuty/Opsgenie)
- [ ] Failed login monitoring
- [ ] Privilege escalation detection
- [ ] Unusual access pattern alerts
- [ ] 7-year audit retention

#### 6. Health Monitoring
- [ ] Self-assessment system enabled
- [ ] Health check rate limiting configured
- [ ] Anomaly detection active
- [ ] Tamper-resistant integrity validation
- [ ] Remediation suggestions configured

---

## 🏥 Self-Assessment & Health Monitoring

### SecureHealthMonitor Service

The system includes comprehensive self-assessment capabilities that continuously evaluate operational integrity, security posture, and performance stability.

#### Core Features

| Feature | Implementation | Security Benefit |
|---------|----------------|------------------|
| **Tamper-Resistance** | HMAC-SHA256 signatures | Prevents report forgery |
| **Integrity Validation** | SHA-256 checksums | Detects unauthorized changes |
| **Anomaly Detection** | Baseline comparison | Identifies security incidents |
| **Rate Limiting** | 60 checks/minute | Prevents DoS abuse |
| **Execution Isolation** | Thread-based checks | Prevents check interference |
| **Audit Logging** | Sanitized event logs | Forensic traceability |

#### Health Check Categories

```python
# Service Availability (Critical)
check_service_availability()  # Core services, instance connectivity

# Configuration Integrity (Critical)  
check_configuration_integrity()  # File integrity, config validation

# Access Control
check_access_control()  # Auth system, MFA status, role assignments

# Dependency Health (Critical)
check_dependency_health()  # Required packages, versions

# Data Flow
check_data_flow()  # Serialization/deserialization

# Performance
check_performance()  # Response times, resource usage

# Security Posture
check_security_posture()  # Debug mode, crypto availability
```

#### Report Formats

**JSON (SIEM Integration):**
```json
{
  "report_id": "health-20240327000000-abc123",
  "generated_at": "2024-03-27T00:00:00Z",
  "overall_status": "healthy",
  "integrity_hash": "sha256:abc123...",
  "signature": "hmac:def456...",
  "checks": [
    {
      "check_id": "service_availability",
      "status": "healthy",
      "severity": "info",
      "duration_ms": 45.2,
      "message": "All core services available"
    }
  ],
  "summary": {
    "healthy": 5,
    "degraded": 1,
    "critical": 0,
    "total": 6
  }
}
```

#### Anomaly Detection Rules

| Anomaly Type | Detection Method | Severity |
|--------------|------------------|----------|
| Critical Component Failure | Status=CRITICAL + check.critical=True | CRITICAL |
| Sudden Degradation | Status change from HEALTHY → DEGRADED | HIGH |
| Unauthorized Config Change | Integrity hash mismatch | HIGH |
| Performance Regression | Duration > baseline + 2σ | MEDIUM |
| Security Posture Change | Debug mode enabled | HIGH |

#### Remediation Engine

Remediation suggestions are risk-rated and require approval for high-risk actions:

```python
# Low risk - Can be automated
"Review configuration file"
"Check network connectivity"
"Clear session cache"

# Medium risk - Requires notification
"Reload service configuration"
"Update policy rules"
"Restart monitoring agent"

# High risk - Requires explicit approval
"Restart application server"
"Revoke all sessions"
"Disable user accounts"
```

---

## 🚀 Production Deployment Security

### 1. Network Architecture
```
Internet
    ↓
[CDN/DDoS Protection - Cloudflare/AWS Shield]
    ↓
[Load Balancer - TLS Termination]
    ↓
[WAF - AWS WAF/ModSecurity]
    ↓
[Reverse Proxy - Nginx/Traefik]
    ↓
[Application Container - Isolated Network]
    ↓
[Database - Private Subnet]
```

### 2. Nginx Security Configuration
```nginx
# /etc/nginx/conf.d/nemoclaw.conf
server {
    listen 443 ssl http2;
    server_name dashboard.your-domain.com;
    
    # TLS Configuration
    ssl_certificate /etc/ssl/certs/nemoclaw.crt;
    ssl_certificate_key /etc/ssl/private/nemoclaw.key;
    ssl_protocols TLSv1.3;
    ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req zone=login burst=3 nodelay;
    
    # Proxy to Streamlit
    location / {
        proxy_pass http://dashboard:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ \.(env|yaml|json|log)$ {
        deny all;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name dashboard.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Kubernetes Security (if applicable)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nemoclaw-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nemoclaw
  template:
    metadata:
      labels:
        app: nemoclaw
    spec:
      serviceAccountName: nemoclaw-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: dashboard
        image: nemoclaw/gateway:v2.1.0
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
              - ALL
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: nemoclaw-secrets
              key: secret-key
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: tmp
        emptyDir: {}
      - name: logs
        persistentVolumeClaim:
          claimName: nemoclaw-logs
```

## 🔍 Security Monitoring

### 1. SIEM Integration
```python
# Send security events to SIEM
import logging
import json
from pythonjsonlogger import jsonlogger

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s %(user)s %(action)s %(resource)s'
        )
        logHandler.setFormatter(formatter)
        self.logger.addHandler(logHandler)
        self.logger.setLevel(logging.INFO)
    
    def log_auth_event(self, user, action, success, ip_address, details=None):
        self.logger.info("Authentication event", extra={
            "user": user,
            "action": action,
            "success": success,
            "ip_address": ip_address,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        })
```

### 2. Alert Rules
```yaml
# Prometheus AlertManager rules
groups:
- name: security_alerts
  rules:
  - alert: FailedLoginSpike
    expr: increase(failed_logins[5m]) > 10
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Multiple failed login attempts detected"
      
  - alert: PrivilegeEscalation
    expr: privilege_changes > 0
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "User privilege level changed"
      
  - alert: UnauthorizedAccess
    expr: unauthorized_access_attempts > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Unauthorized access attempt detected"
```

## 🔄 Incident Response Plan

### 1. Detection
- Monitor SIEM alerts 24/7
- Automated anomaly detection
- User behavior analytics (UBA)

### 2. Containment
```bash
# Emergency stop script
#!/bin/bash
# stop-all-sandboxes.sh

echo "🚨 EMERGENCY CONTAINMENT"
echo "Stopping all sandboxes..."
curl -X POST http://localhost:8501/api/emergency-stop \
  -H "Authorization: Bearer $EMERGENCY_TOKEN"

echo "Revoking all sessions..."
redis-cli FLUSHDB

echo "Enabling maintenance mode..."
touch /app/config/maintenance.lock

echo "Alerting security team..."
curl -X POST https://pagerduty.com/integration \
  -d '{"severity":"critical","description":"Security incident detected"}'
```

### 3. Recovery
- Restore from verified backups
- Rotate all credentials
- Review access logs
- Post-incident analysis

## 📊 Security Metrics

Track these KPIs monthly:

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Failed Login Rate | < 1% | > 5% |
| MFA Adoption | > 95% | < 80% |
| Vulnerability Patch Time | < 7 days | > 30 days |
| Audit Log Integrity | 100% | < 99% |
| Security Training | > 90% completion | < 70% |

## 🎓 Security Training

### For Developers
- OWASP Top 10
- Secure coding practices
- SAST/DAST tools usage

### For Admins
- Incident response procedures
- Privilege management
- Security monitoring

### For Users
- Phishing awareness
- Password hygiene
- Report suspicious activity

---

**Last Updated**: 2024
**Review Cycle**: Quarterly
**Owner**: Security Team
