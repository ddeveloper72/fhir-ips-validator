# Quick Reference: What to Commit vs. Keep Local

## ✅ ALWAYS COMMIT (Version Control)

### Code Files
- `*.py` - All Python source code
- `streamlit_app.py` - Main application
- `scripts/*.py` - Utility scripts
- `src/**/*.py` - Source code modules

### Configuration Templates
- `.env.example` - Template with placeholders ✅
- `.env.local.example` - Local config template ✅
- `.gitignore` - Git exclusion rules ✅
- `requirements.txt` - Dependencies ✅
- `pyproject.toml` - Project metadata ✅

### Documentation
- `README.md` - Project overview ✅
- `docs/*.md` - All documentation ✅
- `SECURITY_CHECKLIST.md` ✅
- Example files for tutorials ✅

### Example Data
- `examples/*.json` - Sample FHIR bundles ✅
- `examples/*.xml` - Sample CDA documents ✅
- `examples/README.md` ✅

### Tests
- `tests/**/*.py` - All test files ✅
- `tests/fixtures/*.json` - Test data ✅

### CI/CD & GitHub
- `.github/**/*.md` - GitHub configuration ✅
- `.github/workflows/*.yml` - CI/CD pipelines ✅
- `.pre-commit-config.yaml` ✅

---

## ❌ NEVER COMMIT (Keep Local)

### Secrets & Credentials
- `.env` - Contains REAL API keys ❌
- `.env.local` - Local secrets ❌
- `credentials.json` ❌
- `api_keys.txt` ❌
- Any file with actual passwords/tokens ❌

### Virtual Environment
- `.venv/` - Python virtual environment ❌
- `venv/` ❌
- Contains ~2000+ package files ❌

### IDE Settings (Personal)
- `.vscode/` - VS Code workspace settings ❌
- `.idea/` - PyCharm settings ❌
- `*.swp`, `*.swo` - Editor temporary files ❌

### Output Files
- `azure_validation_*.json` - Validation results ❌
- `validation_response_*.html` - HTML reports ❌
- `validator_page.html` - Downloaded pages ❌
- `*_discovery_results.json` - API exploration ❌
- `report_*.html` - Generated reports ❌

### Logs & Debug Files
- `logs/*.html` - Log files ❌
- `logs/*.xml` - Debug output ❌
- `*.log` - Any log files ❌
- `.codacy/logs/*.log` - Tool logs ❌

### Cache & Temp Files
- `__pycache__/` - Python bytecode ❌
- `*.pyc`, `*.pyo` - Compiled Python ❌
- `.pytest_cache/` - Test cache ❌
- `.mypy_cache/` - Type checking cache ❌
- `*.tmp`, `*.temp` - Temporary files ❌

---

## 🤔 SITUATIONAL (Case by Case)

### Test Output
- `.coverage` - Coverage data (commit if tracking over time)
- `htmlcov/` - HTML coverage report (usually local)
- `coverage.xml` - For CI/CD (usually commit)

### Documentation Builds
- `docs/_build/` - Local only ❌
- `site/` - Generated docs (local) ❌
- Published docs go to GitHub Pages, not repo

---

## 🎯 Quick Decision Tree

```
Is it a SECRET or CREDENTIAL?
├─ YES → ❌ NEVER commit (.env, passwords, API keys)
└─ NO → Continue...

Can it be REGENERATED from source code?
├─ YES → ❌ Keep local (output files, logs, cache)
└─ NO → Continue...

Is it PERSONAL preference (IDE settings)?
├─ YES → ❌ Keep local (.vscode, .idea)
└─ NO → Continue...

Is it SOURCE CODE or DOCUMENTATION?
├─ YES → ✅ COMMIT IT
└─ NO → Is it a template/example?
         ├─ YES → ✅ COMMIT IT (.env.example)
         └─ NO → ❌ Probably keep local
```

---

## 📝 Before Every Commit

Run this checklist:

```powershell
# 1. Check what's changed
git status

# 2. Review actual changes
git diff

# 3. Look for sensitive patterns
git diff | Select-String -Pattern "api_key|password|secret|token"

# 4. Stage only intended files
git add <specific-files>
# NOT: git add . (too risky)

# 5. Review staged changes
git diff --cached

# 6. Commit with descriptive message
git commit -m "feat: add new feature"

# 7. Final check before push
git log -1 --stat
```

---

## 🚨 Emergency: Committed Something Sensitive?

### If NOT pushed yet:
```powershell
# Remove from last commit (keep changes)
git reset --soft HEAD~1

# Remove from staging
git reset HEAD <file>

# Edit file, then commit again
```

### If already PUSHED:
```powershell
# 1. Remove the file from Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Force push (⚠️ careful!)
git push --force --all

# 3. IMMEDIATELY rotate the exposed credentials
# - Generate new API key at https://gazelle.ehdsi.eu
# - Update .env with new key
# - The old key is now compromised!
```

---

## ✅ Current Status

Your repository is **SECURE**:
- ✅ `.env` is protected by `.gitignore`
- ✅ No sensitive data was committed
- ✅ 110 files safely committed
- ✅ ~30 local files excluded (can be deleted)

---

## 🛠️ Maintenance Commands

```powershell
# Clean local output files
.\cleanup_local_files.ps1

# Verify git status
git status

# See what's ignored
git status --ignored

# Check for large files before commit
git ls-files | ForEach-Object { Get-Item $_ } | Sort-Object Length -Descending | Select-Object -First 10

# Verify nothing sensitive is tracked
git ls-files | Select-String -Pattern "\.env$|credentials|secrets|key"
```

---

## 📚 Resources

- **Security Audit Report:** `SECURITY_AUDIT_REPORT.md`
- **Cleanup Script:** `cleanup_local_files.ps1`
- **Git Docs:** https://git-scm.com/doc
- **GitHub Security:** https://docs.github.com/en/code-security

---

**Last Updated:** May 19, 2026  
**Applies to:** FHIR IPS Validator Project
