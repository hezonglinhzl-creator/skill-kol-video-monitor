$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot 'skill'
$skill = Get-ChildItem -LiteralPath $source -Directory | Select-Object -First 1
if (-not $skill -or -not (Test-Path -LiteralPath (Join-Path $skill.FullName 'SKILL.md'))) { throw 'Skill files are missing.' }
$targetRoot = Join-Path $env:USERPROFILE '.codex\skills'
$target = Join-Path $targetRoot $skill.Name
New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
if (Test-Path -LiteralPath $target) { Write-Host "Already installed: $target"; exit 0 }
Copy-Item -LiteralPath $skill.FullName -Destination $target -Recurse
Write-Host "Installed: $target"
