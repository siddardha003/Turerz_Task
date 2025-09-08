@echo off
REM Setup script to initialize MSVC environment and install Playwright
REM This batch script sets up the Visual Studio environment

echo 🚀 Setting up MSVC environment for Playwright installation
echo.

REM Try to find and call vcvarsall.bat to set up MSVC environment
set "VCVARSALL_2019=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
set "VCVARSALL_2022=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"

if exist "%VCVARSALL_2022%" (
    echo ✅ Found VS 2022 Build Tools
    call "%VCVARSALL_2022%" x64
    goto :install
)

if exist "%VCVARSALL_2019%" (
    echo ✅ Found VS 2019 Build Tools  
    call "%VCVARSALL_2019%" x64
    goto :install
)

echo ❌ Could not find vcvarsall.bat
echo Please check Visual Studio Build Tools installation
pause
exit /b 1

:install
echo.
echo 🔧 MSVC environment activated
echo 📦 Installing Python packages...

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Install packages with compilation support
pip install greenlet==3.0.1
if %errorlevel% neq 0 (
    echo ❌ Failed to install greenlet
    pause
    exit /b 1
)

pip install playwright==1.40.0
if %errorlevel% neq 0 (
    echo ❌ Failed to install playwright
    pause
    exit /b 1
)

pip install pytest-playwright==0.4.3
if %errorlevel% neq 0 (
    echo ❌ Failed to install pytest-playwright
    pause
    exit /b 1
)

echo.
echo ✅ Packages installed successfully!
echo 🌐 Installing Playwright browsers...

playwright install
if %errorlevel% neq 0 (
    echo ❌ Failed to install Playwright browsers
    pause
    exit /b 1
)

echo.
echo 🎉 Installation complete!
echo.
echo 🧪 Running test to verify installation...
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright imported successfully')"

echo.
echo ✅ Setup complete! You can now use Playwright in your project.
pause
