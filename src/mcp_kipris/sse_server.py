import argparse
import datetime
import logging
import os
import sys
from collections.abc import Sequence
from typing import List

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.tools import (
    ForeignPatentApplicantSearchTool,
    ForeignPatentApplicationNumberSearchTool,
    ForeignPatentFreeSearchTool,
    ForeignPatentInternationalApplicationNumberSearchTool,
    ForeignPatentInternationalOpenNumberSearchTool,
    KoreanPatentApplicantSearchTool,
    KoreanPatentApplicationNumberSearchTool,
    KoreanPatentDetailSearchTool,
    KoreanPatentFreeSearchTool,
    KoreanPatentRighterSearchTool,
    KoreanPatentSearchTool,
    KoreanPatentSummarySearchTool,
)

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")

app = Server("mcp-kipris")

tool_handlers = {}


def add_tool_handler(tool_class: ToolHandler):
    global tool_handlers

    tool_handlers[tool_class.name] = tool_class
    logger.info(f"Tool handler added: {tool_class.name}")


def get_tool_handler(name: str) -> ToolHandler | None:
    logger.info(f"Tool handler find: {name}")
    if name not in tool_handlers:
        return None
    logger.info(f"Tool handler found: {name}")
    return tool_handlers[name]


add_tool_handler(KoreanPatentApplicantSearchTool())
add_tool_handler(KoreanPatentSearchTool())
add_tool_handler(KoreanPatentRighterSearchTool())
add_tool_handler(KoreanPatentApplicationNumberSearchTool())
add_tool_handler(KoreanPatentSummarySearchTool())
add_tool_handler(KoreanPatentDetailSearchTool())
add_tool_handler(KoreanPatentFreeSearchTool())
add_tool_handler(ForeignPatentApplicantSearchTool())
add_tool_handler(ForeignPatentApplicationNumberSearchTool())
add_tool_handler(ForeignPatentFreeSearchTool())
add_tool_handler(ForeignPatentInternationalApplicationNumberSearchTool())
add_tool_handler(ForeignPatentInternationalOpenNumberSearchTool())


@app.list_tools()
async def list_tools() -> list[Tool]:
    logger.info(f"Tool handler list: {tool_handlers.values()}")
    return [tool.get_tool_description() for tool in tool_handlers.values()]


@app.call_tool()
async def call_tool(tool_name: str, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for command line run."""
    if not isinstance(args, dict):
        raise RuntimeError("arguments must be dictionary")

    tool_handler = get_tool_handler(tool_name)
    if not tool_handler:
        raise ValueError(f"Unknown tool: {tool_name}")

    try:
        # 비동기 메서드(run_tool_async)를 사용하여 타임아웃 및 응답 시간 개선
        logger.info(f"비동기 실행 시작: {tool_name}")
        start_time = datetime.datetime.now()

        try:
            # 먼저 비동기 메서드 시도
            result = await tool_handler.run_tool_async(args)
        except (AttributeError, NotImplementedError) as e:
            # 비동기 메서드가 없거나 구현되지 않은 경우 동기 메서드로 폴백
            logger.warning(f"비동기 메서드 실패, 동기 메서드로 폴백: {str(e)}")
            result = tool_handler.run_tool(args)

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        logger.info(f"도구 실행 완료: {tool_name}, 소요시간: {elapsed_time:.2f}초")

        return result
    except Exception as e:
        logger.error(f"도구 실행 중 오류 발생: {str(e)}")
        raise RuntimeError(f"Caught Exception. Error: {str(e)}")


def tool_to_dict(tool: Tool) -> dict:
    """Tool 객체를 dictionary로 변환"""
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema,
        "output_schema": tool.outputSchema if hasattr(tool, "outputSchema") else None,
        "metadata": tool.metadata if hasattr(tool, "metadata") else None,
    }


def content_to_dict(content: TextContent | ImageContent | EmbeddedResource) -> dict:
    """Content 객체를 dictionary로 변환"""
    if isinstance(content, TextContent):
        return {
            "type": "text",
            "text": content.text,
            "metadata": content.metadata if hasattr(content, "metadata") else None,
        }
    elif isinstance(content, ImageContent):
        return {
            "type": "image",
            "url": content.url,
            "metadata": content.metadata if hasattr(content, "metadata") else None,
        }
    elif isinstance(content, EmbeddedResource):
        return {
            "type": "embedded",
            "url": content.url,
            "metadata": content.metadata if hasattr(content, "metadata") else None,
        }
    else:
        raise ValueError(f"Unknown content type: {type(content)}")


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        try:
            logger.info("🔗 [SSE] New connection request received")
            async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
                logger.info("✅ [SSE] Connected, running MCP server...")
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
                logger.info("🔥 MCP server run() completed")
            logger.info("🔌 [SSE] Disconnected cleanly")
            return Response(status_code=204)
        except Exception as e:
            logger.error(f"❌ [SSE] Connection error: {str(e)}")
            return Response(status_code=500)

    async def list_tools(request: Request) -> JSONResponse:
        """도구 목록을 JSON 형식으로 반환하는 엔드포인트"""
        tools = [tool.get_tool_description() for tool in tool_handlers.values()]
        tool_dicts = [tool_to_dict(tool) for tool in tools]
        return JSONResponse(tool_dicts)

    async def handle_post_message(request: Request) -> Response:
        """메시지를 처리하는 엔드포인트"""
        try:
            body = await request.json()
            logger.debug(f"Received message: {body}")

            if not isinstance(body, dict):
                logger.error(f"Message is not a dictionary: {body}")
                return Response(status_code=400, content="Message must be a dictionary")

            message_type = body.get("type")
            if message_type != "tool":
                logger.error(f"Invalid message type: {message_type}")
                return Response(status_code=400, content="Invalid message type")

            tool_name = body.get("name")
            if not tool_name:
                logger.error("Tool name is missing")
                return Response(status_code=400, content="Tool name is required")

            args = body.get("args", {})
            if not isinstance(args, dict):
                logger.error(f"Arguments must be a dictionary: {args}")
                return Response(status_code=400, content="Arguments must be a dictionary")

            logger.info(f"Processing tool call: {tool_name} with args: {args}")
            result = await call_tool(tool_name, args)
            result_dicts = [content_to_dict(content) for content in result]
            return JSONResponse(result_dicts)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return Response(status_code=500, content=f"Error: {str(e)}")

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse/", endpoint=handle_sse),
            Route("/tools", endpoint=list_tools),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true", help="Run in HTTP mode")
    parser.add_argument("--port", type=int, default=6274, help="Port to listen on (default: 6274)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    args = parser.parse_args()

    logger.info(f"🚀 argparse received: {args}")

    if args.http:
        logger.info(f"Starting MCP KIPRIS HTTP server on {args.host}:{args.port}...")
        try:
            logger.info("🌐 Starting MCP KIPRIS SSE server...")
            starlette_app = create_starlette_app(app, debug=True)
            config = uvicorn.Config(app=starlette_app, host=args.host, port=args.port)
            server = uvicorn.Server(config=config)
            await server.serve()

        except Exception as e:
            logger.error(f"SSE server error occurred: {str(e)}")
            raise RuntimeError(f"SSE Server Error: {str(e)}")
    else:
        logger.info("Starting MCP KIPRIS stdio server...")
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("stdio_server initialized")
                init_options = app.create_initialization_options()
                logger.info(f"Initialization options created: {init_options}")
                await app.run(read_stream, write_stream, init_options)
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            raise RuntimeError(f"Caught Exception. Error: {str(e)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
