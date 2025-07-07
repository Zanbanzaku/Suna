#!/usr/bin/env python3
"""
Suna Desktop Setup Script
Automated installation and configuration for Suna Desktop Application.
"""

import os
import sys
import subprocess
import shutil
import json
import argparse
from pathlib import Path
import requests
import zipfile
import tempfile

class SunaDesktopSetup:
    """Setup and installation manager for Suna Desktop."""
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.suna_dir = self.current_dir / "suna"
        self.setup_complete = False
        
    def check_python_version(self):
        """Check if Python version is compatible."""
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        print(f"✅ Python {sys.version.split()[0]} detected")
        return True
    
    def check_system_requirements(self):
        """Check system requirements."""
        print("\n🔍 Checking system requirements...")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker detected: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker is not installed or not available")
            print("   Please install Docker from: https://docs.docker.com/get-docker/")
            return False
        
        # Check Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker Compose detected: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker Compose is not installed or not available")
            print("   Please install Docker Compose from: https://docs.docker.com/compose/install/")
            return False
        
        # Check Git
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Git detected: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Git is not installed - using alternative download method")
        
        return True
    
    def install_python_dependencies(self):
        """Install Python dependencies."""
        print("\n📦 Installing Python dependencies...")
        
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                          check=True)
            print("✅ Python dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
    
    def download_suna(self, method='git'):
        """Download Suna repository."""
        print(f"\n📥 Downloading Suna using {method}...")
        
        if self.suna_dir.exists():
            print(f"⚠️  Suna directory already exists at {self.suna_dir}")
            response = input("Do you want to remove it and re-download? (y/N): ")
            if response.lower() == 'y':
                shutil.rmtree(self.suna_dir)
            else:
                print("✅ Using existing Suna directory")
                return True
        
        try:
            if method == 'git':
                subprocess.run([
                    'git', 'clone', 
                    'https://github.com/kortix-ai/suna.git', 
                    str(self.suna_dir)
                ], check=True)
            else:
                # Download as ZIP
                url = "https://github.com/kortix-ai/suna/archive/refs/heads/master.zip"
                print("📥 Downloading Suna as ZIP file...")
                
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    zip_path = tmp_file.name
                
                # Extract ZIP
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.current_dir)
                
                # Rename extracted directory
                extracted_dir = self.current_dir / "suna-master"
                if extracted_dir.exists():
                    extracted_dir.rename(self.suna_dir)
                
                os.unlink(zip_path)
            
            print("✅ Suna downloaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download Suna: {e}")
            return False
    
    def setup_suna_environment(self):
        """Set up Suna environment files."""
        print("\n⚙️  Setting up Suna environment...")
        
        # Backend environment
        backend_env_path = self.suna_dir / 'backend' / '.env'
        if not backend_env_path.exists():
            env_content = """# Suna Backend Configuration
# Generated by Suna Desktop Setup

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_SSL=False

# RabbitMQ Configuration
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672

# LLM Configuration
# Add your API keys here:
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
OPENROUTER_API_KEY=

# Database Configuration
# For local setup, you can use Supabase cloud or local instance
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Search and Web Scraping (Optional)
TAVILY_API_KEY=
FIRECRAWL_API_KEY=

# Background Jobs
QSTASH_URL=
QSTASH_TOKEN=

# Daytona Configuration (for agent execution)
DAYTONA_SERVER_URL=
DAYTONA_API_KEY=
"""
            backend_env_path.write_text(env_content)
            print(f"✅ Created backend environment file: {backend_env_path}")
        else:
            print(f"✅ Backend environment file already exists: {backend_env_path}")
        
        # Frontend environment
        frontend_env_path = self.suna_dir / 'frontend' / '.env.local'
        if not frontend_env_path.exists():
            env_content = """# Suna Frontend Configuration
# Generated by Suna Desktop Setup

NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
"""
            frontend_env_path.write_text(env_content)
            print(f"✅ Created frontend environment file: {frontend_env_path}")
        else:
            print(f"✅ Frontend environment file already exists: {frontend_env_path}")
        
        return True
    
    def create_desktop_config(self):
        """Create configuration for the desktop application."""
        print("\n🖥️  Creating desktop application configuration...")
        
        config = {
            "suna_path": str(self.suna_dir),
            "web_port": 3000,
            "api_port": 8000,
            "mobile_port": 5000,
            "auto_start_services": False,
            "auto_start_mobile_web": True,
            "setup_completed": True,
            "setup_date": str(Path(__file__).stat().st_mtime)
        }
        
        config_path = self.current_dir / "suna_desktop_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Desktop configuration saved: {config_path}")
        return True
    
    def create_launcher_scripts(self):
        """Create launcher scripts for different platforms."""
        print("\n🚀 Creating launcher scripts...")
        
        # Python launcher script
        launcher_content = f"""#!/usr/bin/env python3
\"\"\"
Suna Desktop Launcher
Quick launcher for the Suna Desktop application.
\"\"\"

import os
import sys
import subprocess
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    try:
        from suna_desktop import main as suna_main
        suna_main()
    except ImportError as e:
        print(f"Error importing Suna Desktop: {{e}}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\\nSuna Desktop application closed.")
    except Exception as e:
        print(f"Error running Suna Desktop: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
        
        launcher_path = self.current_dir / "run_suna_desktop.py"
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        print(f"✅ Created Python launcher: {launcher_path}")
        
        # Create batch file for Windows
        if sys.platform == "win32":
            batch_content = f"""@echo off
echo Starting Suna Desktop...
python "{launcher_path}"
pause
"""
            batch_path = self.current_dir / "run_suna_desktop.bat"
            batch_path.write_text(batch_content)
            print(f"✅ Created Windows batch file: {batch_path}")
        
        # Create shell script for Unix-like systems
        else:
            shell_content = f"""#!/bin/bash
echo "Starting Suna Desktop..."
python3 "{launcher_path}"
"""
            shell_path = self.current_dir / "run_suna_desktop.sh"
            shell_path.write_text(shell_content)
            shell_path.chmod(0o755)
            print(f"✅ Created shell script: {shell_path}")
        
        return True
    
    def print_next_steps(self):
        """Print next steps for the user."""
        print("\n" + "="*60)
        print("🎉 Suna Desktop Setup Complete!")
        print("="*60)
        
        print("\n📋 Next Steps:")
        print("\n1. Configure API Keys:")
        print(f"   Edit: {self.suna_dir}/backend/.env")
        print("   Add your LLM API keys (Anthropic, OpenAI, etc.)")
        
        print("\n2. Set up Database:")
        print("   • Create a Supabase project at https://supabase.com")
        print("   • Add the Supabase URL and keys to the .env file")
        print("   • Or use the built-in setup wizard in the desktop app")
        
        print("\n3. Start Suna Desktop:")
        if sys.platform == "win32":
            print("   Double-click: run_suna_desktop.bat")
        else:
            print("   Run: ./run_suna_desktop.sh")
        print("   Or: python run_suna_desktop.py")
        
        print("\n4. Access Suna:")
        print("   • Desktop GUI: Use the application interface")
        print("   • Web Interface: http://localhost:3000 (after starting services)")
        print("   • Mobile Interface: http://localhost:5000")
        print("   • API Documentation: http://localhost:8000/docs")
        
        print("\n📱 Mobile Access:")
        print("   The mobile web interface allows you to access Suna")
        print("   from smartphones, tablets, or other devices on your network.")
        print(f"   Use your computer's IP address: http://[YOUR_IP]:5000")
        
        print("\n🔧 Troubleshooting:")
        print("   • Check Docker is running before starting services")
        print("   • Ensure ports 3000, 5000, and 8000 are available")
        print("   • Check the Setup tab in the desktop app for requirements")
        
        print("\n📚 Documentation:")
        print("   • Suna Repository: https://github.com/kortix-ai/suna")
        print("   • Self-hosting Guide: https://github.com/kortix-ai/suna/blob/master/docs/SELF-HOSTING.md")
        
        print("\n" + "="*60)
    
    def run_setup(self, download_method='git'):
        """Run the complete setup process."""
        print("🚀 Starting Suna Desktop Setup...")
        print("="*50)
        
        steps = [
            ("Checking system requirements", self.check_system_requirements),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Downloading Suna", lambda: self.download_suna(download_method)),
            ("Setting up Suna environment", self.setup_suna_environment),
            ("Creating desktop configuration", self.create_desktop_config),
            ("Creating launcher scripts", self.create_launcher_scripts),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Setup failed at: {step_name}")
                return False
        
        self.setup_complete = True
        self.print_next_steps()
        return True

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Suna Desktop Setup")
    parser.add_argument('--download-method', choices=['git', 'zip'], default='git',
                       help="Method to download Suna (default: git)")
    parser.add_argument('--skip-deps', action='store_true',
                       help="Skip Python dependency installation")
    
    args = parser.parse_args()
    
    setup = SunaDesktopSetup()
    
    print("Welcome to Suna Desktop Setup!")
    print("This will install and configure Suna AI Agent for desktop use.")
    print("Press Ctrl+C at any time to cancel.\n")
    
    try:
        success = setup.run_setup(args.download_method)
        if success:
            print("\n✅ Setup completed successfully!")
            return 0
        else:
            print("\n❌ Setup failed!")
            return 1
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())