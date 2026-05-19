#!/usr/bin/env python3
"""
Pre-commit security check script
Scans for potential secrets before Git commit
"""

import os
import re
import sys
from pathlib import Path

# Patterns to detect secrets
SECRET_PATTERNS = [
    (r'[A-Za-z0-9]{40,}', 'Potential API Key or Token (40+ chars)'),
    (r'sk-[A-Za-z0-9]{32,}', 'Potential Secret Key'),
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub Personal Access Token'),
    (r'glpat-[A-Za-z0-9\-_]{20,}', 'GitLab Personal Access Token'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'-----BEGIN[A-Z ]+PRIVATE KEY-----', 'Private Key'),
    (r'password\s*[=:]\s*[\'"][^\'"]{3,}', 'Password in config'),
    (r'api[_-]?key\s*[=:]\s*[\'"][^\'"]{10,}', 'API Key in config'),
    (r'client[_-]?secret\s*[=:]\s*[\'"][^\'"]{10,}', 'Client Secret'),
]

# Files/directories to always skip
SKIP_PATHS = {
    '.venv', 'venv', '__pycache__', '.git', 'node_modules',
    '.pytest_cache', '.tox', 'dist', 'build', 'logs',
    '.env.example', 'SECURITY_CHECKLIST.md', '.codacy',
    'check_secrets.py', 'GIT_SETUP_GUIDE.md'
}

# Extensions to scan
SCAN_EXTENSIONS = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.sh', '.env'}

def should_scan(path):
    """Check if file should be scanned"""
    # Skip if in excluded directory
    for skip in SKIP_PATHS:
        if skip in str(path):
            return False
    
    # Skip if wrong extension
    if path.suffix not in SCAN_EXTENSIONS:
        return False
    
    return True

def scan_file(file_path):
    """Scan a single file for secrets"""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            for pattern, description in SECRET_PATTERNS:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    findings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'match': match.group()[:50],  # First 50 chars
                        'type': description
                    })
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    
    return findings

def main():
    """Main security scan"""
    print("🔍 Scanning for secrets before commit...\n")
    
    repo_root = Path(__file__).parent
    all_findings = []
    
    # Scan all relevant files
    for file_path in repo_root.rglob('*'):
        if file_path.is_file() and should_scan(file_path):
            findings = scan_file(file_path)
            all_findings.extend(findings)
    
    # Report findings
    if all_findings:
        print("⚠️  POTENTIAL SECRETS DETECTED!\n")
        print("="*80)
        
        for finding in all_findings:
            print(f"\n📄 File: {finding['file']}")
            print(f"   Line: {finding['line']}")
            print(f"   Type: {finding['type']}")
            print(f"   Match: {finding['match']}...")
        
        print("\n" + "="*80)
        print("\n❌ COMMIT BLOCKED - Review and remove secrets before committing")
        print("\nIf these are false positives, add them to SKIP_PATTERNS in this script.")
        return 1
    
    else:
        print("✅ No secrets detected - safe to commit!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
