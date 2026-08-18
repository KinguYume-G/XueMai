# 🔒 UniPulse Asia - Security Audit Report

**Generated**: 2025-11-26  
**Audit Scope**: Phase 1 - Critical Security & Privacy Issues  
**Status**: 🔴 **CRITICAL ISSUES FOUND**

---

## 🚨 Executive Summary

| Category | Status | Issues Found |
|----------|--------|--------------|
| **User Privacy** | 🔴 CRITICAL | 1 major, 1 minor |
| **Authentication** | 🟢 GOOD | 0 critical |
| **Token Management** | 🟢 GOOD | 0 critical |
| **CORS Configuration** | 🟡 WARNING | 1 configuration issue |
| **SQL Injection** | 🟢 PROTECTED | 0 issues (ORM-based) |
| **XSS Protection** | 🟢 PROTECTED | DRF auto-escaping |
| **Dependencies** | 🟡 WARNING | ChromaDB migration incomplete |

**Priority**: 🔴 **P0 Issues Must Be Fixed Before Production**

---

## 🔴 P0 - CRITICAL SECURITY ISSUES

### 🚨 Issue 1.1: User Email/Bio Exposed to Public

**Severity**: **CRITICAL** 🔴  
**Location**: `backend/apps/users/views.py:17`, `backend/apps/users/serializers.py:22`  
**CVE Reference**: Similar to OWASP A01:2021 - Broken Access Control

#### Description
The `UserViewSet` uses `IsAuthenticatedOrReadOnly` permission, allowing **unauthenticated users** to read all user data including emails and bio information via `/api/users/` endpoint.

#### Vulnerable Code
```python
# apps/users/views.py
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('profile').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # ❌ VULNERABLE
```

```python
# apps/users/serializers.py
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "created_at"]  # ❌ Email exposed
```

#### Attack Scenario
```bash
# Attacker can enumerate all user emails without authentication
curl http://api.unipulse.asia/api/users/?page=1
# Response: {"results": [{"id": 1, "username": "alice", "email": "alice@example.com", ...}]}

# Collect emails for spam/phishing campaigns
for page in {1..100}; do
    curl "http://api.unipulse.asia/api/users/?page=$page" | jq -r '.results[].email'
done > emails.txt
```

#### Impact
- **Privacy Violation**: All user emails are public (GDPR/CCPA violation)
- **Phishing Risk**: Attackers can harvest emails for targeted attacks
- **Information Disclosure**: Bio/profile data leaked to competitors

#### Recommended Fix
Create separate serializers for public vs. private user data:

```python
# apps/users/serializers.py
class UserPublicSerializer(serializers.ModelSerializer):
    """Public user info - safe for unauthenticated access"""
    class Meta:
        model = User
        fields = ["id", "username", "created_at"]  # ✅ No email/bio
        read_only_fields = ["id", "created_at"]


class UserPrivateSerializer(serializers.ModelSerializer):
    """Full user info - authenticated users only"""
    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "created_at"]
        read_only_fields = ["id", "created_at"]


# apps/users/views.py
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('profile').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        # ✅ Use different serializers based on authentication
        if self.request.user.is_authenticated:
            return UserPrivateSerializer
        return UserPublicSerializer
```

#### Verification Steps
1. **Before Fix**: `curl http://localhost:8000/api/users/1/` → Shows email
2. **After Fix**: Same curl → Email field missing
3. **Authenticated**: `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/1/` → Shows email

---

### ⚠️ Issue 1.2: ProfileViewSet Same Vulnerability

**Severity**: MEDIUM 🟡  
**Location**: `backend/apps/users/views.py:34`, `backend/apps/users/serializers.py:37`

#### Description
`ProfileViewSet` has same issue - allows unauthenticated users to search by email:

```python
# apps/users/views.py:37
search_fields = ["user__username", "user__email", "major"]  # ❌ Email searchable
```

#### Attack Scenario
```bash
# Search for users by email domain without authentication
curl "http://localhost:8000/api/profiles/?search=@gmail.com"
```

#### Recommended Fix
Remove `user__email` from `search_fields` for unauthenticated users:

```python
class ProfileViewSet(viewsets.ModelViewSet):
    def get_search_fields(self):
        if self.request.user.is_authenticated:
            return ["user__username", "user__email", "major"]
        return ["user__username", "major"]  # ✅ No email search for public
```

---

## 🟢 PASSED - Good Security Practices

### ✅ 1. Token Management Consistency

**Status**: 🟢 **GOOD**

#### Findings
- ✅ **No legacy `token` usage found** in frontend codebase
- ✅ All token references use `xm_access_token` / `xm_refresh_token`
- ✅ Token utilities centralized in `frontend/src/lib/auth/token.ts`
- ✅ Axios interceptor properly handles 401 refresh logic

#### Evidence
```bash
# Scanned entire frontend/src directory
grep -r "localStorage.getItem('token')" frontend/src/
# Result: No matches found ✅
```

---

### ✅ 2. JWT Configuration

**Status**: 🟢 **GOOD** (with minor optimization suggestion)

#### Current Settings (`config/settings/base.py:161-166`)
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),  # ✅ Reasonable
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),   # ✅ Appropriate
    "ROTATE_REFRESH_TOKENS": True,                  # ✅ Security best practice
    "BLACKLIST_AFTER_ROTATION": False,              # ⚠️ Consider enabling
}
```

#### Recommendations
- ✅ Current settings are secure for campus app use case
- 🔵 **Optional**: Enable token blacklisting for stricter security:
  ```python
  "BLACKLIST_AFTER_ROTATION": True,  # Prevent refresh token reuse
  ```
- 🔵 **Optional**: Reduce access token lifetime to 1 hour for production:
  ```python
  "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
  ```

---

### ✅ 3. Authentication Security

**Status**: 🟢 **EXCELLENT**

#### Verified Components
- ✅ Password validation: Min 8 characters enforced
- ✅ Password confirmation check on registration
- ✅ Passwords stored with Django's PBKDF2 hasher (secure)
- ✅ Email case-insensitive login (`email__iexact`)
- ✅ Error messages don't leak user existence ("邮箱或密码错误")

#### Code Review (`apps/authentication/views.py:82-98`)
```python
# ✅ Secure password checking
if not user or not user.check_password(password) or not user.is_active:
    return Response({
        "error": {
            "code": "invalid_credentials",
            "message": "邮箱或密码错误",  # ✅ Generic message
        }
    }, status=401)
```

---

## 🟡 WARNINGS - Configuration Issues

### ⚠️ Warning 1: CORS Limited to Localhost Only

**Severity**: MEDIUM 🟡  
**Location**: `backend/config/settings/base.py:169-173`

#### Current Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

#### Issue
- ❌ Missing Vite default port `5173`
- ❌ No production domains configured
- ❌ Will break when deploying frontend to Vercel

#### Recommended Fix
```python
# config/settings/base.py
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",      # ✅ Vite dev server
    "http://127.0.0.1:5173",
])

# .env.example (add production example)
# CORS_ALLOWED_ORIGINS=https://app.unipulse.asia,https://www.unipulse.asia
```

---

### ⚠️ Warning 2: ChromaDB Code Not Fully Removed

**Severity**: LOW 🟡  
**Location**: Multiple files in `backend/apps/ai/` and `backend/scripts/`

#### Findings
ChromaDB references found in **40+ locations** despite migration to pgvector:
- `backend/apps/ai/services/rag_engine.py` - Still imports `langchain_chroma`
- `backend/scripts/ingest_chunks_to_chroma.py` - ChromaDB ingestion script
- `backend/tests/test_rag_migration.py` - ChromaDB test cases
- Settings: `RAG_VECTOR_BACKEND = 'chromadb'` default value

#### Risk
- 🟡 Code maintenance burden (dead code paths)
- 🟡 Potential dependency conflicts if ChromaDB is uninstalled
- 🟡 Confusing for new developers

#### Recommended Action
See **Task 1.4** in phase1_tasks.md (deferred to P1 cleanup)

---

## 🔵 INFORMATIONAL - Best Practices

### ℹ️ SQL Injection Protection

**Status**: 🟢 **PROTECTED**

Django ORM automatically parameterizes all queries. No raw SQL found in critical paths.

---

### ℹ️ XSS Protection

**Status**: 🟢 **PROTECTED**

Django REST Framework auto-escapes all JSON responses. Frontend uses React (virtual DOM with XSS protection).

---

### ℹ️ CSRF Protection

**Status**: 🟢 **ENABLED**

- ✅ CSRF middleware active (`django.middleware.csrf.CsrfViewMiddleware`)
- ✅ JWT-based API doesn't require CSRF tokens (stateless)
- ✅ Cookie-based sessions not used for API authentication

---

## 📋 Recommended Action Plan

### Phase 1 (Day 1-2) - Critical Fixes

1. **[P0] Fix User Privacy Leak** (Task 1.1)
   - [ ] Create `UserPublicSerializer` and `UserPrivateSerializer`
   - [ ] Update `UserViewSet.get_serializer_class()`
   - [ ] Remove email from `ProfileViewSet.search_fields` for public
   - [ ] Test with authenticated/unauthenticated requests

2. **[P0] Update CORS Configuration** (Task 1.2)
   - [ ] Add Vite port 5173 to allowed origins
   - [ ] Document production domain setup in `.env.example`

### Phase 2 (Day 3-4) - Cleanup

3. **[P1] Remove ChromaDB Code** (Task 1.4)
   - See phase1_tasks.md for detailed steps

### Phase 3 (Day 5) - Documentation

4. **[P2] Security Documentation**
   - [ ] Create `docs/SECURITY.md` with security policies
   - [ ] Add penetration testing checklist
   - [ ] Document rate limiting strategy

---

## 🔍 Files Reviewed

### Backend
- ✅ `apps/authentication/views.py` - Login/Registration
- ✅ `apps/authentication/serializers.py` - Auth serializers
- ✅ `apps/users/views.py` - User/Profile endpoints
- ✅ `apps/users/serializers.py` - User serializers
- ✅ `apps/posts/views.py` - Post permissions
- ✅ `config/settings/base.py` - Security settings

### Frontend
- ✅ `frontend/src/**/*.ts` - Token usage scan (grep search)
- ✅ `lib/auth/token.ts` - Token utilities
- ✅ `lib/api/client.ts` - Axios interceptors
- ✅ `services/api/auth.api.ts` - Auth API calls

---

## 📞 Next Steps

1. **Review this report** with the development team
2. **Prioritize P0 fixes** before any production deployment
3. **Schedule P1 cleanup** in Phase 1 timeline (Day 3-4)
4. **Re-audit after fixes** to verify remediation

---

**Auditor**: Antigravity AI  
**Contact**: This is an automated security audit  
**Confidence**: High (manual code review + automated scanning)
