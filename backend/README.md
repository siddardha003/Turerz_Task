# Turerz - Internshala MCP Automation

A Model Context Protocol (MCP) powered solution for automating Internshala interactions through natural language commands.

## Project Structure

```
backend/
├── src/
│   ├── models.py           # Pydantic data models
│   ├── config.py           # Configuration management
│   └── utils/
│       ├── logging.py      # Structured logging with trace IDs
│       └── date_parser.py  # Date parsing and normalization
├── requirements.txt        # Python dependencies
└── .env.example           # Environment configuration template
```

## Quick Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   playwright install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Internshala credentials
   ```

3. **Verify Setup**
   ```bash
   python -c "from src.models import ChatMessage; print('Models loaded successfully')"
   ```

## Data Models

### Core Entities
- **ChatMessage**: Represents individual chat messages with metadata
- **InternshipSummary**: Basic internship listing information
- **InternshipDetail**: Extended internship details with requirements
- **Filters**: ChatFilter and InternshipFilter for search criteria

### Key Features
- Automatic stipend parsing from text (₹5,000-10,000 → min/max values)
- IST timezone handling for Indian context
- Validation and type safety with Pydantic
- Structured export configuration

## Next Steps

**Task 1.2**: Playwright browser automation foundation
- Browser session management
- Internshala login flow
- Base scraping utilities

---

*Built for the Internshala automation assignment - September 2025*
