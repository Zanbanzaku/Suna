#!/usr/bin/env python3
"""
Complete Build Script for Suna Desktop
Builds Windows installer and Android APK in one go.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import argparse

class CompleteBuildSystem:
    """Complete build system for all Suna Desktop packages."""
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.build_dir = self.project_dir / "build_output"
        
    def setup_build_environment(self):
        """Set up the build environment."""
        print("🔧 Setting up build environment...")
        
        # Create build output directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir()
        
        # Check Python dependencies
        required_packages = [
            'pyinstaller',
            'pillow',  # For icon creation
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                print(f"Installing {package}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        
        print("✅ Build environment ready")
    
    def build_windows_packages(self):
        """Build Windows executable and installer."""
        print("\n🪟 Building Windows packages...")
        
        try:
            from build_windows import WindowsBuilder
            builder = WindowsBuilder()
            success = builder.build_all()
            
            if success:
                # Copy Windows builds to output directory
                windows_dir = self.build_dir / "windows"
                windows_dir.mkdir()
                
                # Copy executable
                exe_path = self.project_dir / "dist" / "SunaDesktop.exe"
                if exe_path.exists():
                    shutil.copy2(exe_path, windows_dir / "SunaDesktop.exe")
                
                # Copy portable package
                portable_path = self.project_dir / "SunaDesktop_Portable.zip"
                if portable_path.exists():
                    shutil.copy2(portable_path, windows_dir / "SunaDesktop_Portable.zip")
                
                # Copy installer if it exists
                installer_path = self.project_dir / "installer" / "SunaDesktopSetup.exe"
                if installer_path.exists():
                    shutil.copy2(installer_path, windows_dir / "SunaDesktopSetup.exe")
                
                print("✅ Windows packages built successfully")
                return True
            else:
                print("❌ Windows build failed")
                return False
                
        except Exception as e:
            print(f"❌ Windows build error: {e}")
            return False
    
    def build_android_app(self):
        """Build Android APK."""
        print("\n📱 Building Android app...")
        
        android_dir = self.project_dir / "android_app"
        if not android_dir.exists():
            print("❌ Android app directory not found")
            return False
        
        try:
            # Change to Android app directory
            original_dir = os.getcwd()
            os.chdir(android_dir)
            
            # Check if Node.js is available
            try:
                subprocess.run(['node', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org")
                return False
            
            # Install dependencies
            print("📦 Installing Node.js dependencies...")
            subprocess.run(['npm', 'install'], check=True)
            
            # Check if Android SDK is available
            android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
            if not android_home:
                print("⚠️  ANDROID_HOME not set. Please install Android Studio and set ANDROID_HOME")
                print("   Skipping Android build...")
                return False
            
            # Build debug APK
            print("🔨 Building Android APK...")
            subprocess.run(['npm', 'run', 'build:android-debug'], check=True)
            
            # Copy APK to output directory
            android_output_dir = self.build_dir / "android"
            android_output_dir.mkdir()
            
            apk_path = android_dir / "android" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
            if apk_path.exists():
                shutil.copy2(apk_path, android_output_dir / "SunaDesktop-debug.apk")
                print("✅ Android APK built successfully")
                return True
            else:
                print("❌ APK not found after build")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Android build failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Android build error: {e}")
            return False
        finally:
            os.chdir(original_dir)
    
    def create_release_package(self):
        """Create a complete release package."""
        print("\n📦 Creating release package...")
        
        release_dir = self.build_dir / "release"
        release_dir.mkdir()
        
        # Copy documentation
        docs = ["README.md", "QUICK_START.md", "requirements.txt"]
        for doc in docs:
            doc_path = self.project_dir / doc
            if doc_path.exists():
                shutil.copy2(doc_path, release_dir / doc)
        
        # Create release info
        release_info = {
            "name": "Suna Desktop",
            "version": "1.0.0",
            "description": "Self-hosting AI Agent Platform",
            "build_date": str(Path(__file__).stat().st_mtime),
            "components": {
                "windows_executable": "windows/SunaDesktop.exe",
                "windows_portable": "windows/SunaDesktop_Portable.zip",
                "windows_installer": "windows/SunaDesktopSetup.exe",
                "android_apk": "android/SunaDesktop-debug.apk"
            },
            "requirements": {
                "windows": "Windows 10+, Docker Desktop",
                "android": "Android 7.0+ (API 24+)"
            },
            "installation": {
                "windows": "Run SunaDesktopSetup.exe or extract portable ZIP",
                "android": "Install SunaDesktop-debug.apk (enable unknown sources)"
            }
        }
        
        with open(release_dir / "release_info.json", 'w') as f:
            json.dump(release_info, f, indent=2)
        
        # Create installation guide
        install_guide = """# Suna Desktop Installation Guide

## Windows Installation

### Option 1: Installer (Recommended)
1. Download `SunaDesktopSetup.exe`
2. Run the installer as administrator
3. Follow the setup wizard
4. Launch from Start Menu or Desktop shortcut

### Option 2: Portable
1. Download `SunaDesktop_Portable.zip`
2. Extract to any folder
3. Run `SunaDesktop.exe`

### Requirements
- Windows 10 or later
- Docker Desktop installed and running
- 4GB RAM minimum, 8GB recommended

## Android Installation

1. Download `SunaDesktop-debug.apk`
2. Enable "Install from unknown sources" in Android settings
3. Install the APK file
4. Configure your computer's IP address in Settings

### Requirements
- Android 7.0+ (API level 24+)
- WiFi connection to same network as computer

## First Time Setup

1. **Install Docker Desktop** on your computer
2. **Start Suna Desktop** application
3. **Complete setup wizard** (API keys, database)
4. **Start services** from Dashboard
5. **Connect mobile app** using computer's IP address

## Troubleshooting

- **Windows**: Check Docker is running, ports 3000/5000/8000 available
- **Android**: Verify IP address, check firewall settings
- **Connection**: Ensure both devices on same WiFi network

For detailed documentation, see README.md
"""
        
        with open(release_dir / "INSTALLATION.md", 'w') as f:
            f.write(install_guide)
        
        print("✅ Release package created")
    
    def build_all(self, skip_windows=False, skip_android=False):
        """Build all packages."""
        print("🚀 Starting complete build process...")
        print("=" * 60)
        
        success_count = 0
        total_builds = 2
        
        # Setup environment
        self.setup_build_environment()
        
        # Build Windows packages
        if not skip_windows:
            if self.build_windows_packages():
                success_count += 1
        else:
            print("\n⏭️  Skipping Windows build")
            total_builds -= 1
        
        # Build Android app
        if not skip_android:
            if self.build_android_app():
                success_count += 1
        else:
            print("\n⏭️  Skipping Android build")
            total_builds -= 1
        
        # Create release package
        self.create_release_package()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 Build Process Complete!")
        print("=" * 60)
        print(f"\n📊 Results: {success_count}/{total_builds} builds successful")
        
        if success_count > 0:
            print(f"\n📁 Output directory: {self.build_dir}")
            print("\n📦 Available packages:")
            
            windows_dir = self.build_dir / "windows"
            if windows_dir.exists():
                for file in windows_dir.iterdir():
                    print(f"   🪟 {file.name}")
            
            android_dir = self.build_dir / "android"
            if android_dir.exists():
                for file in android_dir.iterdir():
                    print(f"   📱 {file.name}")
            
            print(f"\n📋 Documentation: {self.build_dir / 'release'}")
        
        print("\n⚠️  Important Notes:")
        print("- Test all packages before distribution")
        print("- Windows packages may trigger antivirus warnings")
        print("- Android APK requires 'Unknown sources' enabled")
        print("- Users need Docker Desktop for Windows version")
        
        return success_count == total_builds

def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build all Suna Desktop packages")
    parser.add_argument('--skip-windows', action='store_true', help="Skip Windows build")
    parser.add_argument('--skip-android', action='store_true', help="Skip Android build")
    
    args = parser.parse_args()
    
    builder = CompleteBuildSystem()
    success = builder.build_all(
        skip_windows=args.skip_windows,
        skip_android=args.skip_android
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())