param([string]$InstallRoot = '', [switch]$Overwrite)

$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot 'skill'
if (-not (Test-Path -LiteralPath $source -PathType Container)) { $source = Join-Path $PSScriptRoot 'skills' }
if (-not (Test-Path -LiteralPath $source -PathType Container)) { throw 'No skill/ or skills/ directory was found.' }
if ([string]::IsNullOrWhiteSpace($InstallRoot)) { $InstallRoot = Join-Path $env:USERPROFILE '.codex\skills' }
$InstallRoot = [IO.Path]::GetFullPath($InstallRoot)
New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
$programs = [ordered]@{}
$appsRoot = Join-Path $PSScriptRoot 'apps'
if (Test-Path -LiteralPath $appsRoot -PathType Container) {
    Get-ChildItem -LiteralPath $appsRoot -Directory | ForEach-Object { $programs[$_.Name] = $_.FullName }
}
$installed = 0
$skipped = 0
Get-ChildItem -LiteralPath $source -Directory | ForEach-Object {
    $skillFile = Join-Path $_.FullName 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) { throw "SKILL.md is missing: $($_.Name)" }
    $dest = Join-Path $InstallRoot $_.Name
    if (Test-Path -LiteralPath $dest) {
        if ($Overwrite) {
            $backup = "$dest.backup-$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfff'))"
            Copy-Item -LiteralPath $dest -Destination $backup -Recurse
            Copy-Item -Path (Join-Path $_.FullName '*') -Destination $dest -Recurse -Force
            $installed++
            Write-Host "Updated with backup: $($_.Name)"
        } else {
            $skipped++
            Write-Host "Existing Skill preserved; package paths refreshed: $($_.Name)"
        }
    } else {
        Copy-Item -LiteralPath $_.FullName -Destination $dest -Recurse
        $installed++
        Write-Host "Installed: $($_.Name)"
    }
    $location = [ordered]@{ schema_version = 1; package_root = $PSScriptRoot; apps = $programs }
    $json = $location | ConvertTo-Json -Depth 5
    [IO.File]::WriteAllText((Join-Path $dest 'PACKAGE-LOCATION.json'), $json, (New-Object Text.UTF8Encoding($false)))
}
Write-Host "Done. Installed/updated: $installed; existing preserved: $skipped. Keep the extracted package folder."
Write-Host 'If the package is moved, run this installer again to refresh paths. Reopen Codex to reload Skills.'
