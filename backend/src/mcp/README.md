# Turerez MCP Server

## Overview
The Turerez Model Context Protocol (MCP) Server provides external API access to all Internshala automation capabilities through a standardized protocol. This enables integration with AI assistants, external applications, and development tools.

## Features

### 🛠️ Available Tools
1. **extract_chats** - Extract chat messages from Internshala conversations
2. **search_internships** - Search and scrape internships with filters
3. **analyze_market** - Perform comprehensive market analysis
4. **export_data** - Export data with advanced analytics and visualizations
5. **browser_control** - Control browser automation (connect/disconnect/status)
6. **get_recommendations** - AI-powered recommendations for applications

### 📄 Resources
- `turerez://config` - Current configuration settings
- `turerez://status` - Server and browser status
- `turerez://exports` - Recent export history

## Installation

```bash
# Install MCP dependencies
python src/mcp/setup.py

# Or manually:
pip install -r src/mcp/requirements-mcp.txt
```

## Usage

### Start the Server
```bash
python src/mcp/server.py
```

### Test with Demo Client
```bash
python src/mcp/client_demo.py
```

## Tool Examples

### Extract Chat Messages
```json
{
  "tool": "extract_chats",
  "arguments": {
    "limit": 50,
    "export_format": "json",
    "include_analytics": true
  }
}
```

### Search Internships
```json
{
  "tool": "search_internships", 
  "arguments": {
    "category": "Computer Science",
    "location": ["Bangalore", "Remote"],
    "stipend_min": 10000,
    "duration": 3,
    "limit": 20
  }
}
```

### Market Analysis
```json
{
  "tool": "analyze_market",
  "arguments": {
    "analysis_type": "comprehensive",
    "data_source": "recent_search"
  }
}
```

### Export Data
```json
{
  "tool": "export_data",
  "arguments": {
    "data_type": "combined",
    "format": "excel",
    "analytics_level": "comprehensive",
    "include_charts": true
  }
}
```

## Integration Examples

### With AI Assistants
The MCP server enables AI assistants to:
- Extract and analyze your Internshala conversations
- Search for internships matching specific criteria
- Generate market insights and recommendations
- Export data in various formats with analytics

### With External Applications
Applications can integrate Turerez functionality by:
- Connecting to the MCP server via stdio/HTTP/WebSocket
- Calling tools to automate Internshala interactions
- Accessing real-time status and configuration
- Retrieving export history and analytics

## Configuration

### Server Configuration (`mcp-config.json`)
```json
{
  "name": "turerez-mcp-server",
  "version": "1.0.0",
  "mcpServers": {
    "turerez-automation": {
      "command": "python",
      "args": ["src/mcp/server.py"],
      "description": "Turerez Internshala automation via MCP"
    }
  }
}
```

### Client Configuration
```json
{
  "servers": {
    "turerez-automation": {
      "command": "python",
      "args": ["path/to/src/mcp/server.py"],
      "capabilities": ["resources", "tools", "logging"]
    }
  }
}
```

## Development

### Adding New Tools
1. Define tool schema in `handle_list_tools()`
2. Implement handler in `handle_call_tool()`
3. Add documentation and examples
4. Test with client demo

### Adding New Resources
1. Define resource in `handle_list_resources()`
2. Implement reader in `handle_read_resource()`
3. Update documentation

## Security Considerations

- Server runs with same permissions as Turerez application
- Browser automation requires user credentials
- Export files are created in user-specified directories
- No network access beyond Internshala.com

## Troubleshooting

### Common Issues
1. **MCP dependencies not found**
   - Install with: `pip install mcp>=1.0.0`
   - Or run in demo mode

2. **Browser connection fails**
   - Use `browser_control` tool to connect manually
   - Check Internshala login credentials

3. **Export fails**
   - Verify output directory permissions
   - Check disk space for large exports

### Debug Mode
```bash
# Enable debug logging
TUREREZ_LOG_LEVEL=DEBUG python src/mcp/server.py
```

## Roadmap

- [ ] HTTP transport support
- [ ] WebSocket transport support  
- [ ] Real-time notifications
- [ ] Advanced authentication
- [ ] Rate limiting and quotas
- [ ] Multi-user support
