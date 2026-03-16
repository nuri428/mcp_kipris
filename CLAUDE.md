# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP KIPRIS is a Model Context Protocol (MCP) server that wraps the Korean Intellectual Property Rights Information Service (KIPRIS) API, enabling AI assistants like Claude to search Korean and foreign patents.

## Environment Setup

```bash
# Required environment variable
export KIPRIS_API_KEY="your_api_key"

# Install dependencies (uses uv)
pip install -e .
# or
uv sync
```

Python 3.11+ required. The project uses `uv` for dependency management and `ruff` for formatting/linting.

## Running the Server

```bash
# stdio mode (for MCP clients like Claude Desktop)
uv run python -m mcp_kipris.server

# HTTP/SSE mode
uv run python -m mcp_kipris.sse_server --http --port 6274 --host 0.0.0.0

# Via mcpo proxy (stdio → HTTP bridge)
uvx mcpo --port 6274 -- uv run python -m mcp_kipris.server

# Docker SSE server
bash sse_server_build.sh
```

## Running Tests

Tests are standalone scripts that make live API calls — they require a valid `KIPRIS_API_KEY`.

```bash
# Run individual test scripts from project root
python test/test_samsung_patents.py
python test/test_patent_keyword_search.py
python test/test_patent_detail_search.py

# Run pytest (if using pytest-style tests)
pytest test/
```

## Linting and Formatting

```bash
ruff check src/
ruff format src/
```

## Architecture

### Two-Layer Design

Each tool follows a two-layer pattern:

1. **API layer** (`src/mcp_kipris/kipris/api/`): Calls the KIPRIS HTTP API and parses XML responses into `pd.DataFrame`. All API classes extend `ABSKiprisAPI` which handles URL construction, `accessKey` injection, and async/sync call dispatch. Params are auto-converted to camelCase via `stringcase`.

2. **Tool layer** (`src/mcp_kipris/kipris/tools/`): Wraps the API layer as MCP tools. Each tool extends `ToolHandler` (`kipris/abc.py`) and must implement:
   - `get_tool_description()` → returns `mcp.types.Tool` with name, description, inputSchema, and metadata
   - `run_tool(args)` → sync execution, returns `Sequence[TextContent | ...]`
   - `run_tool_async(args)` → async execution using `asyncio.to_thread()` (preferred by server)

### Server Modes

- **`server.py`**: stdio-only MCP server using `mcp.server.stdio`
- **`sse_server.py`**: Starlette app supporting both SSE (`/sse`) and HTTP POST (`/messages/`) transports, plus a `/tools` JSON endpoint and `/.well-known/mcp` discovery endpoint. Uses uvicorn.

Both servers register all tool handlers at module-level into a `tool_handlers` dict. The `call_tool` handler tries `run_tool_async` first, falling back to `run_tool`.

### Tool Organization

```
kipris/tools/
  korean/    # 7 tools: applicant, free, search, righter, application_number, summary, detail
  foreign/   # 5 tools: applicant, application_number, free, international_application_number, international_open_number
```

All tool classes are exported from `kipris/tools/__init__.py` with `Korean*` and `Foreign*` prefixes.

### Adding a New Tool

1. Create an API class in `kipris/api/korean/` or `kipris/api/foreign/` extending `ABSKiprisAPI`
2. Create a tool class in `kipris/tools/korean/` or `kipris/tools/foreign/` extending `ToolHandler`
3. Export from `kipris/tools/__init__.py`
4. Register in both `server.py` and `sse_server.py` with `add_tool_handler()`

### Utility

`src/mcp_kipris/utils/patent_sim.py` contains experimental patent similarity analysis using TF-IDF + cosine similarity and LangChain/Ollama for keyword extraction. This is not registered as an MCP tool.

## Key Conventions

- All tool args are validated with Pydantic models (`BaseModel`) before use
- API responses are parsed into `pd.DataFrame`; tools format them as markdown tables via `.to_markdown()`
- Parameters passed to KIPRIS API use Python snake_case and are auto-converted to camelCase
- The `KIPRIS_API_KEY` env var is loaded via `python-dotenv`; `.env` file can be placed at project root or `src/`
