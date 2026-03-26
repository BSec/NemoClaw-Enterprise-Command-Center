# NemoClaw Enterprise Command Center - API Specifications

**Version**: 2.1.0  
**Classification**: Internal Use  
**Last Updated**: March 27, 2026  
**Protocol**: RESTful API over HTTPS  
**Base URL**: `https://api.nemoclaw.internal/v2`  

---

## 1. API Overview

### 1.1 Authentication

All API requests require authentication using **JWT Bearer tokens**.

**Header Format**:
```
Authorization: Bearer <jwt_token>
```

**Token Acquisition**:
1. Authenticate via `/auth/login` endpoint
2. Receive JWT token in response
3. Include token in all subsequent requests

**Token Properties**:
- **Type**: JWT (JSON Web Token)
- **Algorithm**: RS256 (RSA with SHA-256)
- **Expiry**: 8 hours
- **Refresh**: Available via `/auth/refresh`

### 1.2 Security Headers

All responses include the following security headers:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

### 1.3 Rate Limiting

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Authentication | 5 requests | 5 minutes |
| General API | 100 requests | 1 minute |
| Health Checks | 60 requests | 1 minute |
| Export | 10 requests | 1 minute |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1711533600
```

### 1.4 Response Format

All responses follow this standard format:

**Success Response**:
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2024-03-27T10:00:00Z",
    "request_id": "req-abc123"
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": { ... }
  },
  "meta": {
    "timestamp": "2024-03-27T10:00:00Z",
    "request_id": "req-abc123"
  }
}
```

---

## 2. Authentication API

### 2.1 Login

**Endpoint**: `POST /auth/login`

**Description**: Authenticate user and receive JWT token

**Security**: 
- 🔐 HTTPS required
- 📝 Audit logged
- ⏳ Rate limited (5/5min)

**Request Body**:
```json
{
  "email": "user@company.com",
  "password": "user_password",
  "mfa_code": "123456"  // Optional, required if MFA enabled
}
```

**Request Schema**:
```json
{
  "type": "object",
  "required": ["email", "password"],
  "properties": {
    "email": {
      "type": "string",
      "format": "email",
      "maxLength": 255
    },
    "password": {
      "type": "string",
      "minLength": 12,
      "maxLength": 128
    },
    "mfa_code": {
      "type": "string",
      "pattern": "^[0-9]{6}$"
    }
  }
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 28800,
    "user": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@company.com",
      "name": "User Name",
      "role": "engineer",
      "tenant_id": "tenant-uuid",
      "mfa_enabled": true
    }
  },
  "meta": {
    "timestamp": "2024-03-27T10:00:00Z",
    "request_id": "req-abc123"
  }
}
```

**Response (401 Unauthorized)**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email or password is incorrect",
    "details": {
      "attempts_remaining": 3
    }
  }
}
```

**Response (429 Too Many Requests)**:
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many login attempts. Please try again in 5 minutes.",
    "details": {
      "retry_after": 300
    }
  }
}
```

---

### 2.2 Logout

**Endpoint**: `POST /auth/logout`

**Description**: Invalidate current session/token

**Security**: 
- ✅ Authentication required
- 📝 Audit logged

**Request Headers**:
```
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Successfully logged out"
  }
}
```

---

### 2.3 Refresh Token

**Endpoint**: `POST /auth/refresh`

**Description**: Refresh JWT token before expiry

**Security**: 
- ✅ Valid token required
- 📝 Audit logged

**Request Headers**:
```
Authorization: Bearer <current_token>
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 28800
  }
}
```

---

### 2.4 Verify Token

**Endpoint**: `GET /auth/verify`

**Description**: Verify if token is valid and return user info

**Security**: 
- ✅ Valid token required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@company.com",
      "role": "engineer",
      "permissions": [
        "view_sandboxes",
        "create_sandbox",
        "delete_sandbox"
      ]
    },
    "expires_at": "2024-03-27T18:00:00Z"
  }
}
```

---

## 3. Sandbox Management API

### 3.1 List Sandboxes

**Endpoint**: `GET /sandboxes`

**Description**: List all sandboxes accessible to user

**Security**: 
- ✅ Authentication required
- 🛡️ `view_sandboxes` permission required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `instance_id` | UUID | Filter by instance |
| `status` | string | Filter by status (running, stopped, etc.) |
| `created_by` | UUID | Filter by creator |
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Items per page (default: 20, max: 100) |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "sandboxes": [
      {
        "sandbox_id": "sandbox-uuid-1",
        "name": "training-job-001",
        "instance_id": "instance-uuid",
        "status": "running",
        "image": "nemoclaw/pytorch:2.1.0",
        "gpu_enabled": true,
        "created_by": "user-uuid",
        "created_at": "2024-03-27T08:00:00Z",
        "started_at": "2024-03-27T08:05:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "pages": 3
    }
  }
}
```

---

### 3.2 Create Sandbox

**Endpoint**: `POST /sandboxes`

**Description**: Create a new sandbox

**Security**: 
- ✅ Authentication required
- 🛡️ `create_sandbox` permission required
- 📝 Audit logged

**Request Body**:
```json
{
  "instance_id": "instance-uuid",
  "name": "training-job-001",
  "image": "nemoclaw/pytorch:2.1.0-cuda12.1",
  "gpu_enabled": true,
  "gpu_memory_gb": 24,
  "cpu_cores": 8,
  "memory_gb": 32,
  "storage_gb": 100,
  "environment_vars": {
    "CUDA_VISIBLE_DEVICES": "0,1",
    "PYTHONPATH": "/workspace"
  },
  "ports": [8888, 6006],
  "volumes": [
    {
      "host_path": "/data/datasets",
      "container_path": "/data",
      "read_only": true
    }
  ]
}
```

**Request Schema**:
```json
{
  "type": "object",
  "required": ["instance_id", "name", "image"],
  "properties": {
    "instance_id": {
      "type": "string",
      "format": "uuid"
    },
    "name": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9_-]{3,64}$"
    },
    "image": {
      "type": "string",
      "maxLength": 255
    },
    "gpu_enabled": {
      "type": "boolean",
      "default": false
    },
    "gpu_memory_gb": {
      "type": "integer",
      "minimum": 1,
      "maximum": 80
    },
    "cpu_cores": {
      "type": "integer",
      "minimum": 1,
      "maximum": 128
    },
    "memory_gb": {
      "type": "integer",
      "minimum": 1,
      "maximum": 512
    },
    "storage_gb": {
      "type": "integer",
      "minimum": 10,
      "maximum": 10000
    }
  }
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "sandbox_id": "sandbox-uuid",
    "name": "training-job-001",
    "status": "creating",
    "created_at": "2024-03-27T10:00:00Z",
    "message": "Sandbox creation initiated"
  }
}
```

**Response (403 Forbidden)**:
```json
{
  "success": false,
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Sandbox limit reached for your tier",
    "details": {
      "current": 10,
      "limit": 10,
      "tier": "professional"
    }
  }
}
```

---

### 3.3 Get Sandbox Details

**Endpoint**: `GET /sandboxes/{sandbox_id}`

**Description**: Get detailed information about a specific sandbox

**Security**: 
- ✅ Authentication required
- 🛡️ `view_sandboxes` permission + resource access

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `sandbox_id` | UUID | Sandbox identifier |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "sandbox_id": "sandbox-uuid",
    "name": "training-job-001",
    "instance_id": "instance-uuid",
    "status": "running",
    "image": "nemoclaw/pytorch:2.1.0",
    "gpu_enabled": true,
    "resources": {
      "cpu_cores": 8,
      "memory_gb": 32,
      "storage_gb": 100,
      "gpu_memory_gb": 24
    },
    "environment_vars": {...},
    "ports": [8888, 6006],
    "volumes": [...],
    "created_by": "user-uuid",
    "created_at": "2024-03-27T08:00:00Z",
    "started_at": "2024-03-27T08:05:00Z",
    "health": {
      "status": "healthy",
      "last_check": "2024-03-27T10:00:00Z"
    }
  }
}
```

---

### 3.4 Start Sandbox

**Endpoint**: `POST /sandboxes/{sandbox_id}/start`

**Description**: Start a stopped sandbox

**Security**: 
- ✅ Authentication required
- 🛡️ `start_stop_sandbox` permission required
- 📝 Audit logged

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "sandbox_id": "sandbox-uuid",
    "status": "running",
    "started_at": "2024-03-27T10:00:00Z"
  }
}
```

---

### 3.5 Stop Sandbox

**Endpoint**: `POST /sandboxes/{sandbox_id}/stop`

**Description**: Stop a running sandbox

**Security**: 
- ✅ Authentication required
- 🛡️ `start_stop_sandbox` permission required
- 📝 Audit logged

**Request Body** (optional):
```json
{
  "force": false,  // Force stop if true
  "timeout": 30    // Grace period in seconds
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "sandbox_id": "sandbox-uuid",
    "status": "stopped",
    "stopped_at": "2024-03-27T10:00:00Z"
  }
}
```

---

### 3.6 Delete Sandbox

**Endpoint**: `DELETE /sandboxes/{sandbox_id}`

**Description**: Delete a sandbox (must be stopped)

**Security**: 
- ✅ Authentication required
- 🛡️ `delete_sandbox` permission required
- 📝 Audit logged

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `force` | boolean | false | Force delete even if running |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "sandbox_id": "sandbox-uuid",
    "deleted": true,
    "message": "Sandbox successfully deleted"
  }
}
```

---

### 3.7 Get Sandbox Logs

**Endpoint**: `GET /sandboxes/{sandbox_id}/logs`

**Description**: Retrieve sandbox logs

**Security**: 
- ✅ Authentication required
- 🛡️ `view_logs` permission required

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lines` | integer | 100 | Number of lines to retrieve |
| `since` | ISO8601 | - | Start time filter |
| `until` | ISO8601 | - | End time filter |
| `follow` | boolean | false | Stream logs (WebSocket) |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "sandbox_id": "sandbox-uuid",
    "logs": [
      {
        "timestamp": "2024-03-27T10:00:00Z",
        "level": "INFO",
        "message": "Training started"
      },
      {
        "timestamp": "2024-03-27T10:01:00Z",
        "level": "INFO",
        "message": "Epoch 1/100"
      }
    ],
    "total_lines": 100
  }
}
```

---

## 4. Security Operations API

### 4.1 List Network Requests

**Endpoint**: `GET /security/requests`

**Description**: List network requests pending approval

**Security**: 
- ✅ Authentication required
- 🛡️ `view_request_queue` permission required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (pending, approved, denied) |
| `risk_level` | string | Filter by risk (low, medium, high) |
| `sandbox_id` | UUID | Filter by sandbox |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "requests": [
      {
        "request_id": "req-uuid",
        "timestamp": "2024-03-27T10:00:00Z",
        "sandbox_id": "sandbox-uuid",
        "request_type": "outbound",
        "target_host": "api.external.com",
        "target_port": 443,
        "protocol": "https",
        "risk_score": 75,
        "risk_factors": ["external_domain", "unapproved_api"],
        "status": "pending"
      }
    ]
  }
}
```

---

### 4.2 Approve Request

**Endpoint**: `POST /security/requests/{request_id}/approve`

**Description**: Approve a network request

**Security**: 
- ✅ Authentication required
- 🛡️ `approve_requests` permission required
- 📝 Audit logged

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "request_id": "req-uuid",
    "status": "approved",
    "approved_by": "user-uuid",
    "approved_at": "2024-03-27T10:05:00Z"
  }
}
```

---

### 4.3 List Security Alerts

**Endpoint**: `GET /security/alerts`

**Description**: List security alerts

**Security**: 
- ✅ Authentication required
- 🛡️ `view_security_alerts` permission required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `severity` | string | Filter by severity |
| `acknowledged` | boolean | Filter by acknowledgment status |
| `alert_type` | string | Filter by type |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "alert_id": "alert-uuid",
        "timestamp": "2024-03-27T10:00:00Z",
        "severity": "high",
        "alert_type": "policy_violation",
        "title": "Unauthorized data access",
        "description": "Sandbox attempted to access restricted dataset",
        "source_ip": "10.0.0.50",
        "acknowledged": false
      }
    ]
  }
}
```

---

### 4.4 Acknowledge Alert

**Endpoint**: `POST /security/alerts/{alert_id}/acknowledge`

**Description**: Acknowledge a security alert

**Security**: 
- ✅ Authentication required
- 🛡️ `acknowledge_alerts` permission required
- 📝 Audit logged

**Request Body**:
```json
{
  "notes": "Investigating the issue"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "alert_id": "alert-uuid",
    "acknowledged": true,
    "acknowledged_by": "user-uuid",
    "acknowledged_at": "2024-03-27T10:05:00Z"
  }
}
```

---

## 5. Health Monitoring API

### 5.1 Run Health Assessment

**Endpoint**: `POST /health/assess`

**Description**: Execute comprehensive health assessment

**Security**: 
- ✅ Authentication required
- 🛡️ Any authenticated user
- ⏳ Rate limited (60/min)

**Request Body** (optional):
```json
{
  "check_types": ["service_availability", "security_posture"],
  "quick": false
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "report_id": "health-20240327100000-abc123",
    "generated_at": "2024-03-27T10:00:00Z",
    "overall_status": "healthy",
    "checks": [
      {
        "check_id": "service_availability",
        "status": "healthy",
        "severity": "info",
        "duration_ms": 45.2,
        "message": "All core services available"
      }
    ],
    "integrity_hash": "sha256:abc123...",
    "signature": "hmac:def456..."
  }
}
```

---

### 5.2 Get Health Status

**Endpoint**: `GET /health/status`

**Description**: Get current health status (cached)

**Security**: 
- ✅ Authentication required
- 🛡️ Any authenticated user

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "last_check": "2024-03-27T10:00:00Z",
    "components": {
      "database": "healthy",
      "cache": "healthy",
      "external_api": "healthy"
    }
  }
}
```

---

### 5.3 List Anomalies

**Endpoint**: `GET /health/anomalies`

**Description**: List detected anomalies

**Security**: 
- ✅ Authentication required
- 🛡️ Any authenticated user

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `severity` | string | Filter by severity |
| `acknowledged` | boolean | Filter by status |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "anomalies": [
      {
        "event_id": "anomaly-uuid",
        "timestamp": "2024-03-27T09:55:00Z",
        "anomaly_type": "sudden_degradation",
        "severity": "high",
        "description": "GPU temperature suddenly increased",
        "affected_component": "gpu_metrics",
        "acknowledged": false
      }
    ]
  }
}
```

---

## 6. Audit & Compliance API

### 6.1 Query Audit Logs

**Endpoint**: `GET /audit/logs`

**Description**: Query audit logs with filters

**Security**: 
- ✅ Authentication required
- 🛡️ `view_audit_trail` permission required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | ISO8601 | Start of date range |
| `end_date` | ISO8601 | End of date range |
| `event_type` | string | Filter by event type |
| `user_id` | UUID | Filter by user |
| `severity` | string | Filter by severity |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "log_id": "log-uuid",
        "timestamp": "2024-03-27T10:00:00Z",
        "event_type": "sandbox_create",
        "user_id": "user-uuid",
        "severity": "info",
        "action": "create",
        "resource_type": "sandbox",
        "resource_id": "sandbox-uuid",
        "description": "Created sandbox 'training-job-001'"
      }
    ],
    "total": 150
  }
}
```

---

### 6.2 Export Audit Logs

**Endpoint**: `POST /audit/export`

**Description**: Export audit logs in various formats

**Security**: 
- ✅ Authentication required
- 🛡️ `view_audit_trail` permission required
- ⏳ Rate limited (10/min)

**Request Body**:
```json
{
  "format": "json",
  "start_date": "2024-03-01T00:00:00Z",
  "end_date": "2024-03-27T23:59:59Z",
  "filters": {
    "event_type": ["sandbox_create", "sandbox_delete"],
    "severity": ["high", "critical"]
  }
}
```

**Supported Formats**: `json`, `csv`, `pdf`, `syslog`, `cef`, `leef`

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "export_id": "export-uuid",
    "status": "processing",
    "download_url": "https://api.nemoclaw.internal/v2/audit/exports/export-uuid/download",
    "expires_at": "2024-03-28T10:00:00Z"
  }
}
```

---

## 7. Error Codes

### Standard HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| **200** | OK | Request successful |
| **201** | Created | Resource created successfully |
| **204** | No Content | Request successful, no body |
| **400** | Bad Request | Invalid request parameters |
| **401** | Unauthorized | Authentication required or failed |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource not found |
| **409** | Conflict | Resource conflict (e.g., duplicate) |
| **422** | Unprocessable Entity | Validation error |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error |
| **503** | Service Unavailable | Service temporarily unavailable |

### Application Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | Email or password incorrect | 401 |
| `TOKEN_EXPIRED` | JWT token has expired | 401 |
| `INVALID_TOKEN` | JWT token is invalid | 401 |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permission | 403 |
| `RESOURCE_NOT_FOUND` | Requested resource not found | 404 |
| `VALIDATION_ERROR` | Request validation failed | 422 |
| `QUOTA_EXCEEDED` | Resource limit reached | 403 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `RESOURCE_IN_USE` | Resource cannot be modified | 409 |
| `SANDBOX_NOT_STOPPED` | Sandbox must be stopped first | 409 |
| `INSTANCE_OFFLINE` | Instance is not accessible | 503 |
| `INTERNAL_ERROR` | Unexpected server error | 500 |

---

## 8. SDK Examples

### Python SDK

```python
import requests

class NemoClawClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        
    def authenticate(self, email, password, mfa_code=None):
        """Authenticate and store token"""
        payload = {
            "email": email,
            "password": password
        }
        if mfa_code:
            payload["mfa_code"] = mfa_code
            
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()["data"]
        self.token = data["token"]
        return data["user"]
    
    def _headers(self):
        """Get authenticated headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def list_sandboxes(self, instance_id=None, status=None):
        """List sandboxes with optional filters"""
        params = {}
        if instance_id:
            params["instance_id"] = instance_id
        if status:
            params["status"] = status
            
        response = self.session.get(
            f"{self.base_url}/sandboxes",
            headers=self._headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()["data"]["sandboxes"]
    
    def create_sandbox(self, config):
        """Create a new sandbox"""
        response = self.session.post(
            f"{self.base_url}/sandboxes",
            headers=self._headers(),
            json=config
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def start_sandbox(self, sandbox_id):
        """Start a sandbox"""
        response = self.session.post(
            f"{self.base_url}/sandboxes/{sandbox_id}/start",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def stop_sandbox(self, sandbox_id, force=False):
        """Stop a sandbox"""
        response = self.session.post(
            f"{self.base_url}/sandboxes/{sandbox_id}/stop",
            headers=self._headers(),
            json={"force": force}
        )
        response.raise_for_status()
        return response.json()["data"]

# Usage example
client = NemoClawClient("https://api.nemoclaw.internal/v2")

# Authenticate
user = client.authenticate("engineer@company.com", "password123")
print(f"Logged in as {user['name']}")

# List sandboxes
sandboxes = client.list_sandboxes()
for sandbox in sandboxes:
    print(f"{sandbox['name']}: {sandbox['status']}")

# Create new sandbox
new_sandbox = client.create_sandbox({
    "instance_id": "instance-uuid",
    "name": "training-job-002",
    "image": "nemoclaw/pytorch:2.1.0",
    "gpu_enabled": True,
    "cpu_cores": 8,
    "memory_gb": 32
})
print(f"Created sandbox: {new_sandbox['sandbox_id']}")
```

### cURL Examples

```bash
# Authenticate
curl -X POST https://api.nemoclaw.internal/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "engineer@company.com",
    "password": "password123"
  }'

# List sandboxes
curl -X GET https://api.nemoclaw.internal/v2/sandboxes \
  -H "Authorization: Bearer <token>"

# Create sandbox
curl -X POST https://api.nemoclaw.internal/v2/sandboxes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "instance-uuid",
    "name": "training-job",
    "image": "nemoclaw/pytorch:2.1.0",
    "gpu_enabled": true
  }'

# Start sandbox
curl -X POST https://api.nemoclaw.internal/v2/sandboxes/sandbox-uuid/start \
  -H "Authorization: Bearer <token>"

# Stop sandbox
curl -X POST https://api.nemoclaw.internal/v2/sandboxes/sandbox-uuid/stop \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

---

**Version**: 2.1.0  
**Last Updated**: March 27, 2026  
**Next Review**: April 27, 2026

---

*End of API Specifications*
