# Security Guidelines - MCP STDIO Docker Test Server

> **Source**: Adapted from [Project CodeGuard](https://github.com/project-codeguard/rules) - AI model-agnostic security framework

This document defines security practices that AI assistants and developers must follow. These are guidelines, not rigid rules—but deviations should be conscious and documented.

---

## Core Principles

1. **Secure by Default**: Build security in from the start, not as an afterthought
2. **Least Privilege**: Request only the permissions you need
3. **Defense in Depth**: Don't rely on a single security control
4. **Fail Securely**: Errors should not expose sensitive information

---

## Secrets Management

### ❌ Never Do
- Hardcode secrets, API keys, passwords, or tokens in source code
- Commit `.env` files with real credentials
- Log sensitive information
- Include secrets in error messages

### ✅ Always Do
- Use environment variables for secrets
- Add secret files to `.gitignore`
- Use secret management services in production (Vault, AWS Secrets Manager, etc.)
- Rotate secrets regularly

### Example `.gitignore` entries
```gitignore
# Secrets - NEVER commit these
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
credentials.json
```

### Recognition Patterns - Learn to Spot These Formats

Common Secret Formats You Must NEVER Hardcode:

- AWS Keys: Start with `AKIA`, `AGPA`, `AIDA`, `AROA`, `AIPA`, `ANPA`, `ANVA`, `ASIA`
- Stripe Keys: Start with `sk_live_`, `pk_live_`, `sk_test_`, `pk_test_`
- Google API: Start with `AIza` followed by 35 characters
- GitHub Tokens: Start with `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`
- JWT Tokens: Three base64 sections separated by dots, starts with `eyJ`
- Private Key Blocks: Any text between `-----BEGIN` and `-----END PRIVATE KEY-----`
- Connection Strings: URLs with credentials like `mongodb://user:pass@host`

**Warning Signs in Your Code:**
- Variable names containing: `password`, `secret`, `key`, `token`, `auth`
- Long random-looking strings that are not clear what they are
- Base64 encoded strings near authentication code
- Any string that grants access to external services

### Example Environment Variable Pattern
```python
# Good - using environment variables
import os

log_level = os.environ.get("LOG_LEVEL", "INFO")
api_key = os.environ.get("API_KEY")  # If we ever need one

# Bad - hardcoded values
log_level = "DEBUG"  # OK for non-sensitive config
api_key = "sk_live_abc123xyz"  # NEVER DO THIS
```

---

## Input Validation & Injection Defense

### Core Strategy
- Validate early at trust boundaries with positive (allow‑list) validation and canonicalization.
- Treat all untrusted input as data, never as code. Use safe APIs that separate code from data.
- Parameterize queries/commands; escape only as last resort and context‑specific.

### Validation Playbook
- **Syntactic validation**: enforce format, type, ranges, and lengths for each field.
- **Semantic validation**: enforce business rules (e.g., start ≤ end date, enum allow‑lists).
- **Normalization**: canonicalize encodings before validation; validate complete strings (regex anchors ^$); beware ReDoS.
- **Free‑form text**: define character class allow‑lists; normalize Unicode; set length bounds.
- **Files**: validate by content type (magic), size caps, and safe extensions; server‑generate filenames; scan; store outside web root.

### ❌ Never Do
- Trust user input without validation
- Use string concatenation for SQL queries
- Directly embed user input in shell commands
- Render user input as HTML without escaping
- Use shell invocation for untrusted input

### ✅ Always Do
- Validate input type, length, format, and range
- Use parameterized queries for databases
- Sanitize input before use in commands
- Escape output based on context (HTML, URL, SQL, etc.)
- Use structured execution that separates command and arguments

### Python Input Validation Pattern
```python
# Good - validate inputs
def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    # Validate count parameter
    count = min(max(arguments.get("count", 1), 1), 10)  # Clamp to valid range
    
    # Validate boolean
    include_delay = bool(arguments.get("include_delay", False))
    
    # Validate string length
    message = arguments.get("message", "")
    if len(message) > 10000:  # Reasonable limit
        raise ValueError("Message too long")
    
    return process_request(count, include_delay, message)
```

### OS Command Injection Defense
```python
# Good - avoid shell=True, use list arguments
import subprocess

# Safe - arguments are separate
result = subprocess.run(
    ["docker", "run", "-i", container_name],
    capture_output=True,
    text=True,
    timeout=30
)

# Bad - shell=True with user input
# NEVER DO THIS:
# subprocess.run(f"docker run -i {user_input}", shell=True)
```

---

## Authentication & Authorization

### Authentication Guidelines
- [ ] Use established authentication libraries (don't roll your own)
- [ ] Enforce strong password policies (minimum 8 characters, passphrases accepted)
- [ ] Check new passwords against breach databases and reject common passwords
- [ ] Implement account lockout and rate limiting after failed attempts
- [ ] Use secure session management with HttpOnly, SameSite cookies
- [ ] Always return generic error messages to prevent account enumeration
- [ ] Support password managers (allow paste, no JavaScript blocks)

### Password Storage
- Hash passwords with slow, memory‑hard algorithms (Argon2id preferred, bcrypt/scrypt acceptable)
- Use unique per‑user salts and constant‑time comparison
- Never encrypt passwords - always hash them
- Consider using a pepper (stored separately from database) for additional security

### Multi‑Factor Authentication (MFA)
- Require MFA for sensitive accounts and operations
- Prefer phishing‑resistant factors (WebAuthn/passkeys, hardware tokens)
- Accept TOTP apps as backup; avoid SMS/voice codes when possible
- Implement secure recovery with backup codes
- Require MFA for: login, password changes, privilege elevation, new devices

### Authorization Guidelines
- [ ] Check permissions on every request
- [ ] Use role-based (RBAC) or attribute-based (ABAC) access control
- [ ] Validate user owns resources they're accessing (prevent IDOR)
- [ ] Log access to sensitive resources
- [ ] Apply least privilege principle

**Note for MCP STDIO Test Server**: This server has no authentication or authorization by design - it's for testing only. If you add these features, follow the guidelines above.

---

## Cryptography

### ❌ Never Do
- Implement your own cryptographic algorithms
- Use deprecated algorithms (MD5, SHA1 for security, DES, RC4)
- Use ECB mode for encryption
- Hardcode encryption keys

### ✅ Always Do
- Use well-vetted cryptographic libraries
- Use strong algorithms (AES-256, SHA-256+, RSA-2048+)
- Use authenticated encryption (GCM mode)
- Properly manage key lifecycle

### Recommended Algorithms
| Purpose | Recommended | Avoid |
|---------|-------------|-------|
| Hashing (passwords) | bcrypt, Argon2, scrypt | MD5, SHA1, plain SHA256 |
| Hashing (data integrity) | SHA-256, SHA-3 | MD5, SHA1 |
| Symmetric encryption | AES-256-GCM | DES, 3DES, RC4, AES-ECB |
| Asymmetric encryption | RSA-2048+, ECDSA | RSA-1024 |

### Python Cryptography Example
```python
# Good - using hashlib for non-security hashing
import hashlib

def generate_request_id(data: str) -> str:
    # SHA-256 is fine for non-security purposes like IDs
    return hashlib.sha256(data.encode()).hexdigest()

# For passwords, use bcrypt or Argon2 (not in this project)
```

---

## Data Protection

### Sensitive Data Handling
- Encrypt sensitive data at rest
- Use TLS for data in transit
- Minimize data collection (collect only what's needed)
- Implement data retention policies
- Mask sensitive data in logs and UI

### PII (Personally Identifiable Information)
- [ ] Identify what PII the application handles
- [ ] Document where PII is stored
- [ ] Encrypt PII at rest
- [ ] Implement access controls for PII
- [ ] Support data deletion requests

**Note for MCP STDIO Test Server**: This server generates only random synthetic data with no real PII. All data is ephemeral and not persisted.

---

## Dependency Security

### ❌ Never Do
- Use dependencies with known critical vulnerabilities
- Pin to exact versions without security update strategy
- Import dependencies from untrusted sources

### ✅ Always Do
- Regularly audit dependencies for vulnerabilities
- Keep dependencies updated (especially security patches)
- Use lockfiles for reproducible builds
- Verify package integrity (checksums, signatures)

### Python Dependency Management
```bash
# Audit dependencies for vulnerabilities
pip-audit

# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Verify requirements.txt is minimal
# Only include what's actually needed
```

### Current Dependencies Audit
```
mcp>=1.25.0              # Core MCP protocol - keep updated
pydantic>=2.0.0          # Data validation - keep updated
python-json-logger>=3.0.0 # Logging - keep updated
```

**Action Items:**
- [ ] Run `pip-audit` regularly to check for vulnerabilities
- [ ] Monitor security advisories for mcp, pydantic, and python-json-logger
- [ ] Update dependencies monthly or when security patches released

---

## Error Handling & Logging

### Error Messages
- Don't expose stack traces to users in production
- Don't reveal system information in errors
- Log full details internally, show generic messages externally

### Secure Logging
```python
# BAD - logs sensitive data
logger.info(f"User login: {username}, password: {password}")

# GOOD - logs safely
logger.info("User login attempt", extra={"username": username})

# GOOD - structured logging without sensitive data
logger.info(
    "MCP tool called",
    extra={
        "tool_name": name,
        "arguments": arguments,  # OK - no sensitive data in this project
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
)
```

### What to Log
- [ ] Authentication attempts (success and failure)
- [ ] Authorization failures
- [ ] Input validation failures
- [ ] Application errors
- [ ] Security-relevant events

### What NOT to Log
- Passwords or secrets
- Full credit card numbers
- Personal health information
- Session tokens
- Encryption keys

**Current Logging Audit:**
- ✅ Logs go to stderr (not stdout which is for MCP protocol)
- ✅ No sensitive data logged (project has no sensitive data)
- ✅ Structured JSON logging for production
- ✅ Configurable log levels via environment variables

---

## API Security

### MCP Protocol Security
- [ ] Validate all tool inputs (type, range, format)
- [ ] Return structured responses only
- [ ] Handle errors gracefully without exposing internals
- [ ] Log all tool invocations for audit trail
- [ ] Implement timeouts for long-running operations

### Current Implementation Review
```python
# Good - input validation
count = min(max(arguments.get("count", 1), 1), 10)  # Clamp to 1-10

# Good - error handling
except Exception as e:
    logger.exception("MCP tool failed", extra={"tool_name": name, "error": str(e)})
    return [types.TextContent(type="text", text=f"Error: {str(e)}")]

# Good - structured responses
return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

---

## Docker Security

### Container Security Best Practices
- [ ] Use minimal base images (Alpine Linux)
- [ ] Run as non-root user when possible
- [ ] Don't include unnecessary tools in container
- [ ] Keep base images updated
- [ ] Scan images for vulnerabilities
- [ ] Use specific image tags, not `latest`

### Current Docker Configuration Audit
```dockerfile
# Good - hardened base image
FROM containers.cisco.com/sto-ccc-cloud9/hardened_alpine:latest

# Good - minimal package installation
RUN apk add --no-cache bash python3 py3-pip

# Good - security patch applied
RUN pip install --no-cache-dir --break-system-packages --upgrade 'pip>=25.3'

# Consider - run as non-root user (future enhancement)
# USER nobody
```

**Recommendations:**
- ✅ Using hardened Alpine base
- ✅ Minimal package installation
- ✅ Security patches applied
- ⚠️ Consider adding non-root user for defense in depth
- ✅ No secrets in image
- ✅ Proper ENTRYPOINT/CMD separation

---

## Security Checklist for New Features

### Before Implementation
- [ ] Identify sensitive data involved
- [ ] Document authentication/authorization requirements
- [ ] Consider attack vectors (STRIDE, OWASP Top 10)

### During Implementation
- [ ] Validate all inputs
- [ ] Use parameterized queries (if adding database)
- [ ] Apply least privilege
- [ ] Handle errors securely

### Before Release
- [ ] Run security-focused code review
- [ ] Scan dependencies for vulnerabilities
- [ ] Test authentication/authorization (if applicable)
- [ ] Verify secrets are not in code

---

## Project-Specific Security Posture

### Current Security Status: ✅ GOOD

**Strengths:**
- ✅ No external dependencies (APIs, databases, network calls)
- ✅ No authentication/authorization (by design - testing only)
- ✅ No secrets or credentials in code
- ✅ No sensitive data handling
- ✅ Input validation on all tool parameters
- ✅ Secure logging (no sensitive data, stderr only)
- ✅ Hardened Docker base image
- ✅ Minimal attack surface
- ✅ Proper error handling without information leakage

**Areas for Improvement:**
- ⚠️ Consider running Docker container as non-root user
- ⚠️ Add automated dependency vulnerability scanning to CI/CD
- ⚠️ Document security update process in CONTRIBUTING.md

**Risk Assessment:**
- **Overall Risk**: LOW
- **Rationale**: Server is designed for testing only, has no external dependencies, handles no real data, and has minimal attack surface

---

## Resources

- **Project CodeGuard**: https://github.com/project-codeguard/rules
- **OWASP Top 10**: https://owasp.org/Top10/
- **OWASP Cheat Sheets**: https://cheatsheetseries.owasp.org/
- **CWE (Common Weakness Enumeration)**: https://cwe.mitre.org/
- **Python Security Best Practices**: https://python.readthedocs.io/en/stable/library/security_warnings.html
- **Docker Security**: https://docs.docker.com/engine/security/

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-20 | Initial security guidelines adapted from the-forge template |
