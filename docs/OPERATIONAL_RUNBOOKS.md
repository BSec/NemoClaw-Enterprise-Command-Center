# NemoClaw Enterprise Command Center - Operational Workflows & Runbooks

**Version**: 2.1.0  
**Classification**: Internal Use - Operations  
**Last Updated**: March 27, 2026  
**Audience**: DevOps, SRE, Security Operations

---

## 1. Operational Overview

### 1.1 System Components Health

| Component | Criticality | Health Check | Alert Threshold |
|-----------|-------------|----------------|-----------------|
| **Web Application** | Critical | HTTP 200 on /health | 3 consecutive failures |
| **Database** | Critical | Connection + Query | Connection timeout > 5s |
| **Redis Cache** | High | PING response | 2 consecutive failures |
| **Secrets Vault** | Critical | Seal status | Unseal required |
| **NemoClaw Instances** | Medium | SSH connectivity | 50% instances offline |
| **GPU Cluster** | Medium | NVML queries | GPU temp > 85°C |

### 1.2 Support Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| **Primary On-Call** | oncall@company.com | +1-555-0100 |
| **Security Team** | security@company.com | +1-555-0101 |
| **Platform Lead** | platform-lead@company.com | +1-555-0102 |
| **Engineering Manager** | eng-mgr@company.com | +1-555-0103 |

---

## 2. Deployment Workflows

### 2.1 Standard Deployment

**Pre-Deployment Checklist**:
- [ ] All tests passing in staging
- [ ] Database migrations reviewed
- [ ] Secrets rotation not required
- [ ] Maintenance window announced
- [ ] Rollback plan documented

**Deployment Steps**:

```bash
#!/bin/bash
# deploy.sh - Standard Deployment Workflow

set -euo pipefail

VERSION=$1
ENVIRONMENT=$2

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 1. Pre-deployment health check
log "Step 1: Checking current system health"
curl -sf http://localhost:8501/health/ready || {
    log "ERROR: System not healthy, aborting deployment"
    exit 1
}

# 2. Database backup
log "Step 2: Creating database backup"
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > \
    /backups/pre-deploy-$(date +%Y%m%d-%H%M%S).sql

# 3. Deploy new version
log "Step 3: Deploying version $VERSION"
kubectl set image deployment/nemoclaw-gateway \
    gateway=nemoclaw/gateway:$VERSION

# 4. Wait for rollout
log "Step 4: Waiting for rollout to complete"
kubectl rollout status deployment/nemoclaw-gateway --timeout=300s

# 5. Post-deployment verification
log "Step 5: Running health checks"
sleep 30  # Allow startup
for i in {1..5}; do
    if curl -sf http://localhost:8501/health/ready; then
        log "Health check passed"
        break
    fi
    if [ $i -eq 5 ]; then
        log "ERROR: Health checks failed after deployment"
        log "Initiating rollback..."
        kubectl rollout undo deployment/nemoclaw-gateway
        exit 1
    fi
    sleep 10
done

# 6. Run smoke tests
log "Step 6: Running smoke tests"
pytest tests/smoke/ -v || {
    log "ERROR: Smoke tests failed"
    kubectl rollout undo deployment/nemoclaw-gateway
    exit 1
}

log "Deployment completed successfully!"
```

### 2.2 Database Migration

**Migration Checklist**:
- [ ] Migration tested in staging
- [ ] Backup created
- [ ] Rollback script prepared
- [ ] No long-running transactions

**Migration Procedure**:

```bash
#!/bin/bash
# migrate.sh - Database Migration Workflow

VERSION=$1

# 1. Create backup
echo "Creating backup..."
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > \
    /backups/pre-migration-$(date +%Y%m%d-%H%M%S).sql

# 2. Run migrations in dry-run mode first
echo "Dry-run migration..."
python -m alembic upgrade $VERSION --sql > /tmp/migration-dryrun.sql

# 3. Review migration script
echo "Review the migration script:"
head -50 /tmp/migration-dryrun.sql
echo "..."
read -p "Continue with migration? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration aborted"
    exit 1
fi

# 4. Execute migration
echo "Executing migration..."
python -m alembic upgrade $VERSION

# 5. Verify
echo "Verifying migration..."
python -m alembic current

# 6. Health check
curl -sf http://localhost:8501/health/ready

echo "Migration completed successfully"
```

### 2.3 Rollback Procedure

**When to Rollback**:
- Health checks failing after deployment
- Critical bugs discovered
- Performance degradation > 50%
- Security issues

**Rollback Steps**:

```bash
#!/bin/bash
# rollback.sh - Emergency Rollback

# 1. Identify current and previous versions
CURRENT_VERSION=$(kubectl get deployment nemoclaw-gateway \
    -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d: -f2)
PREVIOUS_VERSION=$(kubectl rollout history deployment/nemoclaw-gateway \
    | grep -B1 "$CURRENT_VERSION" | head -1 | awk '{print $1}')

echo "Current: $CURRENT_VERSION"
echo "Rolling back to: $PREVIOUS_VERSION"

# 2. Execute rollback
kubectl rollout undo deployment/nemoclaw-gateway

# 3. Verify rollback
kubectl rollout status deployment/nemoclaw-gateway

# 4. Health check
curl -sf http://localhost:8501/health/ready || {
    echo "CRITICAL: Rollback failed, manual intervention required"
    alert_oncall
    exit 1
}

echo "Rollback completed successfully"
```

---

## 3. Incident Response Runbooks

### 3.1 P1 - Critical Incident: System Down

**Severity**: Critical  
**Response Time**: 15 minutes  
**SLA**: 1 hour to resolve or escalate

#### Detection
- Alert: `health_critical`
- Symptom: All health checks failing
- Impact: Complete system unavailability

#### Response Steps

**Step 1: Acknowledge (0-5 min)**
```bash
# Acknowledge alert
curl -X POST https://pagerduty.com/acknowledge \
  -d '{"incident_id": "INC-001", "user": "oncall-engineer"}'

# Create incident channel
slack create-channel incident-$(date +%Y%m%d-%H%M)
```

**Step 2: Initial Assessment (5-15 min)**
```bash
# Check pod status
kubectl get pods -l app=nemoclaw-gateway

# Check logs
kubectl logs -l app=nemoclaw-gateway --tail=100

# Check database connectivity
kubectl exec -it deployment/nemoclaw-gateway -- \
  python -c "from services.instance_manager import check_db_connection; print(check_db())"

# Check external dependencies
curl -sf http://vault:8200/v1/sys/health
curl -sf http://redis:6379/ping
```

**Step 3: Recovery Actions**

*Scenario A: Application Error*
```bash
# Restart pods
kubectl rollout restart deployment/nemoclaw-gateway

# Check recovery
kubectl rollout status deployment/nemoclaw-gateway
```

*Scenario B: Database Issue*
```bash
# Check database status
pg_isready -h $DB_HOST

# Check connection pool
kubectl exec -it deployment/nemoclaw-gateway -- \
  python -c "from utils.db import check_pool_status; print(check_pool())"

# Restart database if necessary
# (Requires manual approval for production DB)
```

*Scenario C: Infrastructure Failure*
```bash
# Scale up new nodes
kubectl scale deployment nemoclaw-gateway --replicas=0
kubectl scale deployment nemoclaw-gateway --replicas=3

# Verify load balancer
kubectl get svc nemoclaw-gateway-lb
```

**Step 4: Post-Incident**
- Document timeline in incident log
- Schedule post-mortem within 24 hours
- Update runbook if needed

---

### 3.2 P2 - High Incident: Security Breach Suspected

**Severity**: High  
**Response Time**: 30 minutes  
**SLA**: 4 hours to contain

#### Detection
- Alert: `security_anomaly_detected`
- Symptom: Unauthorized access attempts, policy violations
- Impact: Potential data compromise

#### Response Steps

**Step 1: Immediate Containment**
```bash
# Enable emergency mode (blocks all non-admin access)
kubectl exec -it deployment/nemoclaw-gateway -- \
  python -c "from services.emergency import enable_lockdown; enable_lockdown()"

# Revoke all active sessions
kubectl exec -it deployment/redis -- redis-cli FLUSHDB

# Rotate critical secrets
vault operator rotate
```

**Step 2: Investigation**
```bash
# Collect audit logs for timeframe
python scripts/export_audit.py \
  --start "$(date -d '1 hour ago' -Iminutes)" \
  --end "$(date -Iminutes)" \
  --format json \
  --output /tmp/audit-$(date +%Y%m%d-%H%M).json

# Analyze suspicious activity
python scripts/analyze_audit.py \
  --input /tmp/audit-$(date +%Y%m%d-%H%M).json \
  --report /tmp/analysis-$(date +%Y%m%d-%H%M).txt

# Check for data exfiltration
kubectl logs -l app=nemoclaw-gateway | grep -i "export\|download\|unauthorized"
```

**Step 3: Evidence Preservation**
```bash
# Snapshot database
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > \
  /forensics/db-snapshot-$(date +%Y%m%d-%H%M).sql

# Collect container logs
kubectl logs -l app=nemoclaw-gateway --since=24h > \
  /forensics/logs-$(date +%Y%m%d-%H%M).txt

# Save network flows
kubectl exec -it deployment/nemoclaw-gateway -- \
  tcpdump -w /forensics/capture-$(date +%Y%m%d-%H%M).pcap
```

**Step 4: Recovery**
```bash
# After investigation complete
# Reset passwords for affected users
python scripts/reset_passwords.py --users affected-users.txt

# Re-enable normal operations
kubectl exec -it deployment/nemoclaw-gateway -- \
  python -c "from services.emergency import disable_lockdown; disable_lockdown()"
```

---

### 3.3 P3 - Medium Incident: Performance Degradation

**Severity**: Medium  
**Response Time**: 1 hour  
**SLA**: 8 hours to resolve

#### Detection
- Alert: `performance_degraded`
- Symptom: Response time > 2s, error rate > 1%
- Impact: Slow user experience

#### Response Steps

**Step 1: Diagnosis**
```bash
# Check resource utilization
kubectl top pods -l app=nemoclaw-gateway

# Check database performance
psql -h $DB_HOST -U $DB_USER -c "
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;"

# Check cache hit rate
kubectl exec -it deployment/redis -- redis-cli info stats | grep hit_rate

# Analyze slow queries
kubectl logs -l app=nemoclaw-gateway | grep "slow_query"
```

**Step 2: Mitigation**

*Scenario A: High CPU*
```bash
# Scale horizontally
kubectl scale deployment nemoclaw-gateway --replicas=5

# Enable auto-scaling
kubectl autoscale deployment nemoclaw-gateway \
  --min=3 --max=10 --cpu-percent=70
```

*Scenario B: Database Bottleneck*
```bash
# Kill long-running queries
psql -h $DB_HOST -U $DB_USER -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
AND now() - query_start > interval '5 minutes';"

# Add index if missing query pattern identified
# (Review with DBA first)
```

*Scenario C: Memory Leak*
```bash
# Restart pods to free memory
kubectl rollout restart deployment/nemoclaw-gateway

# Monitor for recurrence
watch -n 30 'kubectl top pods -l app=nemoclaw-gateway'
```

---

## 4. Maintenance Procedures

### 4.1 Daily Health Check

**Schedule**: 09:00 UTC daily  
**Duration**: 15 minutes

```bash
#!/bin/bash
# daily-health-check.sh

echo "=== Daily Health Check ==="
echo "Date: $(date)"

# Check system health
echo "[1/5] System Health"
curl -sf http://localhost:8501/health/ready && echo "✓ Healthy" || echo "✗ Unhealthy"

# Check database
echo "[2/5] Database"
pg_isready -h $DB_HOST && echo "✓ Connected" || echo "✗ Disconnected"

# Check cache
echo "[3/5] Redis Cache"
kubectl exec -it deployment/redis -- redis-cli ping && echo "✓ Available" || echo "✗ Unavailable"

# Check disk space
echo "[4/5] Disk Space"
df -h | grep -E "(Filesystem|/data)"

# Check certificates
echo "[5/5] SSL Certificates"
echo | openssl s_client -servername api.nemoclaw.internal \
  -connect api.nemoclaw.internal:443 2>/dev/null | \
  openssl x509 -noout -dates | grep notAfter

echo "=== Check Complete ==="
```

### 4.2 Weekly Security Review

**Schedule**: Every Monday 10:00 UTC  
**Duration**: 30 minutes

**Checklist**:
- [ ] Review failed login attempts
- [ ] Check for privilege escalations
- [ ] Verify audit log integrity
- [ ] Review access control changes
- [ ] Check for new vulnerabilities (CVE scan)
- [ ] Verify backup completion

```bash
#!/bin/bash
# weekly-security-review.sh

echo "=== Weekly Security Review ==="

# Failed logins
echo "[1/6] Failed Login Attempts (Last 7 days)"
psql -h $DB_HOST -U $DB_USER -c "
SELECT DATE(timestamp) as date, COUNT(*) as attempts
FROM audit_logs
WHERE event_type = 'user_login'
AND success = FALSE
AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY date;"

# Privilege changes
echo "[2/6] Privilege Changes (Last 7 days)"
psql -h $DB_HOST -U $DB_USER -c "
SELECT timestamp, user_id, action, description
FROM audit_logs
WHERE event_type IN ('user_update', 'role_change')
AND timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;"

# Audit integrity
echo "[3/6] Audit Log Integrity"
python scripts/verify_audit_integrity.py

# Access changes
echo "[4/6] Access Control Changes"
git log --since="1 week ago" --oneline -- policies/

# CVE scan
echo "[5/6] Vulnerability Scan"
safety check -r requirements.txt

# Backup status
echo "[6/6] Backup Status"
ls -lah /backups/ | tail -7

echo "=== Review Complete ==="
```

### 4.3 Monthly Maintenance

**Schedule**: First Sunday of month 02:00 UTC  
**Duration**: 2 hours

**Tasks**:
- [ ] Database vacuum and analyze
- [ ] Log rotation and archival
- [ ] Certificate renewal check
- [ ] Dependency updates review
- [ ] Performance baseline update
- [ ] Disaster recovery test

```bash
#!/bin/bash
# monthly-maintenance.sh

echo "=== Monthly Maintenance ==="

# Database maintenance
echo "[1/6] Database Maintenance"
psql -h $DB_HOST -U $DB_USER -c "VACUUM ANALYZE;"

# Log rotation
echo "[2/6] Log Rotation"
logrotate -f /etc/logrotate.d/nemoclaw

# Certificate check
echo "[3/6] Certificate Renewal Check"
python scripts/check_certificates.py --renewal-warning-days 30

# Dependency check
echo "[4/6] Dependency Updates"
pip list --outdated > /tmp/outdated-packages.txt
cat /tmp/outdated-packages.txt

# Performance baseline
echo "[5/6] Performance Baseline"
python scripts/collect_performance_baseline.py

# DR test (dry-run)
echo "[6/6] DR Test (Dry-Run)"
python scripts/test_dr_recovery.py --dry-run

echo "=== Maintenance Complete ==="
```

---

## 5. Backup & Recovery

### 5.1 Backup Strategy

| Data Type | Frequency | Retention | Method |
|-----------|-----------|-----------|--------|
| **Database** | Hourly | 30 days | pg_dump + WAL archiving |
| **Configuration** | On change | 90 days | Git + S3 |
| **Audit Logs** | Real-time | 7 years | Immutable S3 |
| **Secrets** | Daily | 7 days | Vault snapshot |

### 5.2 Backup Verification

```bash
#!/bin/bash
# verify-backup.sh

BACKUP_FILE=$1

echo "Verifying backup: $BACKUP_FILE"

# Check file integrity
if ! pg_restore --list "$BACKUP_FILE" > /dev/null 2>&1; then
    echo "ERROR: Backup file is corrupted"
    exit 1
fi

# Test restore to temporary database
TEMP_DB="test_restore_$(date +%s)"
createdb $TEMP_DB
if pg_restore --dbname=$TEMP_DB "$BACKUP_FILE"; then
    echo "✓ Restore test passed"
    dropdb $TEMP_DB
else
    echo "✗ Restore test failed"
    dropdb $TEMP_DB
    exit 1
fi

echo "Backup verification complete"
```

### 5.3 Point-in-Time Recovery

```bash
#!/bin/bash
# pit-recovery.sh

TARGET_TIME=$1  # Format: 2024-03-27 14:30:00

echo "Recovering to: $TARGET_TIME"

# 1. Stop application
kubectl scale deployment nemoclaw-gateway --replicas=0

# 2. Find base backup before target time
BASE_BACKUP=$(ls -t /backups/base/ | while read f; do
    if [[ $f < $TARGET_TIME ]]; then
        echo $f
        break
    fi
done)

# 3. Restore base backup
echo "Restoring base backup: $BASE_BACKUP"
pg_restore --clean --dbname=$DB_NAME /backups/base/$BASE_BACKUP

# 4. Apply WAL files up to target time
echo "Applying WAL files..."
pg_waldump /wal-archive/ --start-time=$BASE_BACKUP --end-time="$TARGET_TIME" | \
    psql -h $DB_HOST -U $DB_USER $DB_NAME

# 5. Verify recovery
psql -h $DB_HOST -U $DB_USER -c "SELECT MAX(timestamp) FROM audit_logs;"

# 6. Restart application
kubectl scale deployment nemoclaw-gateway --replicas=3

echo "Recovery complete"
```

---

## 6. Monitoring & Alerting

### 6.1 Key Metrics Dashboard

**Grafana Dashboard**: `https://grafana.company.com/d/nemoclaw`  
**Key Metrics**:

| Metric | Warning | Critical | Description |
|--------|---------|----------|-------------|
| **Request Latency** | > 500ms | > 2000ms | p95 response time |
| **Error Rate** | > 1% | > 5% | HTTP 5xx rate |
| **CPU Usage** | > 70% | > 90% | Container CPU |
| **Memory Usage** | > 80% | > 95% | Container memory |
| **Database Connections** | > 80% | > 95% | Pool utilization |
| **Disk Usage** | > 80% | > 90% | Data volume |
| **Certificate Expiry** | < 30 days | < 7 days | SSL cert validity |

### 6.2 Alert Routing

| Alert Severity | PagerDuty | Slack | Email |
|----------------|-----------|-------|-------|
| **Critical (P1)** | Immediate | #alerts-critical | On-call only |
| **High (P2)** | 15 min | #alerts-high | Security + Ops |
| **Medium (P3)** | 1 hour | #alerts-medium | Ops team |
| **Low (P4)** | Business hours | #alerts-low | Daily digest |

### 6.3 Alert Runbook Links

Configure alert notifications to include links to relevant runbooks:

```yaml
# alertmanager-config.yaml
receivers:
  - name: 'critical-alerts'
    pagerduty_configs:
      - service_key: '<key>'
        description: '{{ .GroupLabels.alertname }}'
        details:
          runbook_url: 'https://wiki.company.com/runbooks/{{ .GroupLabels.runbook }}'
```

---

## 7. Troubleshooting Guide

### 7.1 Common Issues

#### Issue: High Memory Usage

**Symptoms**: OOMKilled pods, slow response times

**Diagnosis**:
```bash
# Check memory usage per pod
kubectl top pods -l app=nemoclaw-gateway --sort-by=memory

# Check for memory leaks
kubectl logs -l app=nemoclaw-gateway | grep "MemoryError\|OutOfMemory"

# Profile memory usage
python -m memory_profiler app.py
```

**Resolution**:
```bash
# Quick fix: Restart pods
kubectl rollout restart deployment/nemoclaw-gateway

# Long-term: Scale up memory limits
kubectl patch deployment nemoclaw-gateway -p '{"spec":{"template":{"spec":{"containers":[{"name":"gateway","resources":{"limits":{"memory":"2Gi"}}}]}}}}'
```

#### Issue: Database Connection Pool Exhausted

**Symptoms**: Connection timeout errors, slow queries

**Diagnosis**:
```bash
# Check active connections
psql -h $DB_HOST -U $DB_USER -c "
SELECT count(*), state
FROM pg_stat_activity
GROUP BY state;"

# Check pool status
python -c "from utils.db import check_pool; print(check_pool())"
```

**Resolution**:
```bash
# Increase pool size
# Edit config: database.pool_size = 20

# Kill idle connections
psql -h $DB_HOST -U $DB_USER -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '1 hour';"
```

#### Issue: Certificate Expired

**Symptoms**: SSL handshake failures, security warnings

**Resolution**:
```bash
# Check certificate expiry
echo | openssl s_client -connect api.nemoclaw.internal:443 2>/dev/null | \
  openssl x509 -noout -dates

# Renew certificate
certbot renew --force-renewal

# Verify renewal
kubectl rollout restart deployment/nemoclaw-gateway
```

---

## 8. Security Operations

### 8.1 Access Review Process

**Frequency**: Monthly  
**Owner**: Security Team

**Procedure**:
1. Generate access review report
2. Identify inactive users (>90 days)
3. Review privilege escalations
4. Verify role assignments
5. Document findings

```bash
#!/bin/bash
# access-review.sh

echo "=== Monthly Access Review ==="

# Inactive users
echo "[1/5] Inactive Users (>90 days)"
psql -h $DB_HOST -U $DB_USER -c "
SELECT user_id, email, last_login
FROM users
WHERE last_login < NOW() - INTERVAL '90 days'
OR last_login IS NULL;"

# Admin users
echo "[2/5] Admin Users"
psql -h $DB_HOST -U $DB_USER -c "
SELECT user_id, email, name, created_at
FROM users
WHERE role = 'admin'
AND is_active = TRUE;"

# Recent privilege changes
echo "[3/5] Recent Privilege Changes (30 days)"
psql -h $DB_HOST -U $DB_USER -c "
SELECT timestamp, user_id, old_values, new_values
FROM audit_logs
WHERE event_type = 'user_update'
AND timestamp > NOW() - INTERVAL '30 days'
AND (old_values->>'role' IS DISTINCT FROM new_values->>'role');"

# External access
echo "[4/5] External Access (VPN/SSH)"
cat /var/log/auth.log | grep -i "accepted" | tail -20

# Service accounts
echo "[5/5] Service Account Activity"
psql -h $DB_HOST -U $DB_USER -c "
SELECT user_id, last_login
FROM users
WHERE email LIKE '%@service%'
ORDER BY last_login;"

echo "=== Review Complete ==="
```

### 8.2 Security Incident Response

**Classification**:
- **S1**: Data breach confirmed
- **S2**: Unauthorized access suspected
- **S3**: Policy violation detected
- **S4**: Security alert (informational)

**Response Matrix**:

| Class | Notification | Action | Timeline |
|-------|--------------|--------|----------|
| S1 | Immediate (15 min) | Lockdown + Investigation | 1 hour |
| S2 | Urgent (30 min) | Investigation + Monitoring | 4 hours |
| S3 | Same day | Review + Remediation | 24 hours |
| S4 | Weekly digest | Review | 7 days |

---

## 9. Change Management

### 9.1 Change Types

| Type | Approval | Testing | Window |
|------|----------|---------|--------|
| **Standard** | Team Lead | Automated | Business hours |
| **Normal** | Manager | Staging + Automated | Maintenance window |
| **Emergency** | On-call | Minimal | Immediate |
| **Security** | Security Team | Automated + Manual | Immediate |

### 9.2 Change Request Template

```markdown
## Change Request: CR-YYYY-NNN

**Title**: Brief description
**Type**: Standard/Normal/Emergency/Security
**Requester**: Name
**Date**: YYYY-MM-DD
**Window**: Start - End

### Description
Detailed description of the change

### Impact Assessment
- Services affected: List
- Users affected: Count
- Downtime expected: Duration
- Rollback time: Duration

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Staging validation complete
- [ ] Security scan passing

### Rollback Plan
Detailed rollback procedure

### Approvals
- [ ] Technical Review: Name, Date
- [ ] Security Review: Name, Date
- [ ] Manager Approval: Name, Date
```

---

**Version**: 2.1.0  
**Owner**: Platform Operations Team  
**Next Review**: April 27, 2026

---

*End of Operational Workflows & Runbooks*
