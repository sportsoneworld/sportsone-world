@echo off
setlocal
title SportsOne - write and preview
cd /d "%~dp0"

echo.
echo  ============================================================
echo   SportsOne - writing mode
echo  ============================================================
echo.
echo  This starts Hugo's live preview. Edit any file under
echo  content\ and the browser refreshes as you save.
echo.

where hugo >nul 2>nul
if not %errorlevel%==0 (
  echo  ERROR: Hugo is not installed, or is not on your PATH.
  echo.
  echo    winget install Hugo.Hugo.Extended
  echo.
  echo  Then close this window, open a new one, and try again.
  echo  Check it worked with:  hugo version
  echo  The output must contain the word "extended".
  echo.
  pause
  exit /b 1
)

for /f "tokens=*" %%v in ('hugo version') do set HUGOVER=%%v
echo  Using: %HUGOVER%
echo.
echo  %HUGOVER% | find /i "extended" >nul
if errorlevel 1 (
  echo  WARNING: this looks like the PLAIN edition of Hugo.
  echo  This project needs the EXTENDED edition to build its stylesheet.
  echo    winget uninstall Hugo.Hugo
  echo    winget install Hugo.Hugo.Extended
  echo.
  pause
)

echo  Opening http://localhost:1313
echo  Leave this window open. Press Ctrl+C here to stop.
echo.
start "" "http://localhost:1313/"
hugo server --port 1313 --disableFastRender --navigateToChanged
echo.
pause
