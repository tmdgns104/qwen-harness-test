@echo off
setlocal

set "TOOL_DIR=%~dp0"
if "%TOOL_DIR:~-1%"=="\" set "TOOL_DIR=%TOOL_DIR:~0,-1%"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$tool='%TOOL_DIR%';" ^
  "$p=[Environment]::GetEnvironmentVariable('Path','User');" ^
  "$parts=@($p -split ';' | Where-Object { $_ -and $_.Trim() });" ^
  "if ($parts -contains $tool) { Write-Host 'qhops PATH already configured:' $tool; exit 0 };" ^
  "$new=if ([string]::IsNullOrWhiteSpace($p)) { $tool } else { $p.TrimEnd(';') + ';' + $tool };" ^
  "[Environment]::SetEnvironmentVariable('Path',$new,'User');" ^
  "Write-Host 'qhops PATH added:' $tool;" ^
  "Write-Host 'Open a new CMD window, then run: qhops init ^<repository-path^>'"

if errorlevel 1 (
  echo Failed to add qhops to User PATH.
  exit /b 1
)

endlocal
