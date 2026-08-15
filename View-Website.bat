@echo off
setlocal enabledelayedexpansion
title SportsOne - view the website
cd /d "%~dp0public"

echo.
echo  ============================================================
echo   SportsOne - viewing the finished website
echo  ============================================================
echo.
echo  This serves the built site from the "public" folder.
echo.
echo  IMPORTANT: do not open index.html by double-clicking it.
echo  The page addresses start with a slash, which a browser only
echo  understands when the site is being served. Double-clicking
echo  gives you a page with no styling. That is why this file exists.
echo.

if not exist "index.html" (
  echo  ERROR: public\index.html was not found.
  echo  You may have unzipped only part of the folder. Unzip it again.
  echo.
  pause
  exit /b 1
)

rem --- Try Hugo first: it is what the project is built with. ------------
where hugo >nul 2>nul
if %errorlevel%==0 (
  echo  Starting Hugo's file server on http://localhost:1313
  echo  Leave this window open. Press Ctrl+C here to stop.
  echo.
  start "" "http://localhost:1313/"
  cd /d "%~dp0"
  hugo server --port 1313 --disableFastRender
  goto :done
)

rem --- Then the Python launcher that ships with python.org installs. ----
where py >nul 2>nul
if %errorlevel%==0 (
  echo  Starting a local web server on http://localhost:1313
  echo  Leave this window open. Press Ctrl+C here to stop.
  echo.
  start "" "http://localhost:1313/"
  py -m http.server 1313
  goto :done
)

rem --- Then a plain python on PATH. ------------------------------------
where python >nul 2>nul
if %errorlevel%==0 (
  echo  Starting a local web server on http://localhost:1313
  echo  Leave this window open. Press Ctrl+C here to stop.
  echo.
  start "" "http://localhost:1313/"
  python -m http.server 1313
  goto :done
)

echo  Neither Hugo nor Python was found on this computer.
echo.
echo  Install ONE of these, then run this file again:
echo.
echo    Hugo (you need it to publish anyway):
echo      winget install Hugo.Hugo.Extended
echo.
echo    or Python:
echo      winget install Python.Python.3.12
echo.
echo  Close and reopen this window after installing, so Windows
echo  picks up the new program.
echo.

:done
echo.
pause
