#!/usr/bin/env python3
"""
Minimal MCP Server for Claude Text Editor
"""

import asyncio
import json
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
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
                },
                {
                    "name": "wait_for_files",
                    "description": "Wait up to 30 seconds for new files to appear",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "timeout": {"type": "number", "description": "Seconds to wait (default 30)"}
                        },
                        "required": []
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
                prompt_file = Path.home() / ".claude_text_editor" / "claude_prompt.txt"
                files = list(inbox.glob("*.txt"))
                if files:
                    file = files[0]
                    content = file.read_text()
                    
                    # Read the prompt if it exists
                    prompt_text = ""
                    if prompt_file.exists():
                        prompt_text = prompt_file.read_text().strip() + "\n\n"
                    else:
                        # Use default prompt if file doesn't exist
                        prompt_text = "Process the following text according to these instructions:\n\n1. Fix any grammar or spelling errors\n2. Improve clarity and conciseness\n3. Maintain the original tone and intent\n4. Return only the processed text without explanations\n5. Please consider specific instructions at the start of the end if you see some sentences contained in parenthesis e.g. {return the text all upper case}. Otherwise ignore this point.\n\nText to process:\n\n"
                    
                    return [{"type": "text", "text": f"FILE:{file.name}\n{prompt_text}{content}"}]
                return [{"type": "text", "text": "No files in queue"}]
            
            elif name == "save_edited_text":
                outbox = Path.home() / ".claude_text_editor" / "outbox"
                outbox.mkdir(parents=True, exist_ok=True)
                filename = arguments.get("filename", "output.txt")
                content = arguments.get("content", "")
                
                # Use the same filename as input (what client expects)
                output_path = outbox / filename
                
                # Save the file
                output_path.write_text(content)
                
                # Copy to clipboard
                try:
                    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                    process.communicate(content.encode('utf-8'))
                    debug_log("Copied to clipboard")
                except Exception as e:
                    debug_log(f"Failed to copy to clipboard: {e}")
                
                # Send notification and audio feedback
                try:
                    # Use our notification script if it exists
                    notify_script = Path.home() / "claude-text-editor" / "send_notification.sh"
                    if notify_script.exists():
                        subprocess.run([str(notify_script), "Claude Text Editor", "Text edited and copied to clipboard!"], check=False)
                        debug_log("Sent notification via script")
                    else:
                        # Fallback: just play sound
                        subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], check=False)
                        debug_log("Played completion sound")
                except Exception as e:
                    debug_log(f"Failed to send feedback: {e}")
                
                # Remove original from inbox
                inbox = Path.home() / ".claude_text_editor" / "inbox"
                original = inbox / filename
                if original.exists():
                    original.unlink()
                    debug_log(f"Removed processed file: {filename}")
                
                return [{"type": "text", "text": f"Saved edited text to {filename} and copied to clipboard"}]
            
            elif name == "wait_for_files":
                timeout = arguments.get("timeout", 30) if arguments else 30
                inbox = Path.home() / ".claude_text_editor" / "inbox"
                inbox.mkdir(parents=True, exist_ok=True)
                
                start_time = time.time()
                while time.time() - start_time < timeout:
                    files = list(inbox.glob("*.txt"))
                    if files:
                        return [{"type": "text", "text": f"Files detected! Found {len(files)} files."}]
                    await asyncio.sleep(1)
                
                return [{"type": "text", "text": "No files appeared within timeout period"}]
            
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