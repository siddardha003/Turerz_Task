# Turerez Web Interface

## 🚀 Quick Start Guide

### 1. Start the Web Interface

Navigate to the web interface directory and run:

```bash
cd web_interface
python start_server.py
```

**Or run directly:**

```bash
cd web_interface
python app.py
```

### 2. Access the Interface

- **Main Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **System Status**: http://localhost:8000/api/status

### 3. Features

#### 🎯 **Natural Language Processing**
- Enter commands like: "Show marketing internships with stipend above 10000"
- AI-powered query interpretation
- Smart parameter extraction

#### 🛠️ **MCP Integration** 
- Full access to all 8 MCP tools
- Real-time browser automation
- Direct integration with existing functionality

#### 📊 **Data Export**
- CSV, JSON, and Excel formats
- Real-time data from Internshala
- Analytics and visualization options

#### 🔧 **System Controls**
- Browser automation toggle
- AI features control
- Real-time mode switching

### 4. API Endpoints

#### Core Endpoints:
- `POST /api/process-query` - Process natural language queries
- `POST /api/mcp-tool` - Direct MCP tool execution
- `GET /api/mcp-tools` - List available tools
- `POST /api/browser-control` - Control browser automation
- `POST /api/export` - Export data
- `GET /api/status` - System status

#### Example API Usage:

```javascript
// Process natural language query
fetch('/api/process-query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: "Find tech internships in Bangalore",
        user_preferences: { realtime_mode: true }
    })
});

// Direct MCP tool execution
fetch('/api/mcp-tool', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        tool_name: "search_internships",
        parameters: {
            category: "technology",
            location: "bangalore",
            limit: 20
        }
    })
});
```

### 5. Integration with Existing Features

#### ✅ **Preserves All Current Functionality**
- All existing MCP tools work unchanged
- Chat extraction system intact
- Export system fully functional
- Browser automation preserved
- AI features maintained

#### ✅ **Adds New Capabilities**
- Web-based user interface
- REST API access
- Real-time system monitoring
- Enhanced export options
- Mobile-responsive design

### 6. System Requirements

#### Dependencies:
- FastAPI 0.104+
- Uvicorn (ASGI server)
- Python 3.8+
- All existing Turerez dependencies

#### Browser Support:
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

### 7. Configuration

The web interface uses the same `.env` configuration as the main system:

```env
# Web Interface Settings (optional)
WEB_HOST=0.0.0.0
WEB_PORT=8000
WEB_RELOAD=true

# All existing Turerez settings work
INTERNSHALA_EMAIL=your_email@example.com
INTERNSHALA_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
```

### 8. Development

#### File Structure:
```
web_interface/
├── app.py              # FastAPI application
├── templates/
│   └── index.html      # Main web interface
├── static/
│   └── styles.css      # Additional CSS
├── requirements.txt    # Web dependencies
├── start_server.py     # Startup script
└── README.md          # This file
```

#### Extending the Interface:
1. Add new API endpoints in `app.py`
2. Modify the frontend in `templates/index.html`
3. Add new MCP tool integrations
4. Customize styling in `static/styles.css`

### 9. Troubleshooting

#### Common Issues:

**Port already in use:**
```bash
# Kill existing server
pkill -f uvicorn
# Or use different port
uvicorn app:app --port 8001
```

**MCP server not found:**
```bash
# Make sure you're in the backend directory
cd /path/to/Turerez/backend/web_interface
python start_server.py
```

**Dependencies missing:**
```bash
# Install web interface dependencies
pip install -r requirements.txt
```

### 10. Production Deployment

#### Using Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

#### Using Docker:
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Environment Variables:
```env
WEB_HOST=0.0.0.0
WEB_PORT=8000
WEB_WORKERS=4
LOG_LEVEL=info
```

### 11. Security Considerations

- The web interface runs on all interfaces (0.0.0.0) by default
- For production, consider using HTTPS
- Add authentication if needed
- Review CORS settings for production

### 12. Performance

- Async/await throughout for better performance
- Background task support for long-running operations
- Efficient data streaming for large exports
- Caching for frequently accessed data

---

## 🎉 Ready to Use!

Your Turerez system now has a full web interface while maintaining all existing functionality. The MCP server integration ensures seamless operation with external tools and AI assistants.

**Start the server and visit http://localhost:8000 to begin!**
