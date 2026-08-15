@echo off
setlocal
title SportsOne - rebuild the distributable site
cd /d "%~dp0"

echo.
echo  ============================================================
echo   SportsOne - rebuilding the "public" folder
echo  ============================================================
echo.
echo  This regenerates the finished website into public\ using the
echo  live address https://sportsone.world/ . Upload the CONTENTS
echo  of public\ to your web host.
echo.

where hugo >nul 2>nul
if not %errorlevel%==0 (
  echo  ERROR: Hugo is not installed.
  echo    winget install Hugo.Hugo.Extended
  echo.
  pause
  exit /b 1
)

set HUGO_ENVIRONMENT=production
hugo --minify --gc --cleanDestinationDir --baseURL "https://sportsone.world/"

if errorlevel 1 (
  echo.
  echo  The build FAILED. Nothing was published. The error is above.
  echo  Most often this is a typo in a data file - see docs\05-troubleshooting.md
  echo.
  pause
  exit /b 1
)

echo.
echo  Done. The finished site is in the public folder.
echo.
pause
