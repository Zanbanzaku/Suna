#!/usr/bin/env python3
"""
Suna AI Agent Desktop Client
A GUI application to connect to and interact with the Suna AI agent platform.
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
import tempfile

class SunaClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set headers
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Suna Desktop Client/1.0"
        })
    
    def health_check(self) -> bool:
        """Check if the Suna API is accessible."""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def initiate_agent(self, prompt: str, files: List[str] = None) -> Dict[str, Any]:
        """Initiate a new agent conversation."""
        try:
            # Prepare form data
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
            
            # Note: For file uploads, we need to use multipart/form-data
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
    
    def start_agent(self, thread_id: str) -> Dict[str, Any]:
        """Start the agent for a specific thread."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/thread/{thread_id}/agent/start",
                json={
                    "model_name": "claude-3-5-sonnet-20241022",
                    "enable_thinking": False,
                    "reasoning_effort": "low",
                    "stream": True,
                    "enable_context_manager": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to start agent: {e}")
    
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
                            # Parse JSON response
                            data = json.loads(line.decode('utf-8'))
                            callback_func(data)
                        except json.JSONDecodeError:
                            # Handle non-JSON lines
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
        except Exception as e:
            print(f"Failed to stop agent: {e}")
            return False

class SunaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Suna AI Agent Client")
        self.root.geometry("1000x700")
        
        # Client instance
        self.client = None
        self.current_thread_id = None
        self.current_agent_run_id = None
        self.response_queue = queue.Queue()
        self.streaming_thread = None
        self.is_streaming = False
        
        # Attached files
        self.attached_files = []
        
        self.setup_ui()
        self.root.after(100, self.check_response_queue)
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(conn_frame, text="Suna API URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.url_var = tk.StringVar(value="http://localhost:8000")
        self.url_entry = ttk.Entry(conn_frame, textvariable=self.url_var, width=40)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(conn_frame, text="API Key (optional):").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(conn_frame, textvariable=self.api_key_var, width=30, show="*")
        self.api_key_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_to_suna)
        self.connect_btn.grid(row=0, column=4, padx=(10, 0))
        
        self.status_label = ttk.Label(conn_frame, text="Not connected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=5, sticky=tk.W, pady=(5, 0))
        
        conn_frame.columnconfigure(1, weight=1)
        conn_frame.columnconfigure(3, weight=1)
        
        # File attachment frame
        file_frame = ttk.LabelFrame(main_frame, text="File Attachments", padding="5")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="Add Files", command=self.add_files).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(file_frame, text="Clear Files", command=self.clear_files).grid(row=0, column=1, padx=(0, 10))
        
        self.files_listbox = tk.Listbox(file_frame, height=3)
        self.files_listbox.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        file_frame.columnconfigure(2, weight=1)
        
        # Chat area
        chat_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="5")
        chat_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, height=20)
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("user", foreground="blue", font=("TkDefaultFont", 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground="green")
        self.chat_display.tag_configure("system", foreground="gray", font=("TkDefaultFont", 9, "italic"))
        self.chat_display.tag_configure("error", foreground="red", font=("TkDefaultFont", 10, "bold"))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # Message input
        self.message_entry = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=4)
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.send_btn = ttk.Button(buttons_frame, text="Send Message", command=self.send_message, state=tk.DISABLED)
        self.send_btn.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.stop_btn = ttk.Button(buttons_frame, text="Stop Agent", command=self.stop_agent, state=tk.DISABLED)
        self.stop_btn.grid(row=1, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.new_chat_btn = ttk.Button(buttons_frame, text="New Chat", command=self.new_chat, state=tk.DISABLED)
        self.new_chat_btn.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Bind Enter key to send message
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
    
    def add_files(self):
        """Add files to be attached to the next message."""
        files = filedialog.askopenfilenames(
            title="Select files to attach",
            filetypes=[
                ("All files", "*.*"),
                ("Text files", "*.txt"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Documents", "*.pdf *.doc *.docx"),
                ("Code files", "*.py *.js *.html *.css *.json *.xml")
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
    
    def connect_to_suna(self):
        """Connect to the Suna API."""
        url = self.url_var.get().strip()
        api_key = self.api_key_var.get().strip() or None
        
        if not url:
            messagebox.showerror("Error", "Please enter a Suna API URL")
            return
        
        try:
            self.client = SunaClient(url, api_key)
            
            # Test connection
            if self.client.health_check():
                self.status_label.config(text="Connected successfully", foreground="green")
                self.send_btn.config(state=tk.NORMAL)
                self.new_chat_btn.config(state=tk.NORMAL)
                self.connect_btn.config(text="Reconnect")
                self.append_to_chat("System: Connected to Suna API successfully!", "system")
            else:
                self.status_label.config(text="Connection failed - API not responding", foreground="red")
                messagebox.showerror("Connection Error", "Failed to connect to Suna API. Please check the URL and try again.")
        
        except Exception as e:
            self.status_label.config(text=f"Connection error: {str(e)}", foreground="red")
            messagebox.showerror("Connection Error", f"Failed to connect to Suna API:\n{str(e)}")
    
    def new_chat(self):
        """Start a new chat conversation."""
        # Clear current state
        self.current_thread_id = None
        self.current_agent_run_id = None
        self.is_streaming = False
        
        # Clear chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Clear attached files
        self.clear_files()
        
        self.append_to_chat("System: New conversation started. Send a message to begin!", "system")
        self.stop_btn.config(state=tk.DISABLED)
    
    def send_message(self):
        """Send a message to the Suna agent."""
        if not self.client:
            messagebox.showerror("Error", "Please connect to Suna API first")
            return
        
        message = self.message_entry.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message")
            return
        
        # Disable send button during processing
        self.send_btn.config(state=tk.DISABLED)
        
        # Display user message
        self.append_to_chat(f"You: {message}", "user")
        
        # Clear the input
        self.message_entry.delete(1.0, tk.END)
        
        # Start agent in a separate thread
        threading.Thread(target=self._send_message_worker, args=(message,), daemon=True).start()
    
    def _send_message_worker(self, message: str):
        """Worker thread for sending messages."""
        try:
            # If this is the first message, initiate a new agent
            if not self.current_thread_id:
                self.response_queue.put({"type": "system", "content": "Initiating new conversation..."})
                
                result = self.client.initiate_agent(message, self.attached_files)
                self.current_thread_id = result.get("thread_id")
                self.current_agent_run_id = result.get("agent_run_id")
                
                self.response_queue.put({"type": "system", "content": f"Conversation started (Thread: {self.current_thread_id})"})
                
                # Clear attached files after sending
                self.response_queue.put({"type": "clear_files"})
            else:
                # For subsequent messages, start a new agent run
                self.response_queue.put({"type": "system", "content": "Processing your message..."})
                
                result = self.client.start_agent(self.current_thread_id)
                self.current_agent_run_id = result.get("agent_run_id")
            
            # Start streaming responses
            if self.current_agent_run_id:
                self.is_streaming = True
                self.response_queue.put({"type": "enable_stop"})
                self.client.stream_agent_responses(self.current_agent_run_id, self._handle_stream_response)
            
        except Exception as e:
            self.response_queue.put({"type": "error", "content": f"Error: {str(e)}"})
        finally:
            self.is_streaming = False
            self.response_queue.put({"type": "enable_send"})
            self.response_queue.put({"type": "disable_stop"})
    
    def _handle_stream_response(self, data: Dict[str, Any]):
        """Handle streaming response data."""
        self.response_queue.put(data)
    
    def stop_agent(self):
        """Stop the currently running agent."""
        if self.current_agent_run_id and self.client:
            threading.Thread(target=self._stop_agent_worker, daemon=True).start()
    
    def _stop_agent_worker(self):
        """Worker thread for stopping the agent."""
        try:
            if self.client.stop_agent(self.current_agent_run_id):
                self.response_queue.put({"type": "system", "content": "Agent stopped successfully"})
            else:
                self.response_queue.put({"type": "error", "content": "Failed to stop agent"})
        except Exception as e:
            self.response_queue.put({"type": "error", "content": f"Error stopping agent: {str(e)}"})
        finally:
            self.is_streaming = False
            self.response_queue.put({"type": "enable_send"})
            self.response_queue.put({"type": "disable_stop"})
    
    def check_response_queue(self):
        """Check for new responses in the queue and update UI."""
        try:
            while True:
                data = self.response_queue.get_nowait()
                self._process_response(data)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_response_queue)
    
    def _process_response(self, data: Dict[str, Any]):
        """Process a response from the agent."""
        response_type = data.get("type", "")
        content = data.get("content", "")
        
        if response_type == "system":
            self.append_to_chat(f"System: {content}", "system")
        elif response_type == "error":
            self.append_to_chat(f"Error: {content}", "error")
        elif response_type == "enable_send":
            self.send_btn.config(state=tk.NORMAL)
        elif response_type == "disable_send":
            self.send_btn.config(state=tk.DISABLED)
        elif response_type == "enable_stop":
            self.stop_btn.config(state=tk.NORMAL)
        elif response_type == "disable_stop":
            self.stop_btn.config(state=tk.DISABLED)
        elif response_type == "clear_files":
            self.clear_files()
        elif response_type == "message":
            # Handle agent message responses
            role = data.get("role", "assistant")
            if role == "assistant":
                self.append_to_chat(f"Suna: {content}", "assistant")
        elif response_type == "delta":
            # Handle streaming delta responses
            delta_content = data.get("delta", {}).get("content", "")
            if delta_content:
                self.append_to_chat(delta_content, "assistant", newline=False)
        else:
            # Handle other response types
            if content:
                self.append_to_chat(f"Response: {content}", "assistant")
    
    def append_to_chat(self, text: str, tag: str = "", newline: bool = True):
        """Append text to the chat display."""
        self.chat_display.config(state=tk.NORMAL)
        
        if newline and self.chat_display.get(1.0, tk.END).strip():
            self.chat_display.insert(tk.END, "\n")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        if newline:
            self.chat_display.insert(tk.END, f"[{timestamp}] {text}\n", tag)
        else:
            self.chat_display.insert(tk.END, text, tag)
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

def main():
    """Main function to run the Suna GUI client."""
    root = tk.Tk()
    app = SunaGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down Suna GUI client...")

if __name__ == "__main__":
    main()