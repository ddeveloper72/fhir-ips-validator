# Security Checklist for GitHub Commit

## ✅ Before Committing to GitHub

### 1. Environment Variables
- [ ] `.env` file is in `.gitignore` ✅
- [ ] `.env.example` has only placeholder values ✅
- [ ] No real API keys in `.env.example` ✅
- [ ] No passwords in `.env.example` ✅

### 2. Sensitive Data Check
- [ ] No API keys hardcoded in Python files ✅
- [ ] No passwords in configuration files ✅
- [ ] No Azure credentials in code ✅
- [ ] No database passwords hardcoded ✅

### 3. Validation Output Files
- [ ] `azure_validation_*.json` files in `.gitignore` ✅
- [ ] Validation HTML files in `.gitignore` ✅
- [ ] Discovery results in `.gitignore` ✅
- [ ] Test artifacts excluded ✅

### 4. Clean Repository
- [ ] `.venv/` directory excluded ✅
- [ ] `__pycache__/` excluded ✅
- [ ] `logs/` directory excluded ✅
- [ ] `.vscode/` settings excluded ✅

### 5. Documentation
- [ ] README doesn't contain sensitive data ✅
- [ ] Documentation files are safe ✅
- [ ] Example files contain only test data ✅

## 🔒 Sensitive Files to NEVER Commit

```
.env                                    # Contains real secrets
*.env                                   # Any env files
azure_validation_*.json                 # May contain PHI/PII
validation_response_*.html              # May contain patient data
evs_discovery_results.json             # May expose internal endpoints
credentials.json                        # Service account keys
api_keys.txt                           # API keys
secrets/                               # Secret directories
```

## ✅ Safe to Commit

```
.env.example                           # Template only
.gitignore                             # Security configuration
requirements.txt                       # Dependencies
scripts/*.py                           # Source code (uses env vars)
docs/*.md                              # Documentation
examples/*.json                        # Anonymized test data
README.md                              # Project documentation
```

## 🚨 If You Accidentally Commit Secrets

1. **Immediately rotate all exposed credentials:**
   - Revoke Gazelle API key
   - Rotate Azure Service Principal secret
   - Change database passwords

2. **Remove from Git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

3. **Force push:**
   ```bash
   git push origin --force --all
   ```

4. **Notify security team if enterprise repo**

## 📝 Pre-Commit Command

Run this before each commit to check for secrets:

```bash
# Search for potential secrets
grep -r "API_KEY\|PASSWORD\|SECRET" --include="*.py" --include="*.md" --exclude-dir=".venv"

# Check if .env is staged
git status | grep ".env$"

# Review what you're committing
git diff --staged
```

## ✅ Current Status

- [x] `.env` file excluded from Git
- [x] `.env.example` sanitized
- [x] Validation output files excluded
- [x] No hardcoded secrets in code
- [x] `.gitignore` properly configured
- [x] Documentation scrubbed of sensitive data

**✅ REPOSITORY IS SAFE FOR GITHUB**

## 📋 Quick Pre-Commit Checklist

```bash
# 1. Verify .env not staged
git status | grep ".env$" && echo "❌ STOP: .env is staged!" || echo "✅ Safe"

# 2. Check for validation outputs
git status | grep "azure_validation" && echo "⚠️ Validation files staged" || echo "✅ Safe"

# 3. Search staged files for secrets
git diff --staged | grep -i "api.*key\|password\|secret" && echo "⚠️ Check for secrets" || echo "✅ Safe"
```

## 🔐 Recommended: Use git-secrets

Install git-secrets to prevent committing credentials:

```bash
# Install git-secrets
# macOS
brew install git-secrets

# Configure for this repo
git secrets --install
git secrets --register-aws
git secrets --add 'API_KEY'
git secrets --add 'CLIENT_SECRET'
git secrets --add 'PASSWORD'
```
