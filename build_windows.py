#!/usr/bin/env python3
"""
Windows Build Script for Suna Desktop
Creates executable and installer package for Windows distribution.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import tempfile
import hashlib

class WindowsBuilder:
    """Build Windows executable and installer for Suna Desktop."""
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        self.installer_dir = self.project_dir / "installer"
        
        # Security: Validate paths are within project directory
        self._validate_paths()
        
    def _validate_paths(self):
        """Validate that all paths are within the project directory."""
        try:
            self.project_dir.resolve()
            if not self.project_dir.exists():
                raise ValueError("Project directory does not exist")
        except Exception as e:
            raise ValueError(f"Invalid project directory: {e}")
    
    def _safe_remove_directory(self, path):
        """Safely remove directory with validation."""
        path = Path(path).resolve()
        if not str(path).startswith(str(self.project_dir.resolve())):
            raise ValueError(f"Attempted to remove directory outside project: {path}")
        
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
    
    def check_requirements(self):
        """Check if build requirements are available."""
        print("🔍 Checking build requirements...")
        
        # Check PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__} found")
        except ImportError:
            print("❌ PyInstaller not found. Installing...")
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'pyinstaller'
                ], check=True, timeout=300)
                print("✅ PyInstaller installed")
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                print("❌ Failed to install PyInstaller automatically.")
                print("   Please install manually: python -m pip install pyinstaller")
                return False
        
        # Check Pillow for icon creation
        try:
            import PIL
            print("✅ Pillow found")
        except ImportError:
            print("❌ Pillow not found. Installing...")
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'pillow'
                ], check=True, timeout=300)
                print("✅ Pillow installed")
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                print("❌ Failed to install Pillow automatically.")
                print("   Please install manually: python -m pip install pillow")
                return False
        
        # Check if Inno Setup is available (optional)
        inno_path = Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe")
        if inno_path.exists():
            print("✅ Inno Setup found")
            return True
        else:
            print("⚠️  Inno Setup not found - installer creation will be skipped")
            print("   Download from: https://jrsoftware.org/isdl.php")
            return False
    
    def create_spec_file(self):
        """Create PyInstaller spec file with security considerations."""
        print("📝 Creating PyInstaller spec file...")
        
        # Validate required files exist
        required_files = [
            'launch_suna_desktop.py',
            'requirements.txt',
            'README.md',
            'QUICK_START.md',
            'suna_desktop.py',
            'suna_chat.py',
            'mobile_web.py',
            'setup_suna_desktop.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            raise FileNotFoundError(f"Required files missing: {missing_files}")
        
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launch_suna_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('QUICK_START.md', '.'),
        ('suna_desktop.py', '.'),
        ('suna_chat.py', '.'),
        ('mobile_web.py', '.'),
        ('setup_suna_desktop.py', '.'),
        ('templates', 'templates'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'requests',
        'flask',
        'psutil',
        'gitpython',
        'queue',
        'threading',
        'subprocess',
        'json',
        'pathlib',
        'datetime',
        'uuid',
        'tempfile',
        'zipfile',
        'webbrowser',
        'signal',
        'shutil',
        'hashlib',
        'secrets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SunaDesktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
'''
        
        spec_path = self.project_dir / "suna_desktop.spec"
        spec_path.write_text(spec_content, encoding='utf-8')
        print(f"✅ Spec file created: {spec_path}")
        return spec_path
    
    def create_icon(self):
        """Create application icon with error handling."""
        print("🎨 Creating application icon...")
        
        try:
            from PIL import Image, ImageDraw
            
            # Create 256x256 icon
            img = Image.new('RGBA', (256, 256), (79, 70, 229, 255))  # Indigo background
            draw = ImageDraw.Draw(img)
            
            # Draw robot emoji-like icon
            # Head circle
            draw.ellipse([64, 64, 192, 192], fill=(255, 255, 255, 255))
            
            # Eyes
            draw.ellipse([88, 100, 112, 124], fill=(79, 70, 229, 255))
            draw.ellipse([144, 100, 168, 124], fill=(79, 70, 229, 255))
            
            # Mouth
            draw.arc([100, 140, 156, 170], 0, 180, fill=(79, 70, 229, 255), width=4)
            
            # Antennas
            draw.line([110, 64, 110, 40], fill=(79, 70, 229, 255), width=4)
            draw.line([146, 64, 146, 40], fill=(79, 70, 229, 255), width=4)
            draw.ellipse([106, 36, 114, 44], fill=(255, 255, 255, 255))
            draw.ellipse([142, 36, 150, 44], fill=(255, 255, 255, 255))
            
            # Save as ICO
            icon_path = self.project_dir / "icon.ico"
            img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"✅ Icon created: {icon_path}")
            
        except ImportError:
            print("⚠️  PIL not available - creating placeholder icon")
            # Create a minimal placeholder
            icon_path = self.project_dir / "icon.ico"
            if not icon_path.exists():
                # Create empty file as placeholder
                icon_path.touch()
        except Exception as e:
            print(f"⚠️  Icon creation failed: {e}")
            # Create placeholder
            icon_path = self.project_dir / "icon.ico"
            icon_path.touch()
    
    def build_executable(self):
        """Build the executable using PyInstaller with security checks."""
        print("🔨 Building executable...")
        
        # Clean previous builds
        self._safe_remove_directory(self.build_dir)
        self._safe_remove_directory(self.dist_dir)
        
        # Create spec file
        spec_path = self.create_spec_file()
        
        # Create icon
        self.create_icon()
        
        # Build with PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            str(spec_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
            
            if result.returncode == 0:
                print("✅ Executable built successfully")
                exe_path = self.dist_dir / "SunaDesktop.exe"
                if exe_path.exists():
                    print(f"📦 Executable location: {exe_path}")
                    # Verify executable integrity
                    if self._verify_executable(exe_path):
                        return exe_path
                    else:
                        raise Exception("Executable verification failed")
                else:
                    raise Exception("Executable not found after build")
            else:
                raise Exception(f"Build failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Build timed out after 30 minutes")
    
    def _verify_executable(self, exe_path):
        """Verify the built executable."""
        try:
            # Check file size (should be reasonable)
            size = exe_path.stat().st_size
            if size < 1024 * 1024:  # Less than 1MB is suspicious
                print(f"⚠️  Executable size seems small: {size} bytes")
                return False
            
            # Calculate hash for integrity
            sha256_hash = hashlib.sha256()
            with open(exe_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            print(f"✅ Executable hash: {sha256_hash.hexdigest()[:16]}...")
            return True
            
        except Exception as e:
            print(f"❌ Executable verification failed: {e}")
            return False
    
    def create_installer_script(self, exe_path):
        """Create Inno Setup installer script with security considerations."""
        print("📜 Creating installer script...")
        
        self.installer_dir.mkdir(exist_ok=True)
        
        # Validate exe_path
        if not exe_path.exists():
            raise FileNotFoundError(f"Executable not found: {exe_path}")
        
        installer_script = f'''[Setup]
AppName=Suna Desktop
AppVersion=1.0.0
AppPublisher=Suna AI
AppPublisherURL=https://github.com/kortix-ai/suna
AppSupportURL=https://github.com/kortix-ai/suna/issues
AppUpdatesURL=https://github.com/kortix-ai/suna/releases
DefaultDirName={{autopf}}\\Suna Desktop
DefaultGroupName=Suna Desktop
AllowNoIcons=yes
OutputDir={self.installer_dir}
OutputBaseFilename=SunaDesktopSetup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
DisableDirPage=no
DisableProgramGroupPage=no
CreateAppDir=yes
UninstallDisplayIcon={{app}}\\SunaDesktop.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "{exe_path}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "QUICK_START.md"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\Suna Desktop"; Filename: "{{app}}\\SunaDesktop.exe"
Name: "{{group}}\\{{cm:ProgramOnTheWeb,Suna Desktop}}"; Filename: "https://github.com/kortix-ai/suna"
Name: "{{group}}\\{{cm:UninstallProgram,Suna Desktop}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\Suna Desktop"; Filename: "{{app}}\\SunaDesktop.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\Suna Desktop"; Filename: "{{app}}\\SunaDesktop.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\SunaDesktop.exe"; Description: "{{cm:LaunchProgram,Suna Desktop}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  if Version.Major < 10 then begin
    MsgBox('This application requires Windows 10 or later.', mbError, MB_OK);
    Result := False;
  end else
    Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ErrorCode: Integer;
begin
  if CurStep = ssPostInstall then begin
    // Check if Docker is installed
    if not FileExists('C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe') then begin
      if MsgBox('Docker Desktop is required for Suna to function. Would you like to download it now?', mbConfirmation, MB_YESNO) = IDYES then begin
        ShellExec('open', 'https://docs.docker.com/get-docker/', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
      end;
    end;
  end;
end;
'''
        
        script_path = self.installer_dir / "installer.iss"
        script_path.write_text(installer_script, encoding='utf-8')
        print(f"✅ Installer script created: {script_path}")
        return script_path
    
    def build_installer(self, exe_path):
        """Build the installer using Inno Setup with timeout."""
        print("📦 Building installer...")
        
        script_path = self.create_installer_script(exe_path)
        
        # Check if Inno Setup is available
        inno_path = Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe")
        if not inno_path.exists():
            print("❌ Inno Setup not found - skipping installer creation")
            return None
        
        # Build installer
        cmd = [str(inno_path), str(script_path)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
            
            if result.returncode == 0:
                installer_path = self.installer_dir / "SunaDesktopSetup.exe"
                if installer_path.exists():
                    print(f"✅ Installer created: {installer_path}")
                    return installer_path
                else:
                    raise Exception("Installer not found after build")
            else:
                raise Exception(f"Installer build failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Installer build timed out")
    
    def create_portable_package(self, exe_path):
        """Create a portable package with security validation."""
        print("📁 Creating portable package...")
        
        portable_dir = self.project_dir / "SunaDesktop_Portable"
        self._safe_remove_directory(portable_dir)
        portable_dir.mkdir()
        
        # Copy executable with verification
        if not exe_path.exists():
            raise FileNotFoundError(f"Executable not found: {exe_path}")
        
        shutil.copy2(exe_path, portable_dir / "SunaDesktop.exe")
        
        # Copy documentation
        docs = ["README.md", "QUICK_START.md", "requirements.txt"]
        for doc in docs:
            doc_path = self.project_dir / doc
            if doc_path.exists():
                shutil.copy2(doc_path, portable_dir / doc)
        
        # Create secure run script
        run_script = portable_dir / "Run_Suna_Desktop.bat"
        run_script.write_text('''@echo off
echo Starting Suna Desktop...
echo.
echo Make sure Docker Desktop is running before using Suna!
echo.
echo Press Ctrl+C to cancel if needed...
timeout /t 3 /nobreak >nul
SunaDesktop.exe
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    echo Check the logs above for details.
)
pause
''', encoding='utf-8')
        
        # Create ZIP package
        zip_path = self.project_dir / "SunaDesktop_Portable.zip"
        if zip_path.exists():
            zip_path.unlink()
        
        shutil.make_archive(str(zip_path.with_suffix('')), 'zip', portable_dir)
        
        print(f"✅ Portable package created: {zip_path}")
        return zip_path
    
    def build_all(self):
        """Build all Windows packages with comprehensive error handling."""
        print("🚀 Starting Windows build process...")
        print("=" * 50)
        
        try:
            # Check requirements
            has_inno = self.check_requirements()
            
            # Build executable
            exe_path = self.build_executable()
            
            # Create portable package
            portable_path = self.create_portable_package(exe_path)
            
            # Build installer if Inno Setup is available
            installer_path = None
            if has_inno:
                try:
                    installer_path = self.build_installer(exe_path)
                except Exception as e:
                    print(f"⚠️  Installer creation failed: {e}")
            
            # Summary
            print("\n" + "=" * 50)
            print("🎉 Build completed successfully!")
            print("=" * 50)
            print(f"\n📦 Executable: {exe_path}")
            print(f"📁 Portable Package: {portable_path}")
            if installer_path:
                print(f"💿 Installer: {installer_path}")
            
            print("\n📋 Distribution Options:")
            print("1. Executable - Single file, requires Python runtime")
            print("2. Portable Package - ZIP with docs, no installation needed")
            if installer_path:
                print("3. Installer - Full Windows installer with uninstall support")
            
            print("\n⚠️  Important Notes:")
            print("- Users need Docker Desktop installed")
            print("- Windows 10 or later required")
            print("- Antivirus may flag the executable (false positive)")
            print("- Test all packages before distribution")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Build failed: {e}")
            return False

def main():
    """Main build function with argument validation."""
    try:
        builder = WindowsBuilder()
        success = builder.build_all()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️  Build cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())