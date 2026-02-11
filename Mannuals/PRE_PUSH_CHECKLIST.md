# 📤 Pre-Push Checklist

## Before Pushing to Team Repository

Use this checklist to ensure everything is ready for your team to clone and run the project.

---

## ✅ Pre-Push Checklist

### **1. Environment Files**

- [x] `.env.example` exists with all required variables
- [x] `.env` is in `.gitignore` (don't commit actual `.env`)
- [x] Default credentials are documented

**Verify:**
```bash
# Check .env.example exists
ls -la .env.example

# Verify .env is ignored
git check-ignore .env
# Should output: .env
```

---

### **2. Docker Configuration**

- [x] `docker-compose.yaml` is present
- [x] `Dockerfile` is present
- [x] Services are properly configured
- [x] Volume mounts are correct

**Verify:**
```bash
# Test build
docker compose build

# Test run
docker compose up -d

# Check status
docker compose ps
# Both containers should be "Up"
```

---

### **3. Dependencies**

- [x] `pyproject.toml` is up to date
- [x] `poetry.lock` is present (ensures reproducible builds)
- [x] All dependencies are listed in `[tool.poetry.dependencies]`

**Verify:**
```bash
# Check pyproject.toml
cat pyproject.toml

# Check poetry.lock exists
ls -l poetry.lock

# Should include:
# - fastapi
# - uvicorn
# - sqlalchemy
# - psycopg2-binary
# - python-dotenv
# - jinja2
# - python-multipart
```

---

### **4. Database Files**

- [x] Database models are committed (`app/models.py`)
- [x] CRUD operations are committed (`app/crud.py`)
- [x] Database config is committed (`app/database.py`)
- [x] Init script is committed (`init_db.py`)
- [x] Actual database files are NOT committed

**Verify:**
```bash
# These should be committed
git ls-files | grep -E "(models|crud|database).py"

# These should NOT be in repo
git ls-files | grep -E "\.db$|\.sqlite"
# Should return nothing
```

---

### **5. Documentation**

- [x] `README.md` - Main project documentation
- [x] `TEAM_SETUP_GUIDE.md` - Setup instructions
- [x] `README_DATABASE.md` - Database documentation
- [x] `.env.example` - Environment template

**Verify:**
```bash
# Check all docs exist
ls -la README.md TEAM_SETUP_GUIDE.md README_DATABASE.md .env.example
```

---

### **6. Test Files**

- [x] Test scripts are included
- [x] Tests pass successfully

**Verify:**
```bash
# Run tests
python3 test_crud_operations.py
python3 test_db_integration.py

# All tests should pass ✅
```

---

### **7. Git Status**

- [x] No sensitive files in staging
- [x] `.gitignore` is properly configured
- [x] All necessary files are tracked

**Verify:**
```bash
# Check what will be committed
git status

# Check for sensitive files
git status | grep -E "\.env$|\.db$|\.sqlite"
# Should return nothing

# Check .gitignore
cat .gitignore
```

---

### **8. Application Functionality**

- [x] Application starts successfully
- [x] Database connection works
- [x] Can create projects
- [x] Can add/edit/delete nodes
- [x] Data persists after restart

**Verify:**
```bash
# Start application
docker compose up -d

# Open browser
# http://localhost:8000

# Test:
# 1. Create a project ✅
# 2. Add a node ✅
# 3. Edit a node ✅
# 4. Delete a node ✅
# 5. Restart: docker compose restart
# 6. Data still there ✅
```

---

### **9. Clean Up**

- [x] Remove test data (optional)
- [x] Remove personal configurations
- [x] Remove debug code
- [x] Remove commented code

**Clean up:**
```bash
# Optional: Clear test data
docker compose down -v
docker compose up -d

# This gives your team a fresh start
```

---

### **10. Final Verification**

- [x] Build succeeds
- [x] All tests pass
- [x] Documentation is complete
- [x] No secrets in repository

**Final check:**
```bash
# Clean build test
docker compose down -v
docker compose up --build -d

# Check logs
docker compose logs -f

# Should see:
# ✅ Database started
# ✅ Web app started
# ✅ No errors
```

---

## 🚀 Ready to Push!

### **Push Commands**

```bash
# Add all files
git add .

# Commit with descriptive message
git commit -m "feat: Add PostgreSQL database integration

- Integrated PostgreSQL for persistent storage
- Added SQLAlchemy ORM models
- Implemented CRUD operations
- Added Docker Compose configuration
- Updated documentation
- All features tested and working"

# Push to repository
git push origin main
```

---

## 📋 What Your Team Will Need to Do

After you push, your team members will:

### **Step 1: Clone**
```bash
git clone <repo-url>
cd Caresoft
```

### **Step 2: Setup Environment**
```bash
cp .env.example .env
```

### **Step 3: Start Application**
```bash
docker compose up --build -d
```

### **Step 4: Access Application**
```
http://localhost:8000
```

**That's it!** 🎉

---

## 📝 Files to Commit

### **Essential Files:**
```
✅ app/main.py
✅ app/database.py
✅ app/models.py
✅ app/crud.py
✅ static/css/styles.css
✅ static/js/app.js
✅ templates/index.html
✅ docker-compose.yaml
✅ Dockerfile
✅ pyproject.toml
✅ poetry.lock
✅ .env.example
✅ .gitignore
✅ README.md
✅ TEAM_SETUP_GUIDE.md
✅ README_DATABASE.md
✅ init_db.py
✅ test_*.py (test files)
```

### **Files to NOT Commit:**
```
❌ .env (actual environment file)
❌ *.db (database files)
❌ *.sqlite (SQLite files)
❌ __pycache__/ (Python cache)
❌ .vscode/ (IDE settings)
❌ .idea/ (IDE settings)
❌ *.log (log files)
```

---

## 🔍 Quick Verification Script

Run this before pushing:

```bash
#!/bin/bash

echo "🔍 Pre-Push Verification..."

# Check .env is not staged
if git diff --cached --name-only | grep -q "^\.env$"; then
    echo "❌ ERROR: .env file is staged! Remove it!"
    exit 1
fi

# Check .env.example exists
if [ ! -f .env.example ]; then
    echo "❌ ERROR: .env.example not found!"
    exit 1
fi

# Check docker-compose.yaml exists
if [ ! -f docker-compose.yaml ]; then
    echo "❌ ERROR: docker-compose.yaml not found!"
    exit 1
fi

# Check README exists
if [ ! -f README.md ]; then
    echo "❌ ERROR: README.md not found!"
    exit 1
fi

# Test build
echo "🔨 Testing Docker build..."
if ! docker compose build; then
    echo "❌ ERROR: Docker build failed!"
    exit 1
fi

echo "✅ All checks passed! Ready to push!"
```

Save as `pre-push-check.sh` and run:
```bash
chmod +x pre-push-check.sh
./pre-push-check.sh
```

---

## ✅ Final Checklist Summary

Before pushing, ensure:

- [ ] `.env` is NOT committed
- [ ] `.env.example` IS committed
- [ ] `docker-compose.yaml` IS committed
- [ ] All documentation IS committed
- [ ] Database files are NOT committed
- [ ] Application builds successfully
- [ ] All tests pass
- [ ] Documentation is complete

---

## 🎉 You're Ready!

Once all checks pass, push your code and share the `TEAM_SETUP_GUIDE.md` with your team!

**Your team will be able to:**
1. Clone the repo
2. Run `docker compose up --build -d`
3. Start working immediately!

**No complex setup required!** 🚀

---

**Good luck with your team collaboration!** 👥
