@echo off
REM ========================================================
REM Sales & Inventory Management System - Windows Build Tool
REM ========================================================
echo.
echo ========================================================
echo Sales & Inventory Management System - Windows Build Tool
echo ========================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [Step 1/5] Installing required dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q Pillow pyinstaller

if errorlevel 1 (
    echo ERROR: Could not install dependencies
    pause
    exit /b 1
)
echo    Done!
echo.

echo [Step 2/5] Generating Application Icon...
echo    Choose icon type:
echo    [1] MCF Logo (text) - Default
echo    [2] Chicken Logo
echo.
set /p choice="    Enter choice (1 or 2, default=1): "

if "%choice%"=="" set choice=1
if "%choice%"=="2" (
    python generate_icon.py chicken
) else (
    python generate_icon.py mcf
)

if errorlevel 1 (
    echo    WARNING: Could not generate icon automatically
    echo    Using existing app.ico if available
    echo.
) else (
    echo    Icon generated successfully!
)
echo.

echo [Step 3/5] Cleaning old build files...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist __pycache__ rmdir /s /q __pycache__ 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
echo    Cleaned!
echo.

echo [Step 4/5] Building Windows executable...
echo    This may take a few minutes...
echo.
pyinstaller --clean --noconfirm micchris.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Please check the error messages above
    pause
    exit /b 1
)
echo.

echo [Step 5/5] Verifying build...
if exist "dist\Sales & Inventory Management System.exe" (
    echo    Build successful!
    echo.
    echo ========================================================
    echo BUILD COMPLETE!
    echo ========================================================
    echo.
    echo Your executable is ready at:
    echo    %CD%\dist\Sales & Inventory Management System.exe
    echo.
    echo File information:
    dir "dist\Sales & Inventory Management System.exe"
    echo.
    echo You can now:
    echo    - Run the .exe directly from the dist folder
    echo    - Copy it to any Windows computer (no installation needed)
    echo    - Create a desktop shortcut
    echo    - Distribute to other users
    echo.
) else (
    echo    WARNING: Could not verify executable automatically
    echo    Please check manually if "dist\Sales & Inventory Management System.exe" exists
    echo.
    if exist "dist" (
        echo    Contents of dist folder:
        dir /b dist
    ) else (
        echo    dist folder does not exist!
    )
    echo.
    echo    Note: If PyInstaller reported success, the file should exist.
    echo    The build may have completed successfully despite this warning.
    echo.
)

pause