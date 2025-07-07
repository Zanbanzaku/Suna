# Suna AI Agent Desktop Client

A desktop GUI application for connecting to and interacting with the [Suna AI Agent platform](https://github.com/kortix-ai/suna). This client provides an intuitive interface to chat with Suna, upload files, and manage conversations.

![Suna GUI Client](screenshot.png)

## What is Suna?

Suna is an open-source generalist AI agent that acts on your behalf to accomplish real-world tasks. It combines powerful capabilities including:

- **Browser automation** to navigate the web and extract data
- **File management** for document creation and editing
- **Web crawling** and extended search capabilities
- **Command-line execution** for system tasks
- **Website deployment** and API integrations
- **Research and analysis** across multiple domains

## Features

- 🖥️ **Desktop GUI** - Easy-to-use interface built with Python tkinter
- 💬 **Real-time Chat** - Stream responses from Suna AI agent
- 📁 **File Upload** - Attach multiple files to your conversations
- 🔄 **Conversation Management** - Start new chats and manage ongoing conversations
- ⏹️ **Agent Control** - Start and stop agent runs as needed
- 🔗 **Flexible Connection** - Connect to local or remote Suna instances
- 🔐 **API Key Support** - Optional authentication for secured instances

## Prerequisites

Before using this client, you need:

1. **Python 3.8+** installed on your system
2. **A running Suna instance** (either local or remote)

### Setting up Suna

To run Suna locally, follow these steps:

```bash
# Clone the Suna repository
git clone https://github.com/kortix-ai/suna.git
cd suna

# Run the setup wizard
python setup.py

# Start the services
python start.py
```

For detailed setup instructions, see the [Suna Self-Hosting Guide](https://github.com/kortix-ai/suna/blob/master/docs/SELF-HOSTING.md).

## Installation

1. **Download the GUI client files:**
   ```bash
   # Download the client files to your local machine
   wget https://raw.githubusercontent.com/[your-repo]/suna_gui_client.py
   wget https://raw.githubusercontent.com/[your-repo]/requirements.txt
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python suna_gui_client.py
   ```

## Usage

### 1. Connect to Suna

1. Launch the GUI client
2. Enter your Suna API URL (default: `http://localhost:8000`)
3. Optionally enter an API key if your instance requires authentication
4. Click "Connect" to establish connection

### 2. Start a Conversation

1. Once connected, click "New Chat" to start a fresh conversation
2. Type your message in the text area at the bottom
3. Optionally attach files using the "Add Files" button
4. Click "Send Message" or press `Ctrl+Enter` to send

### 3. Interact with Suna

- **View responses** in real-time as Suna processes your request
- **Upload files** for analysis, processing, or context
- **Stop agent runs** if needed using the "Stop Agent" button
- **Start new conversations** to change topics or clear context

## Example Use Cases

Here are some examples of what you can ask Suna to do:

### Research and Analysis
```
Analyze the market for my next company in the healthcare industry, located in the UK. Give me the major players, their market size, strengths, and weaknesses, and add their website URLs. Once done, generate a PDF report.
```

### Data Processing
```
My company asked me to set up an Excel spreadsheet with all the information about Italian lottery games (Lotto, 10eLotto, and Million Day). Based on that, generate and send me a spreadsheet with all the basic information.
```

### Trip Planning
```
Generate a personal trip to London, with departure from Bangkok on the 1st of May. The trip will last 10 days. Find accommodation in the center of London, with a rating on Google reviews of at least 4.5.
```

### LinkedIn Research
```
Go on LinkedIn, and find me 10 profiles available - they are not working right now - for a junior software engineer position, who are located in Munich, Germany.
```

## Configuration

### Connection Settings

- **Suna API URL**: The base URL of your Suna instance
  - Local: `http://localhost:8000`
  - Remote: `https://your-suna-instance.com`

- **API Key**: Optional authentication token
  - Required only if your Suna instance has authentication enabled
  - Leave blank for open instances

### File Attachments

The client supports attaching various file types:
- Text files (`.txt`, `.md`, `.csv`)
- Images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`)
- Documents (`.pdf`, `.doc`, `.docx`)
- Code files (`.py`, `.js`, `.html`, `.css`, `.json`, `.xml`)
- Any other file type

## Keyboard Shortcuts

- `Ctrl+Enter` - Send message
- `Escape` - Clear message input (when focused)

## Troubleshooting

### Connection Issues

1. **"Connection failed - API not responding"**
   - Verify Suna is running: `curl http://localhost:8000/api/health`
   - Check the URL is correct
   - Ensure no firewall is blocking the connection

2. **Authentication errors**
   - Verify your API key is correct
   - Check if the Suna instance requires authentication

### Performance Issues

1. **Slow responses**
   - This is normal for complex tasks (research, analysis, file processing)
   - Suna may be performing browser automation or API calls
   - Wait for the process to complete or use "Stop Agent" if needed

2. **Large file uploads**
   - Large files may take time to upload
   - Consider breaking down large datasets into smaller files

### Error Messages

- **"Failed to initiate agent"**: Check your Suna instance has sufficient resources
- **"Streaming failed"**: Network connectivity issue or agent stopped unexpectedly
- **"Agent run not found"**: The agent process may have crashed or been terminated

## Development

To modify or extend the client:

1. **Clone the repository**
2. **Install development dependencies**
3. **Make your changes**
4. **Test with a local Suna instance**

The client is built with:
- **tkinter** for the GUI (included with Python)
- **requests** for HTTP communication
- **threading** for non-blocking operations
- **queue** for thread-safe communication

## Security Considerations

- **API Keys**: Store securely and don't share
- **File Uploads**: Be cautious with sensitive files
- **Network**: Use HTTPS for remote connections when possible
- **Local Instance**: Consider firewall rules for local Suna instances

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For issues related to:
- **This GUI client**: Open an issue in this repository
- **Suna platform**: Visit the [Suna repository](https://github.com/kortix-ai/suna)
- **General questions**: Join the [Suna Discord community](https://discord.gg/Py6pCBUUPw)

## Acknowledgments

- [Kortix AI](https://kortix.ai/) for creating the Suna platform
- The open-source community for tools and libraries
- [Suna contributors](https://github.com/kortix-ai/suna/graphs/contributors)