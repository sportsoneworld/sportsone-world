@echo off
setlocal
title SportsOne - import the Inbox
cd /d "%~dp0"

echo.
echo  ============================================================
echo   SportsOne - importing everything in the Inbox
echo  ============================================================
echo.
echo  This looks in the "inbox" folder for stories and pictures
echo  that share a name:
echo.
echo     Article-1.md  +  Article-1.jpg
echo     Article-2.txt +  Article-2.png
echo.
echo  It resizes each picture, writes each story into the site,
echo  puts stories on the front page where you asked, and then
echo  empties the inbox.
echo.

rem Find Python. Written as separate checks rather than nested IFs on purpose:
rem inside a bracketed block, %errorlevel% still holds the value it had before
rem the block started, which is the single most common bug in a .bat file.
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py"
if not defined PY goto :nopython
goto :haspython

:nopython
echo  ERROR: Python is not installed.
echo.
echo    winget install Python.Python.3.12
echo.
echo  Then close this window, open a new one, and try again.
echo.
pause
exit /b 1

:haspython

echo  Checking the picture tool...
%PY% -c "import PIL" >nul 2>nul
if not %errorlevel%==0 (
  echo  Installing it, once. This takes about twenty seconds.
  %PY% -m pip install --quiet --disable-pip-version-check Pillow
)

echo.
%PY% scripts\import-articles.py inbox
if errorlevel 1 (
  echo.
  echo  The import FAILED. Nothing was published. The error is above.
  echo  Your files are still in the inbox - nothing was lost.
  echo.
  pause
  exit /b 1
)

echo.
echo  ------------------------------------------------------------
echo   Next steps
echo  ------------------------------------------------------------
echo   1. Double-click Edit-Website.bat to read the stories through
echo      before anyone else does.
echo   2. When you are happy, publish them the usual way.
echo.
pause
