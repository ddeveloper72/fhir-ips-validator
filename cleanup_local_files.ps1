# Cleanup script for FHIR IPS Validator
# Purpose: Remove local output files that don't need to be version controlled
# Safe to run - only removes files already in .gitignore

Write-Host "`n🧹 FHIR IPS Validator - Local File Cleanup" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "streamlit_app.py")) {
    Write-Host "❌ Error: Run this script from the project root directory" -ForegroundColor Red
    exit 1
}

$removedCount = 0
$totalSize = 0

# Output files to remove
$filePatterns = @(
    "azure_validation_*.json",
    "validation_response_*.html",
    "validator_page.html",
    "evs_discovery_results.json",
    "fhir_r4_discovery_results.json"
)

Write-Host "`n📋 Scanning for output files..." -ForegroundColor Yellow

foreach ($pattern in $filePatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $size = $file.Length
        $totalSize += $size
        Write-Host "  ✓ Removing: $($file.Name) ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Gray
        Remove-Item $file.FullName -Force
        $removedCount++
    }
}

# Codacy logs
if (Test-Path ".codacy/logs") {
    $codacyLogs = Get-ChildItem -Path ".codacy/logs" -Filter "*.log" -ErrorAction SilentlyContinue
    if ($codacyLogs.Count -gt 0) {
        Write-Host "`n📋 Codacy logs found..." -ForegroundColor Yellow
        foreach ($log in $codacyLogs) {
            $size = $log.Length
            $totalSize += $size
            Write-Host "  ✓ Removing: $($log.Name) ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Gray
            Remove-Item $log.FullName -Force
            $removedCount++
        }
    }
}

# Optional: Clean logs directory
if (Test-Path "logs") {
    Write-Host "`n📁 Logs directory found" -ForegroundColor Yellow
    $logFiles = Get-ChildItem -Path "logs" -File -Recurse
    $logCount = $logFiles.Count
    $logSize = ($logFiles | Measure-Object -Property Length -Sum).Sum
    
    Write-Host "  Found $logCount log files ($([math]::Round($logSize/1KB, 2)) KB total)" -ForegroundColor Gray
    $cleanLogs = Read-Host "  Remove all log files? (y/n)"
    
    if ($cleanLogs -eq 'y') {
        foreach ($log in $logFiles) {
            Remove-Item $log.FullName -Force
            $removedCount++
        }
        $totalSize += $logSize
        Write-Host "  ✓ Logs cleaned" -ForegroundColor Green
    } else {
        Write-Host "  ⏭️  Skipping logs" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "✅ Cleanup Complete!" -ForegroundColor Green
Write-Host "  Files removed: $removedCount" -ForegroundColor White
Write-Host "  Space freed: $([math]::Round($totalSize/1KB, 2)) KB" -ForegroundColor White

# Verify git status
Write-Host "`n🔍 Checking git status..." -ForegroundColor Cyan
$gitStatus = & git status --short 2>$null
if ($LASTEXITCODE -eq 0) {
    if ($gitStatus) {
        Write-Host "$gitStatus" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Working tree clean - no changes to commit" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Git not available or not a git repository" -ForegroundColor Yellow
}

Write-Host "`n💡 Tip: These files are in .gitignore and will be regenerated as needed`n" -ForegroundColor Cyan
