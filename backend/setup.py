"""
Setup script for Turerz backend.
Installs dependencies and configures the environment.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and print status."""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False


def main():
    """Setup the backend environment."""
    print("🚀 Turerz Backend Setup")
    print("=" * 40)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or python_version.minor < 8:
        print("❌ Python 3.8+ required")
        return False
    
    # Install requirements
    success = run_command(
        "pip install -r requirements.txt",
        "Installing Python packages"
    )
    if not success:
        return False
    
    # Install Playwright browsers
    success = run_command(
        "playwright install",
        "Installing Playwright browsers"
    )
    if not success:
        print("⚠️ Playwright install failed - you may need to install manually")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📝 Creating .env file from template")
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ .env file created - please update with your credentials")
        except Exception as e:
            print(f"❌ Could not create .env file: {e}")
    
    # Create output directories
    directories = ["logs", "exports", "debug"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your Internshala credentials")
    print("2. Run: python test_browser.py")
    print("3. If tests pass, you're ready for the next task!")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
