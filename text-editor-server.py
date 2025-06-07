#!/usr/bin/env python3
"""
Minimal MCP Server for Claude Text Editor
"""

import asyncio
import json
import sys
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Write debug logs to stderr so they appear in Claude logs
def debug_log(msg):
    print(f"[DEBUG] {msg}", file=sys.stderr, flush=True)

class TextEditorServer:
    def __init__(self):
        debug_log("Creating server instance")
        self.server = Server("text-editor-server")
        self.setup_handlers()
        
    def setup_handlers(self):
        debug_log("Setting up handlers")
        
        @self.server.list_tools()
        async def list_tools():
            debug_log("list_tools called")
            return [
                {
                    "name": "check_edit_queue",
                    "description": "Check if there are any text files waiting to be edited",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_text_to_edit",
                    "description": "Get the next text file content that needs editing",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "save_edited_text",
                    "description": "Save the edited text to the output directory",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["filename", "content"]
                    }
                }
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict = None):
            debug_log(f"call_tool: {name} with args: {arguments}")
            
            if name == "check_edit_queue":
                inbox = Path.home() / ".claude_text_editor" / "inbox"
                inbox.mkdir(parents=True, exist_ok=True)
                files = list(inbox.glob("*.txt"))
                return [{"type": "text", "text": f"Found {len(files)} files in queue"}]
            
            elif name == "get_text_to_edit":
                inbox = Path.home() / ".claude_text_editor" / "inbox"
                files = list(inbox.glob("*.txt"))
                if files:
                    file = files[0]
                    content = file.read_text()
                    return [{"type": "text", "text": f"FILE:{file.name}\n{content}"}]
                return [{"type": "text", "text": "No files in queue"}]
            
            elif name == "save_edited_text":
                outbox = Path.home() / ".claude_text_editor" / "outbox"
                outbox.mkdir(parents=True, exist_ok=True)
                filename = arguments.get("filename", "output.txt")
                content = arguments.get("content", "")
                output_path = outbox / filename
                output_path.write_text(content)
                
                # Remove original from inbox
                inbox = Path.home() / ".claude_text_editor" / "inbox"
                original = inbox / filename
                if original.exists():
                    original.unlink()
                
                return [{"type": "text", "text": f"Saved edited text to {filename}"}]
            
            return [{"type": "text", "text": f"Unknown tool: {name}"}]
    
    async def run(self):
        debug_log("Starting server run()")
        async with stdio_server() as (read_stream, write_stream):
            debug_log("stdio_server context entered")
            
            try:
                debug_log("Creating initialization options")
                from mcp.server import InitializationOptions
                from mcp.types import ServerCapabilities, ToolsCapability
                
                capabilities = ServerCapabilities(
                    tools=ToolsCapability()
                )
                
                init_options = InitializationOptions(
                    server_name="text-editor",
                    server_version="1.0.0",
                    capabilities=capabilities
                )
                
                debug_log("Calling server.run()")
                await self.server.run(
                    read_stream,
                    write_stream,
                    initialization_options=init_options
                )
                debug_log("server.run() completed normally")
            except Exception as e:
                debug_log(f"server.run() raised exception: {e}")
                debug_log(f"Exception type: {type(e)}")
                import traceback
                debug_log(f"Traceback: {traceback.format_exc()}")
                raise

async def main():
    debug_log("Script starting")
    server = TextEditorServer()
    await server.run()
    debug_log("main() completed")

if __name__ == "__main__":
    debug_log("Starting text-editor-server-minimal")
    try:
        asyncio.run(main())
    except Exception as e:
        debug_log(f"Error: {e}")
        raise