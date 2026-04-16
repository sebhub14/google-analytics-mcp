#!/usr/bin/env python
# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Entry point for the Google Analytics MCP server."""
import asyncio
import os
import analytics_mcp.coordinator as coordinator
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn

def run_server():
    """Runs the MCP server over streamable HTTP."""
    session_manager = StreamableHTTPSessionManager(
        app=coordinator.app,
        event_store=None,
        json_response=False,
    )

    async def handle_streamable_http(scope, receive, send):
        await session_manager.handle_request(scope, receive, send)

    async def lifespan(app):
        async with session_manager.run():
            yield

    starlette_app = Starlette(
        lifespan=lifespan,
        routes=[Mount("/mcp", app=handle_streamable_http)],
    )

    host = os.environ.get("FASTMCP_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(starlette_app, host=host, port=port)

if __name__ == "__main__":
    run_server()
