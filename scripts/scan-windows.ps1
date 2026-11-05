$ErrorActionPreference = 'Stop'
$folder = (Resolve-Path 'dist/LittleBoar').Path
$scanner = Get-ChildItem "$env:ProgramData/Microsoft/Windows Defender/Platform/*/MpCmdRun.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
if (-not $scanner) {
    $fallback = "$env:ProgramFiles/Windows Defender/MpCmdRun.exe"
    if (-not (Test-Path $fallback)) { throw 'Windows Defender unavailable; artifact will not be published.' }
    $scannerPath = $fallback
} else { $scannerPath = $scanner.FullName }
& $scannerPath -SignatureUpdate
if ($LASTEXITCODE -ne 0) { throw 'Defender signature update failed; artifact will not be published.' }
# Disable remediation so detections fail the build rather than silently removing files.
& $scannerPath -Scan -ScanType 3 -File $folder -DisableRemediation
if ($LASTEXITCODE -ne 0) { throw 'Defender scan failed or detected a threat; artifact will not be published.' }
$hashes = Get-ChildItem $folder -Recurse -File | Sort-Object FullName | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    "$hash  $([IO.Path]::GetRelativePath($folder, $_.FullName))"
}
$hashes | Set-Content 'dist/LittleBoar/SHA256SUMS.txt'
"Defender scan completed successfully. Source commit: $env:GITHUB_SHA" | Set-Content 'dist/LittleBoar/SCAN.txt'
