#!/usr/bin/env python3
"""
MCP Server for Claude Text Editor
Monitors a folder for new text files and processes them with Claude
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import time

from mcp.server import Server
from mcp.server.stdio import stdio_server

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("text-editor-server")

class TextEditorServer:
    def __init__(self):
        self.server = Server("text-editor-server")
        self.monitor_dir = Path.home() / ".claude_text_editor" / "inbox"
        self.response_dir = Path.home() / ".claude_text_editor" / "outbox"
        self.prompt_file = Path.home() / ".claude_text_editor" / "claude_prompt.txt"
        self.processed_files = set()
        self.monitoring = False
        
        # Create directories if they don't exist
        self.monitor_dir.mkdir(parents=True, exist_ok=True)
        self.response_dir.mkdir(parents=True, exist_ok=True)
        self.prompt_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create default prompt if it doesn't exist
        if not self.prompt_file.exists():
            self._create_default_prompt()
        
        # Setup handlers
        self._setup_handlers()
        
    def _create_default_prompt(self):
        """Create a default prompt file"""
        default_prompt = """Process the following text according to these instructions:

1. Fix any grammar or spelling errors
2. Improve clarity and conciseness
3. Maintain the original tone and intent
4. Return only the processed text without explanations

Text to process:
"""
        self.prompt_file.write_text(default_prompt)
        logger.info(f"Created default prompt at {self.prompt_file}")
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_resources()
        async def list_resources():
            """List available resources"""
            resources = []
            
            # Add prompt file as a resource
            if self.prompt_file.exists():
                resources.append({
                    "uri": f"file://{self.prompt_file}",
                    "name": "Claude Prompt",
                    "mimeType": "text/plain",
                    "description": "The prompt template used for processing text"
                })
            
            # Add any pending files as resources
            try:
                for file_path in self.monitor_dir.glob("*.txt"):
                    if file_path.name not in self.processed_files:
                        resources.append({
                            "uri": f"file://{file_path}",
                            "name": f"Pending: {file_path.name}",
                            "mimeType": "text/plain",
                            "description": f"Text file waiting to be processed"
                        })
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
            
            return resources
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource by URI"""
            try:
                if uri.startswith("file://"):
                    file_path = Path(uri[7:])  # Remove 'file://' prefix
                    if file_path.exists():
                        return file_path.read_text()
                    else:
                        raise ValueError(f"File not found: {file_path}")
                else:
                    raise ValueError(f"Unsupported URI scheme: {uri}")
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                raise
        
        @self.server.list_tools()
        async def list_tools():
            """List available tools"""
            return [
                {
                    "name": "process_next_file",
                    "description": "Process the next text file in the monitor folder",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "start_monitoring",
                    "description": "Start monitoring the folder for new text files",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "stop_monitoring",
                    "description": "Stop monitoring the folder",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_status",
                    "description": "Get the current monitoring status and pending files",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "update_prompt",
                    "description": "Update the Claude prompt template",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The new prompt template"
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Optional[Dict[str, Any]] = None):
            """Handle tool calls"""
            try:
                if name == "process_next_file":
                    result = await self._process_next_file()
                    return [{"type": "text", "text": result}]
                
                elif name == "start_monitoring":
                    result = await self._start_monitoring()
                    return [{"type": "text", "text": result}]
                
                elif name == "stop_monitoring":
                    result = self._stop_monitoring()
                    return [{"type": "text", "text": result}]
                
                elif name == "get_status":
                    result = self._get_status()
                    return [{"type": "text", "text": result}]
                
                elif name == "update_prompt":
                    if not arguments or "prompt" not in arguments:
                        raise ValueError("Missing 'prompt' argument")
                    result = self._update_prompt(arguments["prompt"])
                    return [{"type": "text", "text": result}]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [{"type": "text", "text": f"Error: {str(e)}"}]
    
    async def _process_next_file(self) -> str:
        """Process the next available text file"""
        try:
            # Find the oldest unprocessed file
            pending_files = []
            for file_path in self.monitor_dir.glob("*.txt"):
                if file_path.name not in self.processed_files:
                    # Get file creation time
                    stat = file_path.stat()
                    pending_files.append((stat.st_mtime, file_path))
            
            if not pending_files:
                return "No files to process"
            
            # Sort by creation time and get the oldest
            pending_files.sort(key=lambda x: x[0])
            _, file_path = pending_files[0]
            
            # Read the file content
            try:
                content = file_path.read_text()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                self.processed_files.add(file_path.name)
                return f"Error reading file: {str(e)}"
            
            # Read the prompt template
            try:
                prompt_template = self.prompt_file.read_text()
            except Exception as e:
                logger.error(f"Error reading prompt: {e}")
                prompt_template = "Process this text:\n"
            
            # Combine prompt and content
            full_prompt = prompt_template + "\n" + content
            
            # Create response file name (same as input but in response directory)
            response_file = self.response_dir / f"response_{file_path.stem}_{int(time.time())}.txt"
            
            # Mark as processed
            self.processed_files.add(file_path.name)
            
            # Remove the original file
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"Error removing file {file_path}: {e}")
            
            # Return the prompt for Claude to process
            return f"PROCESS_FILE:{response_file.name}\n{full_prompt}"
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return f"Error: {str(e)}"
    
    async def _start_monitoring(self) -> str:
        """Start monitoring the folder"""
        if self.monitoring:
            return "Already monitoring"
        
        self.monitoring = True
        
        # Start the monitoring task
        asyncio.create_task(self._monitor_folder())
        
        return f"Started monitoring {self.monitor_dir}"
    
    def _stop_monitoring(self) -> str:
        """Stop monitoring the folder"""
        if not self.monitoring:
            return "Not currently monitoring"
        
        self.monitoring = False
        return "Stopped monitoring"
    
    def _get_status(self) -> str:
        """Get current status"""
        try:
            pending_files = []
            for file_path in self.monitor_dir.glob("*.txt"):
                if file_path.name not in self.processed_files:
                    pending_files.append(file_path.name)
            
            status = {
                "monitoring": self.monitoring,
                "monitor_dir": str(self.monitor_dir),
                "response_dir": str(self.response_dir),
                "pending_files": pending_files,
                "processed_count": len(self.processed_files)
            }
            
            return json.dumps(status, indent=2)
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return f"Error: {str(e)}"
    
    def _update_prompt(self, new_prompt: str) -> str:
        """Update the prompt template"""
        try:
            self.prompt_file.write_text(new_prompt)
            return "Prompt updated successfully"
        except Exception as e:
            logger.error(f"Error updating prompt: {e}")
            return f"Error: {str(e)}"
    
    async def _monitor_folder(self):
        """Monitor folder for new files"""
        logger.info(f"Started monitoring {self.monitor_dir}")
        
        while self.monitoring:
            try:
                # Check for new files
                for file_path in self.monitor_dir.glob("*.txt"):
                    if file_path.name not in self.processed_files:
                        logger.info(f"Found new file: {file_path.name}")
                        # Auto-process the file
                        result = await self._process_next_file()
                        logger.info(f"Processed file with result: {result[:100]}...")
                
                # Wait before checking again
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error
        
        logger.info("Stopped monitoring")
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                None  # initialization_options
            )

async def main():
    """Main entry point"""
    server = TextEditorServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)