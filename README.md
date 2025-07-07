# Suna Desktop - Self-Hosting AI Agent Platform

A comprehensive desktop application that **self-hosts** the [Suna AI Agent platform](https://github.com/kortix-ai/suna) with both desktop GUI and mobile web interfaces. This is a complete package that bundles Suna with an easy-to-use interface for personal and team use.

![Suna Desktop](screenshot.png)

## What is Suna?

Suna is an open-source generalist AI agent that acts on your behalf to accomplish real-world tasks. It combines powerful capabilities including:

- **Browser automation** to navigate the web and extract data
- **File management** for document creation and editing
- **Web crawling** and extended search capabilities
- **Command-line execution** for system tasks
- **Website deployment** and API integrations
- **Research and analysis** across multiple domains

## Features

### 🖥️ Desktop Application
- **Service Management** - Start/stop Suna services with one click
- **Integrated Chat** - Chat directly with Suna from the desktop app
- **Configuration Manager** - Easy setup and management of API keys and settings
- **Service Monitoring** - Real-time status of all Suna components
- **Environment Editor** - Built-in editor for configuration files

### � Mobile Web Interface
- **Cross-platform Access** - Use Suna from any device with a web browser
- **Mobile-optimized UI** - Responsive design for smartphones and tablets
- **Real-time Chat** - Full conversation capabilities on mobile
- **File Upload Support** - Attach files from mobile devices

### 🚀 Self-Hosting Capabilities
- **Complete Package** - Includes all Suna components (backend, frontend, database)
- **Docker Integration** - Automated service management with Docker Compose
- **One-click Setup** - Automated installation and configuration
- **Local Network Access** - Share with other devices on your network
- **No External Dependencies** - Run completely offline (after initial setup)

## Prerequisites

Before installing Suna Desktop, ensure you have:

1. **Python 3.8+** installed on your system
2. **Docker and Docker Compose** for running Suna services
3. **Git** (recommended) or internet connection for downloading Suna

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for Suna Desktop + additional space for Docker images
- **Network**: Internet connection for initial setup and LLM API calls

## Quick Start Installation

### Option 1: Automated Setup (Recommended)

1. **Download and run the setup script:**
   ```bash
   # Download the setup files
   git clone [this-repository-url]
   cd suna-desktop
   
   # Run automated setup
   python setup_suna_desktop.py
   ```

2. **Follow the setup wizard:**
   - The script will check system requirements
   - Download and configure Suna automatically
   - Create launcher scripts for your platform

3. **Start Suna Desktop:**
   ```bash
   # Windows
   run_suna_desktop.bat
   
   # Linux/macOS
   ./run_suna_desktop.sh
   
   # Or directly with Python
   python run_suna_desktop.py
   ```

### Option 2: Manual Installation

1. **Download the files:**
   ```bash
   wget https://raw.githubusercontent.com/[your-repo]/suna_desktop.py
   wget https://raw.githubusercontent.com/[your-repo]/suna_chat.py
   wget https://raw.githubusercontent.com/[your-repo]/mobile_web.py
   wget https://raw.githubusercontent.com/[your-repo]/requirements.txt
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download Suna manually:**
   ```bash
   git clone https://github.com/kortix-ai/suna.git
   ```

4. **Run the desktop application:**
   ```bash
   python suna_desktop.py
   ```

## Usage

### 1. Initial Setup

1. **Launch Suna Desktop** using the created launcher script
2. **Go to the Setup tab** if it's your first time
3. **Select your Suna directory** (downloaded during installation)
4. **Check requirements** to ensure Docker and dependencies are ready
5. **Setup environment** to create necessary configuration files
6. **Complete setup** to enable other features

### 2. Configure Suna

1. **Go to Settings tab** to configure your environment
2. **Add API Keys** for LLM providers (Anthropic, OpenAI, etc.)
3. **Configure database** settings (Supabase recommended)
4. **Set up optional services** like Tavily for web search

### 3. Start Services

1. **Go to Dashboard tab** to manage Suna services
2. **Click "Start Services"** to launch Suna with Docker Compose
3. **Monitor service status** with real-time health indicators
4. **View logs** to troubleshoot any issues

### 4. Use Suna

#### Desktop Interface
1. **Go to Chat tab** for the integrated chat interface
2. **Attach files** using the file attachment section
3. **Send messages** and watch Suna work in real-time
4. **Start new conversations** as needed

#### Web Interface (Desktop/Laptop)
1. **Click "Open Web Interface"** from the Dashboard
2. Access the full Suna web app at `http://localhost:3000`
3. Use all Suna features through the browser

#### Mobile Interface
1. **Access from any device** on your network
2. **Navigate to** `http://[YOUR_COMPUTER_IP]:5000`
3. **Use the mobile-optimized interface** for chatting on the go

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

### Environment Setup

Suna Desktop automatically creates configuration files during setup:

#### Backend Configuration (`suna/backend/.env`)
```bash
# LLM API Keys (Required)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Database (Required)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Optional Services
TAVILY_API_KEY=your_tavily_key_for_web_search
FIRECRAWL_API_KEY=your_firecrawl_key_for_scraping
```

#### Frontend Configuration (`suna/frontend/.env.local`)
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

### Service Ports

By default, Suna Desktop uses these ports:
- **Frontend (Web UI)**: `3000`
- **Backend (API)**: `8000`
- **Mobile Interface**: `5000`
- **Redis**: `6379`
- **RabbitMQ**: `5672`, `15672` (management UI)

### File Attachments

All interfaces support various file types:
- **Text files**: `.txt`, `.md`, `.csv`, `.json`, `.xml`, `.yaml`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`
- **Documents**: `.pdf`, `.doc`, `.docx`
- **Code files**: `.py`, `.js`, `.html`, `.css`, `.sql`
- **Archives**: `.zip`, `.tar`, `.gz`

### Keyboard Shortcuts

- **Desktop Chat**: `Ctrl+Enter` to send message
- **Mobile Web**: `Enter` to send, `Shift+Enter` for new line
- **Web Interface**: Standard Suna shortcuts apply

## Troubleshooting

### Setup Issues

1. **Docker not found**
   - Install Docker Desktop from [docker.com](https://docs.docker.com/get-docker/)
   - Ensure Docker is running before starting Suna Desktop

2. **Permission errors**
   - On Linux/macOS: Ensure user is in docker group
   - Run: `sudo usermod -aG docker $USER` then logout/login

3. **Port conflicts**
   - Check if ports 3000, 5000, 8000 are available
   - Use `netstat -tulpn | grep :3000` to check port usage
   - Modify ports in Settings tab if needed

### Service Issues

1. **Services won't start**
   - Check Docker daemon is running
   - Verify sufficient disk space (>2GB free)
   - Check service logs in Dashboard tab

2. **Database connection errors**
   - Ensure Supabase credentials are correct in Settings
   - Create a new Supabase project if needed
   - Check network connectivity to Supabase

3. **LLM API errors**
   - Verify API keys are correct and have sufficient credits
   - Check API key format (no extra spaces/characters)
   - Try different LLM providers

### Performance Issues

1. **Slow agent responses**
   - Normal for complex tasks (research, analysis, automation)
   - Check system resources (CPU, RAM usage)
   - Ensure stable internet connection for LLM APIs

2. **High resource usage**
   - Suna runs multiple Docker containers
   - Close unnecessary applications
   - Consider upgrading system RAM if consistently high

### Network Issues

1. **Mobile interface not accessible**
   - Check firewall allows connections on port 5000
   - Ensure computer and mobile device are on same network
   - Use computer's actual IP address, not localhost

2. **Web interface loading issues**
   - Wait for all services to fully start (check Dashboard)
   - Clear browser cache and cookies
   - Try accessing from incognito/private browsing mode

## Development and Customization

### Architecture

Suna Desktop consists of:
- **Desktop GUI** (`suna_desktop.py`) - Main application with tkinter
- **Chat Interface** (`suna_chat.py`) - Integrated chat component
- **Mobile Web** (`mobile_web.py`) - Flask-based mobile interface
- **Service Manager** - Docker Compose integration
- **Configuration Manager** - Environment file handling

### Extending the Application

1. **Custom integrations** - Add new tools or APIs to Suna
2. **UI modifications** - Customize the desktop or mobile interface
3. **Additional services** - Add monitoring, backup, or other services
4. **Deployment options** - Package for distribution or cloud deployment

### Technology Stack

- **Desktop**: Python 3.8+, tkinter, threading, queue
- **Mobile Web**: Flask, HTML5, CSS3, JavaScript
- **Service Management**: Docker, Docker Compose
- **HTTP Communication**: requests library
- **Configuration**: JSON, environment files

## Security and Privacy

### Data Security

- **Local deployment** - All data stays on your machine
- **API key protection** - Keys stored in local environment files
- **Network isolation** - Optional firewall configuration
- **File access** - Limited to specified directories

### Privacy Considerations

- **LLM API calls** - Messages sent to configured LLM providers
- **Web search** - Optional services may access external APIs
- **Local storage** - Conversations stored in Supabase database
- **Network access** - Mobile interface accessible on local network

## Deployment Options

### Personal Use
- **Single-user setup** on personal computer
- **Family sharing** via mobile interface on local network
- **Offline capability** for air-gapped environments

### Small Team/Office
- **Shared network deployment** accessible by team members
- **Centralized configuration** with shared API keys
- **Multiple user access** via web and mobile interfaces

### Advanced Deployment
- **Cloud deployment** using Docker containers
- **Reverse proxy** setup for external access
- **Load balancing** for high-availability deployments

## Comparison with Cloud Suna

| Feature | Suna Desktop (Self-hosted) | Cloud Suna |
|---------|---------------------------|-------------|
| **Cost** | Free (after setup) | Subscription-based |
| **Privacy** | Complete local control | Data processed on cloud |
| **Setup** | Requires technical setup | Instant access |
| **Customization** | Full customization | Limited customization |
| **Mobile Access** | Local network only | Global access |
| **Maintenance** | Self-managed updates | Automatic updates |
| **Performance** | Depends on local hardware | Optimized cloud infrastructure |

## Contributing

We welcome contributions to make Suna Desktop better! You can help by:

### Code Contributions
1. **Fork this repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** and test thoroughly
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Other Ways to Contribute
- **Report bugs** and suggest improvements
- **Create documentation** and tutorials
- **Share your use cases** and configurations
- **Help other users** in discussions

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Support and Community

### Getting Help

For issues related to:
- **Suna Desktop**: Open an issue in this repository
- **Suna Core Platform**: Visit the [Suna repository](https://github.com/kortix-ai/suna)
- **General questions**: Join the [Suna Discord community](https://discord.gg/Py6pCBUUPw)

### Documentation and Resources

- **Suna Documentation**: [Official Docs](https://github.com/kortix-ai/suna/tree/master/docs)
- **Self-Hosting Guide**: [Detailed Setup](https://github.com/kortix-ai/suna/blob/master/docs/SELF-HOSTING.md)
- **API Reference**: Available at `http://localhost:8000/docs` when running
- **Video Tutorials**: [Watch Examples](https://www.suna.so)

### Community Showcase

Share your Suna Desktop setups and use cases:
- **Automation workflows** you've created
- **Custom integrations** and modifications
- **Deployment configurations** for different environments
- **Performance optimizations** and tips

## Acknowledgments

### Core Technologies
- **[Suna AI Platform](https://github.com/kortix-ai/suna)** by [Kortix AI](https://kortix.ai/)
- **[Docker](https://docker.com)** for containerization
- **[Python](https://python.org)** and tkinter for desktop GUI
- **[Flask](https://flask.palletsprojects.com)** for mobile web interface

### Contributors
- **Suna Core Team**: [Adam Cohen Hillel](https://x.com/adamcohenhillel), [Dat-lequoc](https://x.com/datlqqq), [Marko Kraemer](https://twitter.com/markokraemer)
- **Open Source Libraries**: Anthropic, OpenAI, Supabase, and many others
- **Community Contributors**: Everyone who reports issues, suggests improvements, and shares their setups

---

**Made with ❤️ for the open-source AI community**

*Suna Desktop brings the power of autonomous AI agents to your personal computer, giving you complete control over your AI workflows while maintaining privacy and customization.*