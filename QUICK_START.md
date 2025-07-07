# Suna Desktop - Quick Start Guide

Get Suna AI Agent running on your desktop in minutes!

## ⚡ Super Quick Start (1-2-3)

### 1. Download and Install

```bash
# Option A: Clone this repository
git clone [this-repository-url]
cd suna-desktop

# Option B: Download files manually
# Download all .py files and requirements.txt to a folder
```

### 2. Run the Launcher

```bash
# Install dependencies and run
pip install -r requirements.txt
python launch_suna_desktop.py
```

### 3. Follow the Setup Wizard

The launcher will automatically:
- Check system requirements
- Download Suna
- Set up configuration files
- Create launcher scripts

## 🔧 Prerequisites

Make sure you have:
- **Python 3.8+** ([Download here](https://python.org/downloads/))
- **Docker Desktop** ([Download here](https://docs.docker.com/get-docker/))
- **Git** (optional, for easier updates)

## 📱 Accessing Suna

After setup, you can access Suna through:

### Desktop Application
- **Start**: Run the created launcher script
- **Use**: Chat tab for conversations, Dashboard for service management

### Web Interface (Full Suna)
- **URL**: http://localhost:3000
- **Start**: Click "Open Web Interface" in Desktop Dashboard

### Mobile Interface
- **URL**: http://[YOUR_COMPUTER_IP]:5000
- **Find IP**: Windows: `ipconfig`, Mac/Linux: `ifconfig`
- **Access**: Any device on your WiFi network

## ⚙️ Essential Configuration

### 1. API Keys (Required)
Add your LLM API keys in **Settings tab**:
```
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### 2. Database (Required)
1. Create free account at [Supabase](https://supabase.com)
2. Create new project
3. Add credentials to Settings tab:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

### 3. Optional Services
- **Web Search**: Add Tavily API key for web search capabilities
- **Web Scraping**: Add Firecrawl API key for advanced web scraping

## 🚀 First Conversation

1. **Start Services**: Dashboard tab → "Start Services"
2. **Open Chat**: Chat tab → type your message
3. **Try Examples**:
   - "Analyze the current AI market trends"
   - "Find 5 Python libraries for data visualization"
   - "Help me plan a trip to Tokyo"

## 📊 Common Use Cases

### Research Assistant
```
Research and compare the top 5 project management tools for small teams. 
Include pricing, key features, and pros/cons for each.
```

### Data Analysis
```
Analyze this CSV file and create visualizations showing sales trends 
by region and product category.
```

### Web Automation
```
Go to Hacker News, find the top 10 posts today, and summarize 
the most interesting technical discussions.
```

### Content Creation
```
Create a comprehensive blog post about sustainable web development 
practices, including code examples and best practices.
```

## 🔧 Troubleshooting

### Setup Issues
- **Docker not found**: Install Docker Desktop and ensure it's running
- **Permission errors**: Add user to docker group (Linux/Mac)
- **Port conflicts**: Change ports in Settings if 3000/8000/5000 are busy

### Service Issues
- **Won't start**: Check Docker is running, check disk space
- **No API response**: Verify API keys are correct and have credits
- **Database errors**: Check Supabase credentials and network

### Performance Issues
- **Slow responses**: Normal for complex tasks, check internet connection
- **High CPU/RAM**: Suna runs multiple containers, close other apps if needed

## 📚 Next Steps

### Learn More
- **Full Documentation**: See README.md for detailed information
- **Suna Platform**: [GitHub Repository](https://github.com/kortix-ai/suna)
- **Video Examples**: [Official Website](https://www.suna.so)

### Advanced Setup
- **Custom Agents**: Create specialized AI agents for specific tasks
- **Network Sharing**: Configure for team access
- **Cloud Deployment**: Deploy to cloud for remote access

### Community
- **Discord**: [Join Suna Community](https://discord.gg/Py6pCBUUPw)
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share your use cases and get help

## 🎯 Success Checklist

- [ ] Python 3.8+ installed
- [ ] Docker Desktop installed and running
- [ ] Suna Desktop downloaded and launched
- [ ] Setup wizard completed successfully
- [ ] API keys configured (Anthropic/OpenAI)
- [ ] Supabase database configured
- [ ] Services started successfully
- [ ] First conversation completed
- [ ] Mobile interface accessible (optional)

**Congratulations!** 🎉 You now have a fully functional, self-hosted AI agent platform running on your desktop!

---

**Need Help?** 
- Check the [full README](README.md) for detailed documentation
- Join our [Discord community](https://discord.gg/Py6pCBUUPw) for support
- Open an issue on GitHub if you encounter problems