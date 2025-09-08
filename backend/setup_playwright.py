"""
Python script to set up MSVC environment and install Playwright.
This script finds the Visual Studio installation and sets up the environment.
"""

import os
import subprocess
import sys
from pathlib import Path

def find_vs_installation():
    """Find Visual Studio installation path."""
    possible_paths = [
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools",
        "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community",
        "C:\\Program Files\\Microsoft Visual Studio\\2019\\Community",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\Professional",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Professional",
        "C:\\Program Files\\Microsoft Visual Studio\\2022\\Professional",
        "C:\\Program Files\\Microsoft Visual Studio\\2019\\Professional"
    ]
    
    for path in possible_paths:
        vs_path = Path(path)
        vcvarsall = vs_path / "VC" / "Auxiliary" / "Build" / "vcvarsall.bat"
        if vcvarsall.exists():
            return str(vcvarsall)
    
    return None

def setup_msvc_environment():
    """Set up MSVC environment variables."""
    vcvarsall = find_vs_installation()
    if not vcvarsall:
        print("❌ Could not find Visual Studio installation")
        return False
    
    print(f"✅ Found vcvarsall.bat at: {vcvarsall}")
    
    # Run vcvarsall.bat and capture environment
    print("🔧 Setting up MSVC environment...")
    cmd = f'"{vcvarsall}" x64 && set'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to run vcvarsall.bat: {result.stderr}")
            return False
        
        # Parse environment variables from output
        env_vars = {}
        for line in result.stdout.split('\n'):
            if '=' in line and not line.startswith('='):
                key, value = line.split('=', 1)
                env_vars[key] = value
        
        # Update current environment
        os.environ.update(env_vars)
        print("✅ MSVC environment variables set")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up environment: {e}")
        return False

def install_packages():
    """Install Python packages with compilation support."""
    packages = [
        "greenlet==3.0.1",
        "playwright==1.40.0", 
        "pytest-playwright==0.4.3"
    ]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Exception installing {package}: {e}")
            return False
    
    return True

def install_browsers():
    """Install Playwright browsers."""
    print("🌐 Installing Playwright browsers...")
    try:
        result = subprocess.run([sys.executable, "-m", "playwright", "install"], 
                             capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully")
            return True
        else:
            print(f"❌ Failed to install browsers: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception installing browsers: {e}")
        return False

def test_installation():
    """Test that Playwright is working."""
    print("🧪 Testing Playwright installation...")
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            "from playwright.sync_api import sync_playwright; print('✅ Playwright working!')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Playwright test passed!")
            return True
        else:
            print(f"❌ Playwright test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception testing Playwright: {e}")
        return False

def main():
    """Main installation process."""
    print("🚀 Turerz Playwright Installation with MSVC Setup")
    print("=" * 60)
    
    # Step 1: Set up MSVC environment
    if not setup_msvc_environment():
        print("\n💡 Alternative approaches:")
        print("1. Open 'Developer Command Prompt for VS 2019/2022'")
        print("2. Navigate to this directory")
        print("3. Activate virtual environment: .venv\\Scripts\\activate")
        print("4. Run: pip install playwright==1.40.0")
        return False
    
    # Step 2: Install packages
    if not install_packages():
        print("\n❌ Package installation failed")
        return False
    
    # Step 3: Install browsers
    if not install_browsers():
        print("\n⚠️ Browser installation failed, but packages are installed")
        print("You can try running 'playwright install' manually later")
    
    # Step 4: Test installation
    if test_installation():
        print("\n🎉 Installation complete and verified!")
        return True
    else:
        print("\n⚠️ Installation complete but test failed")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Ready to use Playwright!")
        print("Next: Update requirements.txt and run browser tests")
    else:
        print("\n❌ Installation had issues")
        print("Check the error messages above for troubleshooting")
    
    input("\nPress Enter to continue...")
    sys.exit(0 if success else 1)
