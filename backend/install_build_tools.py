"""
Windows Build Tools Installation Guide for Turerz
This script helps install the necessary build tools for Playwright compilation.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_build_tools():
    """Check if Visual Studio Build Tools are installed."""
    print("🔍 Checking for Visual Studio Build Tools...")
    
    # Common paths where VS Build Tools might be installed
    vs_paths = [
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools", 
        "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community",
        "C:\\Program Files\\Microsoft Visual Studio\\2019\\Community",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\Professional",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Professional"
    ]
    
    for path in vs_paths:
        if Path(path).exists():
            print(f"✅ Found Visual Studio installation at: {path}")
            return True
    
    print("❌ Visual Studio Build Tools not found")
    return False

def check_compiler():
    """Check if cl.exe (MSVC compiler) is available."""
    print("\n🔍 Checking for MSVC compiler...")
    
    try:
        result = subprocess.run(['cl'], capture_output=True, text=True)
        if result.returncode != 0:  # cl.exe shows help and exits with error code
            print("✅ MSVC compiler (cl.exe) is available")
            return True
    except FileNotFoundError:
        print("❌ MSVC compiler (cl.exe) not found in PATH")
        return False
    
    return False

def download_vs_buildtools():
    """Provide instructions for downloading VS Build Tools."""
    print("\n📥 Visual Studio Build Tools Installation Instructions:")
    print("=" * 60)
    print("1. Download Visual Studio Build Tools from:")
    print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    print("\n2. Run the installer and select:")
    print("   ✅ C++ build tools")
    print("   ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools")
    print("   ✅ Windows 11 SDK (or Windows 10 SDK)")
    print("   ✅ CMake tools for Visual Studio")
    print("\n3. After installation, restart your terminal/VS Code")
    print("\n4. Run this script again to verify installation")

def install_with_conda():
    """Alternative: Install using conda which has pre-compiled packages."""
    print("\n🐍 Alternative: Use Conda for Pre-compiled Packages")
    print("=" * 50)
    print("If you have Anaconda/Miniconda installed:")
    print("1. conda create -n turerz python=3.11")
    print("2. conda activate turerz") 
    print("3. conda install -c conda-forge playwright")
    print("4. playwright install")

def install_with_wheels():
    """Try installing with pre-compiled wheels."""
    print("\n🛞 Attempting installation with pre-compiled wheels...")
    
    # Try to install Playwright with specific wheel options
    commands = [
        "pip install --upgrade pip",
        "pip install --only-binary=all playwright==1.40.0",
        "pip install --only-binary=all greenlet"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Success: {cmd}")
            else:
                print(f"❌ Failed: {cmd}")
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"❌ Exception: {e}")

def main():
    """Main installation checker and helper."""
    print("🚀 Turerz Build Tools Setup")
    print("=" * 40)
    
    # Check current state
    has_build_tools = check_build_tools()
    has_compiler = check_compiler()
    
    if has_build_tools and has_compiler:
        print("\n🎉 Build environment looks good!")
        print("You should be able to install Playwright now.")
        return True
    
    if not has_build_tools:
        download_vs_buildtools()
        install_with_conda()
        
        print("\n⚡ Quick Alternative:")
        print("Try the wheel-only installation first:")
        install_with_wheels()
        
        return False
    
    print("\n❓ Build tools found but compiler not in PATH")
    print("Try opening a 'Developer Command Prompt' or 'Developer PowerShell'")
    print("from the Visual Studio installation.")
    
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Next Steps:")
        print("1. Install Visual Studio Build Tools (recommended)")
        print("2. Or try the conda approach")
        print("3. Or use the wheel-only installation")
        print("4. Restart your terminal after installation")
        print("5. Run this script again to verify")
    
    sys.exit(0 if success else 1)
