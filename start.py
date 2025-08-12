#!/usr/bin/env python3
"""
Startup script for Impuestito Discord Bot
Provides easy bot launching with configuration validation and dependency checking.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'discord',
        'impuestito',
        'dotenv',
        'aiohttp',
        'cachetools',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install missing packages with: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Copy .env.example to .env and configure your settings:")
        print("   cp .env.example .env")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required variables
    required_vars = ['DISCORD_BOT_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("💡 Add them to your .env file")
        return False
    
    print("✅ Environment configuration")
    return True

def check_bot_file():
    """Check if main bot file exists"""
    bot_file = Path('bot.py')
    
    if not bot_file.exists():
        print("❌ bot.py not found")
        print("💡 Make sure you're in the correct directory")
        return False
    
    print("✅ Bot file found")
    return True

def main():
    """Main startup function"""
    print("🤖 Impuestito Discord Bot - Startup Check")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_env_file),
        ("Bot File", check_bot_file)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    if not all_passed:
        print("\n❌ Startup checks failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n✅ All checks passed!")
    print("🚀 Starting bot...")
    print("=" * 50)
    
    try:
        # Start the bot
        subprocess.run([sys.executable, 'bot.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Bot exited with error code {e.returncode}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == '__main__':
    main()