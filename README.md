# 🚀 Turerez - AI-Powered Internshala Automation

> **A comprehensive automation platform for Internshala with AI integration, web interface, and MCP (Model Context Protocol) server capabilities.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Web%20Interface-green.svg)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com)
[![Selenium](https://img.shields.io/badge/Selenium-Browser%20Automation-yellow.svg)](https://selenium.dev)

## ✨ Key Features

### 🤖 **AI-Powered Automation**
- **Natural Language Processing** - Process commands like *"Find marketing internships with stipend above ₹10,000"*
- **Smart Recommendations** - AI-powered internship suggestions based on your preferences
- **Content Analysis** - Automated analysis of job descriptions and requirements
- **OpenAI Integration** - GPT-4o-mini for intelligent query parsing and insights

### 🌐 **Modern Web Interface**
- **Responsive Web UI** - Beautiful, modern interface accessible via browser
- **Real-time Processing** - Live status updates and progress tracking
- **Natural Language Commands** - Type queries in plain English
- **System Controls** - Easy toggles for browser automation and AI features

### 🔧 **MCP Server Integration**
- **Model Context Protocol** - Standards-compliant MCP server
- **7 Core Tools** - Chat extraction, internship search, market analysis, and more
- **API Access** - RESTful endpoints for external integrations
- **Tool Orchestration** - Seamless coordination between different automation tools

### 📊 **Data Management & Export**
- **Multi-format Export** - CSV, JSON, Excel support
- **Advanced Analytics** - Comprehensive data analysis and insights
- **Chat Message Extraction** - Automated conversation data collection
- **Internship Scraping** - Intelligent job listing extraction with filters

### 🚀 **Browser Automation**
- **Selenium WebDriver** - Robust browser automation with session management
- **Rate Limiting** - Built-in request throttling to respect platform limits
- **Error Handling** - Advanced retry mechanisms and error recovery
- **Headless Support** - Background automation or visual debugging modes

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python 3.8+ | Core application logic |
| **Web Framework** | FastAPI | Modern web interface and API |
| **AI Integration** | OpenAI GPT-4o-mini | Natural language processing |
| **Browser Automation** | Selenium WebDriver | Web scraping and interaction |
| **Data Models** | Pydantic | Type-safe data validation |
| **Configuration** | Pydantic Settings | Environment management |
| **Async Processing** | asyncio | High-performance concurrent operations |
| **Logging** | Structured logging | Comprehensive debugging and monitoring |

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- OpenAI API key (optional, for AI features)

### 1. Clone & Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd Turerez

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (required)
# Add your Internshala credentials and OpenAI API key
notepad .env  # Windows
nano .env     # macOS/Linux
```

**Required Environment Variables:**
```env
INTERNSHALA_EMAIL=your_email@example.com
INTERNSHALA_PASSWORD=your_password
OPENAI_API_KEY=sk-your-openai-api-key  # Optional for AI features
```

### 3. Launch Web Interface
```bash
# Start the web server
cd web_interface
python app.py

# Or use the startup script
python start_server.py
```

🌐 **Access the web interface at: http://localhost:8000**

### 4. Alternative: CLI Usage
```bash
# Run CLI interface
python cli.py

# Or use MCP server directly
python src/mcp/server.py
```

## 📖 Usage Examples

### Web Interface
1. Open http://localhost:8000
2. Type natural language commands:
   - *"Show me graphic design internships in Mumbai"*
   - *"Find remote tech internships with high stipend"*
   - *"Extract recent chat messages"*
   - *"Analyze market trends for data science roles"*

### API Endpoints
```bash
# Get system status
curl http://localhost:8000/api/status

# List available MCP tools
curl http://localhost:8000/api/mcp-tools

# Process natural language query
curl -X POST http://localhost:8000/api/process-query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find marketing internships with stipend above 5000"}'
```

### CLI Commands
```bash
# Search internships
python cli.py search "python developer" --location "Remote" --stipend-min 10000

# Extract chat messages
python cli.py extract-chats --limit 50 --format csv

# Export data
python cli.py export --format excel --analytics-level detailed
```

## 📁 Project Structure

```
Turerez/
├── backend/
│   ├── src/
│   │   ├── ai/              # AI integration (OpenAI, analysis, recommendations)
│   │   ├── browser/         # Browser automation (Selenium, auth, rate limiting)
│   │   ├── chat/            # Chat message extraction and analysis
│   │   ├── export/          # Data export and processing utilities
│   │   ├── internships/     # Internship scraping and filtering
│   │   ├── mcp/             # Model Context Protocol server
│   │   └── utils/           # Common utilities (logging, date parsing)
│   ├── web_interface/       # FastAPI web application
│   ├── tests/               # Unit tests
│   ├── cli.py              # Command-line interface
│   └── requirements.txt     # Python dependencies
├── exports/                 # Generated export files
├── logs/                   # Application logs
└── .venv/                  # Virtual environment
```

## 🔧 Advanced Configuration

### Browser Settings
```env
HEADLESS=true                    # Run browser in headless mode
BROWSER_TIMEOUT=30000           # Page load timeout (ms)
REQUESTS_PER_MINUTE=30          # Rate limiting
CONCURRENT_REQUESTS=3           # Max concurrent requests
```

### AI Features
```env
ENABLE_AI_ANALYSIS=true         # Enable AI-powered analysis
ENABLE_SMART_RECOMMENDATIONS=true  # Enable AI recommendations
OPENAI_MODEL=gpt-4o-mini       # OpenAI model to use
OPENAI_MAX_TOKENS=4000         # Max tokens per request
```

### Export Options
```env
CSV_OUTPUT_DIR=./exports       # Output directory for exports
LOG_LEVEL=INFO                 # Logging level (DEBUG, INFO, WARNING, ERROR)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. **Check the logs** in the `logs/` directory
2. **Verify configuration** in your `.env` file
3. **Review API documentation** at http://localhost:8000/docs
4. **Open an issue** on GitHub with detailed error information

## 🙋‍♂️ Questions?

**Common Questions:**
- **Q: How do I get an OpenAI API key?** A: Visit https://platform.openai.com/api-keys
- **Q: Can I run without AI features?** A: Yes! Simply don't set the `OPENAI_API_KEY` variable
- **Q: Is my Internshala data safe?** A: All data stays local - no external transmission except to OpenAI (if enabled)
- **Q: Can I customize the scraping behavior?** A: Yes! Modify filters in `src/internships/scraper.py`

**Need help?** Feel free to ask about:
- Setup and configuration issues
- Feature customization
- API integration
- Performance optimization
- Adding new automation capabilities

---

*Built with ❤️ for efficient internship hunting and automation*
