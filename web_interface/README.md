# AI Prompt Engineering System - Web Interface

## Overview
Web interface for the AI Prompt Engineering System, providing a user-friendly way to manage hierarchical rules and interact with MCP tools.

## Architecture
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI web server
- **Integration**: Bridge to MCP server via HTTP/WebSocket
- **Database**: SQLite (shared with MCP server)

## Project Structure
```
web_interface/
├── frontend/          # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── public/
│   └── package.json
├── backend/           # FastAPI server
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
└── docker-compose.yml
```

## Development Setup

### Prerequisites
- Node.js 18+
- Python 3.8+
- npm or yarn

### Installation
1. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Running the Application
1. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

3. Access the application at `http://localhost:3000`

## Features

### Rule Management
- Visual rule hierarchy browser
- Rule editor with syntax highlighting
- Dependency visualization
- Real-time collaboration

### MCP Integration
- Execute MCP tools through web interface
- Access MCP resources
- Monitor system performance
- Rule validation and optimization

### Templates
- Pre-built rule templates
- Framework-specific rule sets
- Export/import functionality

## API Endpoints

### Rule Management
- `GET /api/rules` - List all rules
- `POST /api/rules` - Create new rule
- `PUT /api/rules/{id}` - Update rule
- `DELETE /api/rules/{id}` - Delete rule

### MCP Integration
- `POST /api/mcp/generate-prompt` - Generate prompt
- `POST /api/mcp/analyze-rules` - Analyze rules
- `POST /api/mcp/validate-rules` - Validate rules
- `GET /api/mcp/resources/{type}` - Get MCP resources

### Real-time
- `WebSocket /ws/updates` - Real-time updates