@echo off
setlocal
title SportsOne - Publishing Tool
cd /d "%~dp0"

echo.
echo  ============================================================
echo   SPORTSONE - THE PUBLISHING TOOL
echo  ============================================================
echo.
echo   This opens the publishing tool in your web browser.
echo.
echo   LEAVE THIS BLACK WINDOW OPEN while you are working.
echo   Closing it closes the tool.
echo.

rem --- Find Python. -----------------------------------------------------
rem Written as separate checks rather than nested IFs on purpose: inside a
rem bracketed block %errorlevel% still holds the value it had before the
rem block started, which is the commonest bug there is in a .bat file.
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py"
if not defined PY goto :nopython

rem --- Hugo has to be there: it builds every preview. --------------------
where hugo >nul 2>nul
if not %errorlevel%==0 goto :nohugo

rem --- Pillow resizes the photographs. Installed once, quietly. ----------
%PY% -c "import PIL" >nul 2>nul
if not %errorlevel%==0 (
  echo   Setting up the picture tool. This happens once and takes
  echo   about twenty seconds...
  echo.
  %PY% -m pip install --quiet --disable-pip-version-check Pillow
)

%PY% scripts\cms\server.py
goto :end

:nopython
echo   PROBLEM: Python is not installed on this computer.
echo.
echo   The tool needs it. To install it, open the Start menu, type
echo   "Command Prompt", open it, and paste in this line:
echo.
echo       winget install Python.Python.3.12
echo.
echo   Then CLOSE this window, open it again, and double-click
echo   this file a second time.
echo.
pause
exit /b 1

:nohugo
echo   PROBLEM: Hugo is not installed on this computer.
echo.
echo   Hugo is the program that builds SportsOne, and it draws
echo   every preview in the tool. To install it, open the Start
echo   menu, type "Command Prompt", open it, and paste in this line:
echo.
echo       winget install Hugo.Hugo.Extended
echo.
echo   Then CLOSE this window, open it again, and double-click
echo   this file a second time.
echo.
pause
exit /b 1

:end
echo.
echo   The tool has closed. Nothing you saved has been lost.
echo.
pause
