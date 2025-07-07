#!/usr/bin/env python3
"""
Suna Desktop Application
A self-hosting desktop app for Suna AI Agent with GUI and web interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import time
import os
import sys
import json
import shutil
import webbrowser
from pathlib import Path
import signal
import psutil
from typing import Optional, Dict, Any, List
import requests
import queue
from datetime import datetime

class SunaService:
    """Manages the Suna backend services."""
    
    def __init__(self, suna_path: str):
        self.suna_path = Path(suna_path)
        self.processes = {}
        self.is_running = False
        self.web_port = 3000
        self.api_port = 8000
        
    def check_requirements(self) -> tuple[bool, str]:
        """Check if all requirements are met to run Suna."""
        # Check if Docker is available
        try:
            subprocess.run(['docker', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "Docker is not installed or not available"
        
        # Check if docker-compose is available
        try:
            subprocess.run(['docker-compose', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "Docker Compose is not installed or not available"
        
        # Check if Suna directory exists and has necessary files
        if not self.suna_path.exists():
            return False, f"Suna directory not found: {self.suna_path}"
        
        required_files = ['docker-compose.yaml', 'backend/', 'frontend/']
        for file in required_files:
            if not (self.suna_path / file).exists():
                return False, f"Required file/directory missing: {file}"
        
        return True, "All requirements met"
    
    def setup_environment(self) -> tuple[bool, str]:
        """Set up the environment files if they don't exist."""
        try:
            # Check if backend .env exists
            backend_env = self.suna_path / 'backend' / '.env'
            if not backend_env.exists():
                # Create basic .env file
                env_content = """# Suna Backend Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_SSL=False
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672

# LLM Configuration (add your API keys)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
OPENROUTER_API_KEY=

# Database Configuration
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Optional Services
TAVILY_API_KEY=
FIRECRAWL_API_KEY=
"""
                backend_env.write_text(env_content)
            
            # Check if frontend .env.local exists
            frontend_env = self.suna_path / 'frontend' / '.env.local'
            if not frontend_env.exists():
                # Create basic frontend env
                env_content = """NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
"""
                frontend_env.write_text(env_content)
            
            return True, "Environment setup completed"
        except Exception as e:
            return False, f"Failed to setup environment: {str(e)}"
    
    def start_services(self) -> tuple[bool, str]:
        """Start all Suna services using Docker Compose."""
        if self.is_running:
            return False, "Services are already running"
        
        try:
            # Change to Suna directory
            os.chdir(self.suna_path)
            
            # Start services with docker-compose
            process = subprocess.Popen(
                ['docker-compose', 'up', '-d'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.is_running = True
                return True, "Services started successfully"
            else:
                return False, f"Failed to start services: {stderr}"
        
        except Exception as e:
            return False, f"Error starting services: {str(e)}"
    
    def stop_services(self) -> tuple[bool, str]:
        """Stop all Suna services."""
        if not self.is_running:
            return False, "Services are not running"
        
        try:
            os.chdir(self.suna_path)
            
            # Stop services
            process = subprocess.Popen(
                ['docker-compose', 'down'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.is_running = False
                return True, "Services stopped successfully"
            else:
                return False, f"Failed to stop services: {stderr}"
        
        except Exception as e:
            return False, f"Error stopping services: {str(e)}"
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of all services."""
        try:
            os.chdir(self.suna_path)
            process = subprocess.run(
                ['docker-compose', 'ps', '--format', 'json'],
                capture_output=True,
                text=True
            )
            
            if process.returncode == 0:
                services = []
                for line in process.stdout.strip().split('\n'):
                    if line:
                        services.append(json.loads(line))
                return {"status": "success", "services": services}
            else:
                return {"status": "error", "message": process.stderr}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_health(self) -> Dict[str, bool]:
        """Check health of individual services."""
        health = {
            "frontend": False,
            "backend": False,
            "redis": False,
            "rabbitmq": False
        }
        
        # Check frontend
        try:
            response = requests.get(f"http://localhost:{self.web_port}", timeout=5)
            health["frontend"] = response.status_code == 200
        except:
            pass
        
        # Check backend
        try:
            response = requests.get(f"http://localhost:{self.api_port}/api/health", timeout=5)
            health["backend"] = response.status_code == 200
        except:
            pass
        
        # Note: Redis and RabbitMQ health would need docker inspection
        # For simplicity, we'll mark them as healthy if backend is healthy
        if health["backend"]:
            health["redis"] = True
            health["rabbitmq"] = True
        
        return health

class SunaDesktopGUI:
    """Main GUI application for Suna Desktop."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Suna Desktop - AI Agent Platform")
        self.root.geometry("900x700")
        
        # Initialize service manager
        self.suna_service = None
        self.suna_path = None
        self.status_queue = queue.Queue()
        
        # GUI state
        self.is_setup = False
        
        self.setup_gui()
        self.root.after(1000, self.update_status)
    
    def setup_gui(self):
        """Set up the main GUI interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Setup tab
        self.setup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_frame, text="Setup")
        self.create_setup_tab()
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.create_dashboard_tab()
        
        # Chat tab
        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="Chat")
        self.create_chat_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.create_settings_tab()
        
        # Initially disable tabs except setup
        for i in range(1, self.notebook.index("end")):
            self.notebook.tab(i, state="disabled")
    
    def create_setup_tab(self):
        """Create the setup/installation tab."""
        setup_main = ttk.Frame(self.setup_frame, padding="20")
        setup_main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(setup_main, text="Suna Desktop Setup", 
                               font=("TkDefaultFont", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Suna path selection
        path_frame = ttk.LabelFrame(setup_main, text="Suna Installation", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(path_frame, text="Select Suna directory:").pack(anchor=tk.W)
        
        path_select_frame = ttk.Frame(path_frame)
        path_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_select_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(path_select_frame, text="Browse", 
                  command=self.browse_suna_path).pack(side=tk.RIGHT)
        
        ttk.Button(path_frame, text="Download Suna", 
                  command=self.download_suna).pack(pady=(10, 0))
        
        # Requirements check
        req_frame = ttk.LabelFrame(setup_main, text="Requirements Check", padding="10")
        req_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.req_text = scrolledtext.ScrolledText(req_frame, height=6, state=tk.DISABLED)
        self.req_text.pack(fill=tk.BOTH, expand=True)
        
        req_btn_frame = ttk.Frame(req_frame)
        req_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(req_btn_frame, text="Check Requirements", 
                  command=self.check_requirements).pack(side=tk.LEFT)
        
        ttk.Button(req_btn_frame, text="Setup Environment", 
                  command=self.setup_environment).pack(side=tk.LEFT, padx=(10, 0))
        
        # Setup button
        self.setup_btn = ttk.Button(setup_main, text="Complete Setup", 
                                   command=self.complete_setup, state=tk.DISABLED)
        self.setup_btn.pack(pady=(20, 0))
    
    def create_dashboard_tab(self):
        """Create the dashboard tab."""
        dash_main = ttk.Frame(self.dashboard_frame, padding="20")
        dash_main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(dash_main, text="Suna Dashboard", 
                               font=("TkDefaultFont", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Service controls
        control_frame = ttk.LabelFrame(dash_main, text="Service Control", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Services", 
                                   command=self.start_services)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Services", 
                                  command=self.stop_services, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.restart_btn = ttk.Button(btn_frame, text="Restart Services", 
                                     command=self.restart_services, state=tk.DISABLED)
        self.restart_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Access buttons
        access_frame = ttk.Frame(control_frame)
        access_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(access_frame, text="Open Web Interface", 
                  command=self.open_web_interface).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(access_frame, text="Open API Docs", 
                  command=self.open_api_docs).pack(side=tk.LEFT)
        
        # Service status
        status_frame = ttk.LabelFrame(dash_main, text="Service Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status indicators
        self.status_vars = {
            "frontend": tk.StringVar(value="●"),
            "backend": tk.StringVar(value="●"),
            "redis": tk.StringVar(value="●"),
            "rabbitmq": tk.StringVar(value="●")
        }
        
        for i, (service, var) in enumerate(self.status_vars.items()):
            frame = ttk.Frame(status_frame)
            frame.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
            
            status_label = ttk.Label(frame, textvariable=var, font=("TkDefaultFont", 12))
            status_label.pack(side=tk.LEFT)
            
            name_label = ttk.Label(frame, text=service.capitalize())
            name_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Logs
        logs_frame = ttk.LabelFrame(dash_main, text="Service Logs", padding="10")
        logs_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=8, state=tk.DISABLED)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
    
    def create_chat_tab(self):
        """Create the integrated chat tab."""
        from suna_chat import SunaChatInterface
        self.chat_interface = SunaChatInterface(self.chat_frame)
    
    def create_settings_tab(self):
        """Create the settings tab."""
        settings_main = ttk.Frame(self.settings_frame, padding="20")
        settings_main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(settings_main, text="Settings", 
                               font=("TkDefaultFont", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Port configuration
        port_frame = ttk.LabelFrame(settings_main, text="Port Configuration", padding="10")
        port_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(port_frame, text="Web Interface Port:").grid(row=0, column=0, sticky=tk.W)
        self.web_port_var = tk.StringVar(value="3000")
        ttk.Entry(port_frame, textvariable=self.web_port_var, width=10).grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(port_frame, text="API Port:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.api_port_var = tk.StringVar(value="8000")
        ttk.Entry(port_frame, textvariable=self.api_port_var, width=10).grid(row=1, column=1, padx=(10, 0), pady=(5, 0))
        
        # Environment configuration
        env_frame = ttk.LabelFrame(settings_main, text="Environment Variables", padding="10")
        env_frame.pack(fill=tk.BOTH, expand=True)
        
        self.env_text = scrolledtext.ScrolledText(env_frame, height=15)
        self.env_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Button(env_frame, text="Load Environment", 
                  command=self.load_environment).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(env_frame, text="Save Environment", 
                  command=self.save_environment).pack(side=tk.LEFT)
    
    def browse_suna_path(self):
        """Browse for Suna installation directory."""
        path = filedialog.askdirectory(title="Select Suna Directory")
        if path:
            self.path_var.set(path)
    
    def download_suna(self):
        """Download Suna from GitHub."""
        def download_worker():
            try:
                import git
                target_dir = filedialog.askdirectory(title="Select Download Location")
                if target_dir:
                    suna_dir = os.path.join(target_dir, "suna")
                    self.status_queue.put(("info", "Downloading Suna from GitHub..."))
                    git.Repo.clone_from("https://github.com/kortix-ai/suna.git", suna_dir)
                    self.status_queue.put(("success", f"Suna downloaded to {suna_dir}"))
                    self.path_var.set(suna_dir)
            except ImportError:
                self.status_queue.put(("error", "GitPython not installed. Please install with: pip install gitpython"))
            except Exception as e:
                self.status_queue.put(("error", f"Download failed: {str(e)}"))
        
        threading.Thread(target=download_worker, daemon=True).start()
    
    def check_requirements(self):
        """Check system requirements."""
        path = self.path_var.get().strip()
        if not path:
            self.append_to_logs("Please select Suna directory first", "error")
            return
        
        self.suna_service = SunaService(path)
        success, message = self.suna_service.check_requirements()
        
        self.append_to_logs(f"Requirements check: {message}", 
                           "success" if success else "error")
        
        if success:
            self.setup_btn.config(state=tk.NORMAL)
    
    def setup_environment(self):
        """Set up environment files."""
        if not self.suna_service:
            self.append_to_logs("Please check requirements first", "error")
            return
        
        success, message = self.suna_service.setup_environment()
        self.append_to_logs(f"Environment setup: {message}", 
                           "success" if success else "error")
    
    def complete_setup(self):
        """Complete the setup process."""
        if not self.suna_service:
            return
        
        self.is_setup = True
        self.suna_path = self.path_var.get()
        
        # Enable other tabs
        for i in range(1, self.notebook.index("end")):
            self.notebook.tab(i, state="normal")
        
        # Switch to dashboard
        self.notebook.select(1)
        
        self.append_to_logs("Setup completed successfully!", "success")
    
    def start_services(self):
        """Start Suna services."""
        if not self.suna_service:
            return
        
        def start_worker():
            self.status_queue.put(("info", "Starting Suna services..."))
            success, message = self.suna_service.start_services()
            self.status_queue.put(("success" if success else "error", message))
            
            if success:
                self.status_queue.put(("enable_stop", None))
                self.status_queue.put(("disable_start", None))
        
        threading.Thread(target=start_worker, daemon=True).start()
    
    def stop_services(self):
        """Stop Suna services."""
        if not self.suna_service:
            return
        
        def stop_worker():
            self.status_queue.put(("info", "Stopping Suna services..."))
            success, message = self.suna_service.stop_services()
            self.status_queue.put(("success" if success else "error", message))
            
            if success:
                self.status_queue.put(("enable_start", None))
                self.status_queue.put(("disable_stop", None))
        
        threading.Thread(target=stop_worker, daemon=True).start()
    
    def restart_services(self):
        """Restart Suna services."""
        def restart_worker():
            # Stop first
            if self.suna_service.is_running:
                self.status_queue.put(("info", "Stopping services..."))
                self.suna_service.stop_services()
                time.sleep(2)
            
            # Then start
            self.status_queue.put(("info", "Starting services..."))
            success, message = self.suna_service.start_services()
            self.status_queue.put(("success" if success else "error", message))
        
        threading.Thread(target=restart_worker, daemon=True).start()
    
    def open_web_interface(self):
        """Open the web interface in browser."""
        webbrowser.open(f"http://localhost:{self.suna_service.web_port}")
    
    def open_api_docs(self):
        """Open API documentation."""
        webbrowser.open(f"http://localhost:{self.suna_service.api_port}/docs")
    
    def load_environment(self):
        """Load environment variables from file."""
        if not self.suna_service:
            return
        
        env_file = self.suna_service.suna_path / 'backend' / '.env'
        if env_file.exists():
            content = env_file.read_text()
            self.env_text.delete(1.0, tk.END)
            self.env_text.insert(1.0, content)
    
    def save_environment(self):
        """Save environment variables to file."""
        if not self.suna_service:
            return
        
        env_file = self.suna_service.suna_path / 'backend' / '.env'
        content = self.env_text.get(1.0, tk.END)
        env_file.write_text(content)
        messagebox.showinfo("Success", "Environment variables saved!")
    
    def append_to_logs(self, message: str, level: str = "info"):
        """Append message to logs."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determine color based on level
        if hasattr(self, 'req_text'):
            text_widget = self.req_text
        else:
            text_widget = self.logs_text
        
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, f"[{timestamp}] {message}\n")
        text_widget.see(tk.END)
        text_widget.config(state=tk.DISABLED)
    
    def update_status(self):
        """Update service status and handle queued messages."""
        # Handle status queue
        try:
            while True:
                msg_type, content = self.status_queue.get_nowait()
                
                if msg_type in ["info", "success", "error"]:
                    self.append_to_logs(content, msg_type)
                elif msg_type == "enable_stop":
                    self.stop_btn.config(state=tk.NORMAL)
                    self.restart_btn.config(state=tk.NORMAL)
                elif msg_type == "disable_stop":
                    self.stop_btn.config(state=tk.DISABLED)
                    self.restart_btn.config(state=tk.DISABLED)
                elif msg_type == "enable_start":
                    self.start_btn.config(state=tk.NORMAL)
                elif msg_type == "disable_start":
                    self.start_btn.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        
        # Update service status indicators
        if self.suna_service and self.is_setup:
            health = self.suna_service.check_health()
            for service, is_healthy in health.items():
                if service in self.status_vars:
                    self.status_vars[service].set("🟢" if is_healthy else "🔴")
        
        # Schedule next update
        self.root.after(5000, self.update_status)

def main():
    """Main function to run the Suna Desktop application."""
    root = tk.Tk()
    app = SunaDesktopGUI(root)
    
    def on_closing():
        """Handle application closing."""
        if app.suna_service and app.suna_service.is_running:
            result = messagebox.askyesno(
                "Confirm Exit", 
                "Suna services are running. Stop them before exiting?"
            )
            if result:
                app.suna_service.stop_services()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down Suna Desktop...")

if __name__ == "__main__":
    main()