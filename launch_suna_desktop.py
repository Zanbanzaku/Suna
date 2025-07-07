#!/usr/bin/env python3
"""
Suna Desktop Quick Launcher
Simple script to launch Suna Desktop with automatic setup if needed.
"""

import os
import sys
import json
from pathlib import Path

def check_setup():
    """Check if Suna Desktop has been set up."""
    config_file = Path("suna_desktop_config.json")
    return config_file.exists()

def run_setup():
    """Run the setup process."""
    print("🚀 Suna Desktop is not set up yet. Running setup...")
    try:
        from setup_suna_desktop import SunaDesktopSetup
        setup = SunaDesktopSetup()
        return setup.run_setup()
    except ImportError:
        print("❌ Setup script not found. Please ensure setup_suna_desktop.py is in the current directory.")
        return False
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def launch_desktop():
    """Launch the Suna Desktop application."""
    try:
        from suna_desktop import main
        main()
    except ImportError as e:
        print(f"❌ Failed to import Suna Desktop: {e}")
        print("Please ensure all required files are present and dependencies are installed:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Failed to launch Suna Desktop: {e}")
        return False
    return True

def main():
    """Main launcher function."""
    print("🤖 Suna Desktop Launcher")
    print("=" * 30)
    
    # Check if setup is needed
    if not check_setup():
        print("\n📋 First-time setup required...")
        if not run_setup():
            print("\n❌ Setup failed. Please check the error messages above.")
            input("Press Enter to exit...")
            return 1
        
        print("\n✅ Setup completed! Launching Suna Desktop...")
    
    # Launch the desktop application
    print("\n🚀 Starting Suna Desktop...")
    try:
        if launch_desktop():
            print("\n👋 Suna Desktop closed.")
        else:
            print("\n❌ Failed to launch Suna Desktop.")
            return 1
    except KeyboardInterrupt:
        print("\n\n⏹️  Suna Desktop interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())