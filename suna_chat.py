#!/usr/bin/env python3
"""
Suna Chat Interface
Integrated chat component for the Suna Desktop application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
import json
import threading
import time
import os
from datetime import datetime
import uuid
from typing import Optional, Dict, Any, List
import queue

class SunaAPI:
    """API client for communicating with Suna backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Suna Desktop/1.0"
        })
    
    def health_check(self) -> bool:
        """Check if Suna API is accessible."""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def initiate_agent(self, prompt: str, files: List[str] = None) -> Dict[str, Any]:
        """Initiate a new agent conversation."""
        try:
            data = {
                'prompt': prompt,
                'model_name': 'claude-3-5-sonnet-20241022',
                'enable_thinking': 'false',
                'reasoning_effort': 'low',
                'stream': 'true',
                'enable_context_manager': 'false'
            }
            
            files_data = []
            if files:
                for file_path in files:
                    if os.path.exists(file_path):
                        files_data.append(('files', (os.path.basename(file_path), open(file_path, 'rb'))))
            
            response = self.session.post(
                f"{self.base_url}/api/agent/initiate",
                data=data,
                files=files_data if files_data else None,
                timeout=30
            )
            
            # Close file handles
            for _, (_, file_handle) in files_data:
                file_handle.close()
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to initiate agent: {e}")
    
    def stream_agent_responses(self, agent_run_id: str, callback_func):
        """Stream agent responses in real-time."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/agent-run/{agent_run_id}/stream",
                stream=True,
                timeout=300
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            callback_func(data)
                        except json.JSONDecodeError:
                            callback_func({"type": "raw", "content": line.decode('utf-8')})
            else:
                raise Exception(f"Stream Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            callback_func({"type": "error", "content": f"Streaming failed: {e}"})
    
    def stop_agent(self, agent_run_id: str) -> bool:
        """Stop a running agent."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/agent-run/{agent_run_id}/stop",
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

class SunaChatInterface:
    """Integrated chat interface for Suna Desktop."""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.api = SunaAPI()
        
        # Chat state
        self.current_thread_id = None
        self.current_agent_run_id = None
        self.is_streaming = False
        self.attached_files = []
        
        # Threading
        self.response_queue = queue.Queue()
        
        self.setup_interface()
        self.check_response_queue()
    
    def setup_interface(self):
        """Set up the chat interface."""
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Connection status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.connection_label = ttk.Label(status_frame, text="Checking connection...", 
                                         foreground="orange")
        self.connection_label.pack(side=tk.LEFT)
        
        ttk.Button(status_frame, text="Reconnect", 
                  command=self.check_connection).pack(side=tk.RIGHT)
        
        # File attachments
        file_frame = ttk.LabelFrame(main_frame, text="File Attachments", padding="5")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_btn_frame = ttk.Frame(file_frame)
        file_btn_frame.pack(fill=tk.X)
        
        ttk.Button(file_btn_frame, text="Add Files", 
                  command=self.add_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(file_btn_frame, text="Clear Files", 
                  command=self.clear_files).pack(side=tk.LEFT)
        
        self.files_listbox = tk.Listbox(file_frame, height=3)
        self.files_listbox.pack(fill=tk.X, pady=(5, 0))
        
        # Chat display
        chat_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="5")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED, 
            height=20,
            font=("Consolas", 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for styling
        self.chat_display.tag_configure("user", foreground="#2563eb", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground="#059669", font=("Consolas", 10))
        self.chat_display.tag_configure("system", foreground="#6b7280", font=("Consolas", 9, "italic"))
        self.chat_display.tag_configure("error", foreground="#dc2626", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("timestamp", foreground="#9ca3af", font=("Consolas", 8))
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        # Message input
        input_container = ttk.Frame(input_frame)
        input_container.pack(fill=tk.BOTH, expand=True)
        
        self.message_entry = scrolledtext.ScrolledText(
            input_container, 
            wrap=tk.WORD, 
            height=4,
            font=("Consolas", 10)
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Control buttons
        btn_frame = ttk.Frame(input_container)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.send_btn = ttk.Button(btn_frame, text="Send", 
                                  command=self.send_message, state=tk.DISABLED)
        self.send_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", 
                                  command=self.stop_agent, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.new_chat_btn = ttk.Button(btn_frame, text="New Chat", 
                                      command=self.new_chat, state=tk.DISABLED)
        self.new_chat_btn.pack(fill=tk.X)
        
        # Keyboard bindings
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
        self.message_entry.bind('<Shift-Return>', lambda e: None)  # Allow Shift+Enter for new line
        
        # Initial connection check
        self.check_connection()
    
    def check_connection(self):
        """Check connection to Suna API."""
        def check_worker():
            if self.api.health_check():
                self.response_queue.put(("connection", "success"))
            else:
                self.response_queue.put(("connection", "failed"))
        
        threading.Thread(target=check_worker, daemon=True).start()
    
    def add_files(self):
        """Add files to attach to the next message."""
        files = filedialog.askopenfilenames(
            title="Select files to attach",
            filetypes=[
                ("All files", "*.*"),
                ("Text files", "*.txt *.md *.csv"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Documents", "*.pdf *.doc *.docx"),
                ("Code files", "*.py *.js *.html *.css *.json *.xml *.yaml *.yml")
            ]
        )
        
        for file_path in files:
            if file_path not in self.attached_files:
                self.attached_files.append(file_path)
                self.files_listbox.insert(tk.END, os.path.basename(file_path))
    
    def clear_files(self):
        """Clear all attached files."""
        self.attached_files.clear()
        self.files_listbox.delete(0, tk.END)
    
    def new_chat(self):
        """Start a new chat conversation."""
        self.current_thread_id = None
        self.current_agent_run_id = None
        self.is_streaming = False
        
        # Clear chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Clear files
        self.clear_files()
        
        self.append_to_chat("🔄 New conversation started. Send a message to begin!", "system")
        self.update_button_states()
    
    def send_message(self):
        """Send a message to Suna."""
        message = self.message_entry.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message")
            return
        
        # Display user message
        self.append_to_chat(f"👤 You: {message}", "user")
        
        # Clear input
        self.message_entry.delete(1.0, tk.END)
        
        # Disable send button
        self.send_btn.config(state=tk.DISABLED)
        
        # Start processing in background
        threading.Thread(target=self._send_message_worker, args=(message,), daemon=True).start()
    
    def _send_message_worker(self, message: str):
        """Background worker for sending messages."""
        try:
            if not self.current_thread_id:
                # First message - initiate agent
                self.response_queue.put(("system", "🚀 Initiating new conversation..."))
                
                result = self.api.initiate_agent(message, self.attached_files)
                self.current_thread_id = result.get("thread_id")
                self.current_agent_run_id = result.get("agent_run_id")
                
                self.response_queue.put(("system", f"✅ Conversation started (ID: {self.current_thread_id[:8]}...)"))
                self.response_queue.put(("clear_files", None))
            
            # Start streaming responses
            if self.current_agent_run_id:
                self.is_streaming = True
                self.response_queue.put(("enable_stop", None))
                self.response_queue.put(("stream_start", None))
                
                self.api.stream_agent_responses(self.current_agent_run_id, self._handle_stream_response)
        
        except Exception as e:
            self.response_queue.put(("error", f"❌ Error: {str(e)}"))
        finally:
            self.is_streaming = False
            self.response_queue.put(("enable_send", None))
            self.response_queue.put(("disable_stop", None))
    
    def _handle_stream_response(self, data: Dict[str, Any]):
        """Handle streaming response data."""
        self.response_queue.put(("stream_data", data))
    
    def stop_agent(self):
        """Stop the currently running agent."""
        if self.current_agent_run_id:
            threading.Thread(target=self._stop_agent_worker, daemon=True).start()
    
    def _stop_agent_worker(self):
        """Background worker for stopping agent."""
        try:
            if self.api.stop_agent(self.current_agent_run_id):
                self.response_queue.put(("system", "⏹️ Agent stopped successfully"))
            else:
                self.response_queue.put(("error", "❌ Failed to stop agent"))
        except Exception as e:
            self.response_queue.put(("error", f"❌ Error stopping agent: {str(e)}"))
        finally:
            self.is_streaming = False
            self.response_queue.put(("enable_send", None))
            self.response_queue.put(("disable_stop", None))
    
    def check_response_queue(self):
        """Check for responses and update UI."""
        try:
            while True:
                msg_type, data = self.response_queue.get_nowait()
                self._process_response(msg_type, data)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.parent.after(100, self.check_response_queue)
    
    def _process_response(self, msg_type: str, data: Any):
        """Process different types of responses."""
        if msg_type == "connection":
            if data == "success":
                self.connection_label.config(text="🟢 Connected to Suna", foreground="green")
                self.send_btn.config(state=tk.NORMAL)
                self.new_chat_btn.config(state=tk.NORMAL)
            else:
                self.connection_label.config(text="🔴 Not connected", foreground="red")
                self.send_btn.config(state=tk.DISABLED)
                self.new_chat_btn.config(state=tk.DISABLED)
        
        elif msg_type == "system":
            self.append_to_chat(f"🔧 System: {data}", "system")
        
        elif msg_type == "error":
            self.append_to_chat(f"❌ {data}", "error")
        
        elif msg_type == "clear_files":
            self.clear_files()
        
        elif msg_type == "enable_send":
            self.send_btn.config(state=tk.NORMAL)
        
        elif msg_type == "enable_stop":
            self.stop_btn.config(state=tk.NORMAL)
        
        elif msg_type == "disable_stop":
            self.stop_btn.config(state=tk.DISABLED)
        
        elif msg_type == "stream_start":
            self.append_to_chat("🤖 Suna: ", "assistant", newline=False)
        
        elif msg_type == "stream_data":
            self._handle_stream_data(data)
    
    def _handle_stream_data(self, data: Dict[str, Any]):
        """Handle individual stream data chunks."""
        data_type = data.get("type", "")
        
        if data_type == "delta":
            # Handle streaming text chunks
            delta_content = data.get("delta", {}).get("content", "")
            if delta_content:
                self.append_to_chat(delta_content, "assistant", newline=False)
        
        elif data_type == "message":
            # Handle complete messages
            content = data.get("content", "")
            role = data.get("role", "assistant")
            if content and role == "assistant":
                self.append_to_chat(f"🤖 Suna: {content}", "assistant")
        
        elif data_type == "tool_use":
            # Handle tool usage
            tool_name = data.get("name", "unknown")
            self.append_to_chat(f"🔧 Using tool: {tool_name}", "system")
        
        elif data_type == "tool_result":
            # Handle tool results
            self.append_to_chat("✅ Tool completed", "system")
        
        elif data_type == "error":
            content = data.get("content", "Unknown error")
            self.append_to_chat(f"❌ Error: {content}", "error")
        
        elif data_type == "done":
            self.append_to_chat("\n✅ Response complete", "system")
            self.is_streaming = False
            self.response_queue.put(("enable_send", None))
            self.response_queue.put(("disable_stop", None))
    
    def append_to_chat(self, text: str, tag: str = "", newline: bool = True):
        """Append text to the chat display."""
        self.chat_display.config(state=tk.NORMAL)
        
        if newline and self.chat_display.get(1.0, tk.END).strip():
            self.chat_display.insert(tk.END, "\n")
        
        # Add timestamp for new messages
        if newline and tag in ["user", "assistant", "system", "error"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        self.chat_display.insert(tk.END, text, tag)
        
        if newline:
            self.chat_display.insert(tk.END, "\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def update_button_states(self):
        """Update button states based on current status."""
        if self.is_streaming:
            self.send_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.send_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)