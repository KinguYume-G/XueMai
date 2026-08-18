# UniPulse Asia - Phase 1 Detailed Tasks

**Timeline**: 5 Days  
**Focus**: Security Fixes & Code Health  
**Status**: Ready for Execution

---

## 🔴 P0 - Critical Security (Day 1-2)

### Task 1.1: User Privacy Protection 🚨 CRITICAL

**Priority**: P0  
**Estimated Time**: 2-3 hours  
**Files to Modify**:
- `backend/apps/users/serializers.py`
- `backend/apps/users/views.py`

#### Problem Statement
The `/api/users/` endpoint exposes email addresses and bio information to **unauthenticated** users, violating user privacy and GDPR principles. This allows attackers to enumerate all user emails for phishing campaigns.

**Current Vulnerability**:
```bash
# Anyone can access this without authentication
curl http://localhost:8000/api/users/1/
# Response includes: {"email": "alice@example.com", "bio": "...", ...}
```

#### Implementation Steps

1. **Create Public/Private User Serializers**
   
   ```python
   # apps/users/serializers.py
   
   class UserPublicSerializer(serializers.ModelSerializer):
       """Public user info - safe for unauthenticated access"""
       class Meta:
           model = User
           fields = ["id", "username", "created_at"]
           read_only_fields = ["id", "created_at"]
   
   
   class UserPrivateSerializer(serializers.ModelSerializer):
       """Full user info - authenticated users only"""
       class Meta:
           model = User
           fields = ["id", "username", "email", "bio", "created_at"]
           read_only_fields = ["id", "created_at"]
   ```

2. **Update UserViewSet to Use Conditional Serializer**
   
   ```python
   # apps/users/views.py
   
   class UserViewSet(viewsets.ModelViewSet):
       queryset = User.objects.select_related('profile').all()
       permission_classes = [IsAuthenticatedOrReadOnly]
       
       def get_serializer_class(self):
           # Return different serializers based on authentication status
           if self.request.user.is_authenticated:
               return UserPrivateSerializer
           return UserPublicSerializer
   ```

3. **Fix ProfileViewSet Email Search Leak**
   
   ```python
   # apps/users/views.py
   
   class ProfileViewSet(viewsets.ModelViewSet):
       # ... existing code ...
       
       def get_search_fields(self):
           """Restrict email search to authenticated users only"""
           if self.request.user.is_authenticated:
               return ["user__username", "user__email", "major"]
           return ["user__username", "major"]  # No email for public
   ```

#### Verification Plan

**Automated Test** (create new test file):
```python
# backend/apps/users/tests/test_user_privacy.py

from django.test import TestCase
from rest_framework.test import APIClient
from apps.users.models import User

class UserPrivacyTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    def test_unauthenticated_cannot_see_email(self):
        """Unauthenticated users should NOT see email"""
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('email', response.data)
        self.assertIn('username', response.data)
    
    def test_authenticated_can_see_email(self):
        """Authenticated users SHOULD see email"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.data)
```

**Manual Verification Steps**:
```bash
# After implementation, run these commands:

# 1. Test unauthenticated access (should NOT show email)
curl http://localhost:8000/api/users/1/
# Expected: {"id": 1, "username": "alice", "created_at": "..."}
# ✅ PASS if email field is missing

# 2. Test authenticated access (should show email)
TOKEN="your_access_token_here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/1/
# Expected: {"id": 1, "username": "alice", "email": "alice@example.com", ...}
# ✅ PASS if email field is present

# 3. Test profile search without auth (should NOT find by email)
curl "http://localhost:8000/api/profiles/?search=@example.com"
# Expected: Empty results or error
# ✅ PASS if email search doesn't work
```

**Run Test Command**:
```bash
cd backend
python manage.py test apps.users.tests.test_user_privacy -v 2
```

---

### Task 1.2: Token Consistency Validation ✅ VERIFIED

**Priority**: P0  
**Estimated Time**: 1 hour  
**Status**: ✅ **PASSED - No Issues Found**

#### Audit Results
Scanned entire `frontend/src/` directory:
```bash
grep -r "localStorage.getItem('token')" frontend/src/
# Result: No matches found ✅
```

**Conclusion**: All code uses correct `xm_access_token` / `xm_refresh_token` keys. No action needed.

---

### Task 1.3: CORS Configuration Update

**Priority**: P0  
**Estimated Time**: 30 minutes  
**Files to Modify**: `backend/config/settings/base.py`, `backend/.env.example`

#### Problem
Current CORS config only allows `localhost:3000`, missing Vite's default port `5173` and production domains.

#### Implementation Steps

1. **Update Settings to Use Environment Variable**
   
   ```python
   # config/settings/base.py
   
   # Replace static list with env-based configuration
   CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[
       "http://localhost:3000",
       "http://127.0.0.1:3000",
       "http://localhost:5173",      # Vite dev server
       "http://127.0.0.1:5173",
   ])
   CORS_ALLOW_CREDENTIALS = True
   ```

2. **Update .env.example**
   
   ```env
   # backend/.env.example
   
   # CORS Configuration (comma-separated list)
   # Development (default)
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   
   # Production example (uncomment and modify)
   # CORS_ALLOWED_ORIGINS=https://app.unipulse.asia,https://www.unipulse.asia
   ```

#### Verification
```bash
# 1. Start backend
cd backend && python manage.py runserver

# 2. Start frontend on Vite port
cd frontend && pnpm dev  # Should use port 5173

# 3. Test CORS headers
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/api/users/ \
     -v
# ✅ PASS if response includes:
# Access-Control-Allow-Origin: http://localhost:5173
```

---

## 🟡 P1 - Important Cleanup (Day 3-4)

### Task 1.4: Remove ChromaDB Legacy Code

**Priority**: P1  
**Estimated Time**: 3-4 hours  
**Files to Clean**:
- `backend/apps/ai/services/rag_engine.py` (40 references)
- `backend/scripts/ingest_chunks_to_chroma.py`
- `backend/scripts/test_rag_query.py`
- `backend/tests/test_rag_migration.py`

#### Background
Project migrated from ChromaDB to pgvector for RAG, but legacy code remains causing maintenance burden.

#### Implementation Steps

1. **Update RAG Engine - Remove ChromaDB Import**
   
   ```python
   # backend/apps/ai/services/rag_engine.py
   
   # ❌ DELETE these lines:
   from langchain_chroma import Chroma
   
   # ❌ DELETE ChromaDB initialization in __init__
   if backend == 'chromadb':
       # ... delete entire block ...
   
   # ❌ DELETE _retrieve_from_chromadb method
   def _retrieve_from_chromadb(self, ...):
       # ... delete entire method ...
   ```

2. **Update Default Backend in Settings**
   
   ```python
   # config/settings/base.py
   
   # Change default from 'chromadb' to 'pgvector'
   RAG_VECTOR_BACKEND = env.str('RAG_VECTOR_BACKEND', default='pgvector')  # ✅ Changed
   ```

3. **Archive ChromaDB Scripts**
   
   ```bash
   # Move to archive folder instead of deleting (for reference)
   mkdir -p backend/scripts/archive
   mv backend/scripts/ingest_chunks_to_chroma.py backend/scripts/archive/
   mv backend/scripts/test_rag_query.py backend/scripts/archive/
   ```

4. **Update Dependencies**
   
   Check if `langchain-chroma` can be removed from `requirements-ai.txt`:
   ```bash
   # If no other imports, remove:
   # langchain-chroma
   # chromadb
   ```

#### Verification

**Test RAG Functionality**:
```bash
# 1. Set pgvector as backend
echo "RAG_VECTOR_BACKEND=pgvector" >> backend/.env

# 2. Test RAG retrieval
cd backend
python test_rag_api.py
# ✅ PASS if RAG returns results without ChromaDB errors

# 3. Check for ChromaDB imports
grep -r "langchain_chroma" backend/apps/
grep -r "chromadb" backend/apps/
# ✅ PASS if no matches in production code (only in archive/)
```

---

### Task 1.5: Organize Test Scripts

**Priority**: P1  
**Estimated Time**: 1 hour  
**Files to Move**: All `test_*.py` files in `backend/` root

#### Implementation

```bash
# Create scripts directory
mkdir -p backend/scripts

# Move test scripts
cd backend
mv test_ai_simple.py scripts/
mv test_bookmark_api.py scripts/
mv test_db_connection.py scripts/
mv test_rag_api.py scripts/
mv test_rag_debug.py scripts/
mv test_rag_integration.py scripts/
mv test_serializer.py scripts/

# Keep manage.py and production files in root
```

#### Verification
```bash
# Root should be clean
ls backend/*.py
# Expected: Only manage.py, wsgi.py, asgi.py

# Scripts in proper folder
ls backend/scripts/test_*.py
# ✅ PASS if all test scripts are there
```

---

### Task 1.6: Fix requirements.txt Encoding

**Priority**: P1  
**Estimated Time**: 15 minutes  
**File**: `backend/requirements.txt`

#### Problem
Current encoding is UTF-16LE, causing read errors.

#### Implementation
```bash
# Convert to UTF-8
cd backend
Get-Content requirements.txt | Set-Content -Encoding UTF8 requirements_utf8.txt
Move-Item -Force requirements_utf8.txt requirements.txt

# Verify
file requirements.txt
# Expected: requirements.txt: ASCII text
```

---

## 🟢 P2 - Polish (Day 5)

### Task 1.7: Configure Code Formatters

**Priority**: P2  
**Estimated Time**: 2 hours

#### Backend - Black + isort

1. **Install Black**
   ```bash
   cd backend
   pip install black isort
   ```

2. **Create `pyproject.toml`**
   ```toml
   [tool.black]
   line-length = 100
   target-version = ['py311']
   exclude = '''
   /(
       migrations
     | __pycache__
     | .venv
   )/
   '''
   
   [tool.isort]
   profile = "black"
   skip = ["migrations", ".venv"]
   ```

3. **Run Formatter**
   ```bash
   black apps/ config/ core/
   isort apps/ config/ core/
   ```

#### Frontend - ESLint + Prettier

1. **Install Dependencies**
   ```bash
   cd frontend
   pnpm add -D prettier eslint-config-prettier
   ```

2. **Create `.prettierrc`**
   ```json
   {
     "semi": false,
     "singleQuote": true,
     "tabWidth": 2,
     "printWidth": 100
   }
   ```

3. **Run Formatter**
   ```bash
   pnpm prettier --write "src/**/*.{ts,tsx}"
   ```

#### Verification
```bash
# Backend
black --check apps/
# ✅ PASS if "All done! ✨ 🍰 ✨"

# Frontend
pnpm prettier --check "src/**/*.{ts,tsx}"
# ✅ PASS if no files need formatting
```

---

## 📊 Task Summary

| Task | Priority | Time | Status |
|------|----------|------|--------|
| 1.1 User Privacy Protection | P0 | 2-3h | ⏳ Pending |
| 1.2 Token Consistency | P0 | 1h | ✅ Verified |
| 1.3 CORS Update | P0 | 30m | ⏳ Pending |
| 1.4 ChromaDB Removal | P1 | 3-4h | ⏳ Pending |
| 1.5 Organize Scripts | P1 | 1h | ⏳ Pending |
| 1.6 Fix Encoding | P1 | 15m | ⏳ Pending |
| 1.7 Code Formatting | P2 | 2h | ⏳ Pending |
| **Total** | - | **~10h** | - |

---

## 🚀 Execution Order

**Day 1-2** (Critical Security):
1. Task 1.1 - User Privacy (most critical)
2. Task 1.3 - CORS Update
3. Verify with manual + automated tests

**Day 3-4** (Cleanup):
4. Task 1.4 - ChromaDB Removal
5. Task 1.5 - Organize Scripts
6. Task 1.6 - Fix Encoding

**Day 5** (Polish):
7. Task 1.7 - Code Formatting
8. Final review and documentation

---

**Next Step**: Begin execution of Task 1.1 (User Privacy Protection)
