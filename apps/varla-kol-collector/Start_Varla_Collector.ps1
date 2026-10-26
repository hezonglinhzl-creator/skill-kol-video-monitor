$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$kolDir = Join-Path $root "KOL_recorder"
$viralDir = Join-Path $root "viral_video_finder"

function Resolve-Python {
  $candidates = @()
  if ($env:VARLA_PYTHON_CMD) {
    $candidates += $env:VARLA_PYTHON_CMD
  }
  $candidates += Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  $candidates += "python"
  $candidates += "py"

  foreach ($candidate in $candidates) {
    try {
      $process = Start-Process -FilePath $candidate -ArgumentList "--version" -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$env:TEMP\varla_python_stdout.txt" -RedirectStandardError "$env:TEMP\varla_python_stderr.txt"
      if ($process.ExitCode -eq 0) {
        return $candidate
      }
    } catch {
      continue
    }
  }

  throw "Python 3.10+ was not found. Install Python from python.org or run this from Codex where bundled Python is available."
}

$env:VARLA_PYTHON_CMD = Resolve-Python

Write-Host "Starting Varla Collector..."
Write-Host ""
Write-Host "Python:"
Write-Host $env:VARLA_PYTHON_CMD
Write-Host ""
Write-Host "Two service windows will open:"
Write-Host "- KOL recorder: http://127.0.0.1:8765"
Write-Host "- Viral video center: http://127.0.0.1:8766"
Write-Host ""
Write-Host "Keep both black windows open while using the Chrome extension."

Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$kolDir`" && call start_kol_recorder.bat"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$viralDir`" && call start_viral_video_finder.bat"

Start-Sleep -Seconds 4
Start-Process "http://127.0.0.1:8765"
Start-Process "http://127.0.0.1:8766"

Write-Host "Done. You can close this launcher window."
