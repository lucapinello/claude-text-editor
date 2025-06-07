# Claude Text Editor

A seamless text editing system that integrates with Claude Desktop through the Model Context Protocol (MCP). Select text anywhere on macOS, send it to Claude for editing, and automatically receive the edited version.

## Features

- 🚀 **Zero-friction editing**: Select text → Right-click → "Edit with Claude" → Get edited text
- 📁 **File-based processing**: No timeouts, no focus switching required
- 🔄 **Automatic queue management**: Drop files in inbox, get results in outbox
- 🎯 **Customizable prompts**: Define your editing instructions in `claude_prompt.txt`
- 🖥️ **System-wide integration**: Works with any macOS application
- 🤖 **MCP-powered**: Native integration with Claude Desktop

## Prerequisites

- macOS (tested on macOS 14.x)
- Claude Desktop app installed
- Terminal access
- Internet connection

## Installation

### Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/lucapinello/claude-text-editor.git
cd claude-text-editor

# Run the install script
./install.sh
```

The install script will:
- Check for Python/conda/mamba
- Create the necessary directories
- Set up the Python environment
- Install dependencies
- Configure Claude Desktop
- Copy all files to the correct locations

### Manual Installation

If you prefer to install manually or the script doesn't work for your setup:

#### Step 1: Install Miniforge (Python Environment Manager)

```bash
# Download and install Miniforge
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
bash Miniforge3-MacOSX-arm64.sh -b -p ~/miniforge3

# Initialize conda for your shell
~/miniforge3/bin/conda init bash
~/miniforge3/bin/conda init zsh

# Restart your terminal or source your shell config
source ~/.zshrc  # or ~/.bash_profile
```

### Step 2: Create Project Directory and Download Files

```bash
# Create project directory
mkdir -p ~/Projects/claudetext
cd ~/Projects/claudetext

# Create the installation directory
mkdir -p ~/claude-text-editor
```

### Step 3: Create the MCP Server File

Create `~/claude-text-editor/text-editor-server-minimal.py`:

```python
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
```

### Step 4: Create the Wrapper Script

Create `~/claude-text-editor/mcp-server-wrapper.sh`:

```bash
#!/bin/bash
# Initialize conda/mamba for bash
export PATH="$HOME/miniforge3/condabin:$PATH"
eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
conda activate claude-text-editor
python ~/claude-text-editor/text-editor-server-minimal.py
```

Make it executable:
```bash
chmod +x ~/claude-text-editor/mcp-server-wrapper.sh
```

### Step 5: Create Conda Environment and Install Dependencies

```bash
# Create conda environment
conda create -n claude-text-editor python=3.11 -y

# Activate the environment
conda activate claude-text-editor

# Install MCP SDK
pip install mcp
```

### Step 6: Configure Claude Desktop

Create or edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "text-editor": {
      "command": "/bin/bash",
      "args": ["/Users/YOUR_USERNAME/claude-text-editor/mcp-server-wrapper.sh"]
    }
  }
}
```

**IMPORTANT**: Replace `YOUR_USERNAME` with your actual macOS username. You can find it by running:
```bash
echo $USER
```

### Step 7: Create Working Directories

```bash
# Create directories for text processing
mkdir -p ~/.claude_text_editor/inbox
mkdir -p ~/.claude_text_editor/outbox

# Create default prompt file
cat > ~/.claude_text_editor/claude_prompt.txt << 'EOF'
Please edit the following text according to these instructions:
1. Fix any grammar or spelling errors
2. Improve clarity and conciseness
3. Maintain the original tone and intent
4. Return only the edited text without explanations

Text to edit:
EOF
```

### Step 8: Create the Client Script (Optional)

Create `~/claude-text-editor/claude_text_client.py` for command-line usage:

```python
#!/usr/bin/env python3
"""
Claude Text Editor Client
Drops text files in monitored folder and watches for responses
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("claude_text_client")

class ClaudeTextClient:
    def __init__(self):
        self.inbox_dir = Path.home() / ".claude_text_editor" / "inbox"
        self.outbox_dir = Path.home() / ".claude_text_editor" / "outbox"
        
        # Create directories if they don't exist
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
    
    def process_text(self, text: str, timeout: int = 30) -> str:
        """
        Process text by dropping it in the monitored folder and waiting for response
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        input_filename = f"text_{timestamp}.txt"
        input_path = self.inbox_dir / input_filename
        
        # Write text to inbox
        logger.info(f"Writing text to {input_path}")
        try:
            input_path.write_text(text)
        except Exception as e:
            logger.error(f"Failed to write input file: {e}")
            return f"Error: Failed to write input file: {e}"
        
        # Expected response file pattern
        response_pattern = f"response_text_{timestamp}_*.txt"
        
        # Wait for response
        logger.info("Waiting for Claude to process...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check for response files
            response_files = list(self.outbox_dir.glob(response_pattern))
            
            if response_files:
                # Found response file
                response_file = response_files[0]
                logger.info(f"Found response: {response_file}")
                
                try:
                    # Read response
                    response_text = response_file.read_text()
                    
                    # Clean up response file
                    response_file.unlink()
                    logger.info("Response file cleaned up")
                    
                    return response_text
                    
                except Exception as e:
                    logger.error(f"Error reading response: {e}")
                    return f"Error: Failed to read response: {e}"
            
            # Wait a bit before checking again
            time.sleep(0.5)
        
        # Timeout reached
        logger.warning(f"Timeout waiting for response after {timeout} seconds")
        
        # Clean up input file if it still exists
        if input_path.exists():
            try:
                input_path.unlink()
            except:
                pass
        
        return "Error: Timeout waiting for Claude response"
    
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            logger.info("Text copied to clipboard")
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Claude Text Editor Client")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default: 30)")
    parser.add_argument("--no-clipboard", action="store_true", help="Don't copy result to clipboard")
    
    args = parser.parse_args()
    
    # Read text from stdin
    try:
        text = sys.stdin.read()
        if not text.strip():
            print("Error: No text provided", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create client and process text
    client = ClaudeTextClient()
    result = client.process_text(text, timeout=args.timeout)
    
    # Output result
    print(result)
    
    # Copy to clipboard if requested
    if not args.no_clipboard and not result.startswith("Error:"):
        client.copy_to_clipboard(result)
    
    # Exit with appropriate code
    sys.exit(0 if not result.startswith("Error:") else 1)

if __name__ == "__main__":
    main()
```

Make it executable:
```bash
chmod +x ~/claude-text-editor/claude_text_client.py
```

### Step 9: Test the Installation

1. **Restart Claude Desktop**:
   ```bash
   osascript -e 'tell application "Claude" to quit'
   sleep 2
   open -a "Claude"
   ```

2. **Check the server logs**:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp-server-text-editor.log
   ```

   You should see messages like:
   ```
   [DEBUG] Starting text-editor-server-minimal
   [DEBUG] Script starting
   [DEBUG] Creating server instance
   [DEBUG] Setting up handlers
   [DEBUG] Starting server run()
   ```

3. **Test with a file**:
   ```bash
   echo "Please make this sentence more professional." > ~/.claude_text_editor/inbox/test.txt
   ```

4. **In Claude Desktop**, type:
   ```
   Please check the edit queue and process any waiting files.
   ```

## Usage

### Basic Workflow

1. **Drop files in the inbox**: Place `.txt` files in `~/.claude_text_editor/inbox/`
2. **Use Claude Desktop**: Ask Claude to check the edit queue and process files
3. **Find results**: Edited files appear in `~/.claude_text_editor/outbox/`

### Using the Client Script

```bash
# Edit text from clipboard
pbpaste | ~/claude-text-editor/claude_text_client.py

# Edit text from a file
cat myfile.txt | ~/claude-text-editor/claude_text_client.py

# Edit with custom timeout
echo "Edit this text" | ~/claude-text-editor/claude_text_client.py --timeout 60

# Edit without copying to clipboard
echo "Edit this text" | ~/claude-text-editor/claude_text_client.py --no-clipboard
```

### Customizing Edit Instructions

Edit `~/.claude_text_editor/claude_prompt.txt` to change how Claude processes your text:

```text
Please edit the following text to:
- Make it more formal and professional
- Fix any technical inaccuracies
- Add relevant examples where appropriate

Text to edit:
```

### Creating a macOS Service for System-Wide Text Editing

#### Step 1: Create the Shortcut Script

Create `~/claude-text-editor/claude_text_shortcut.sh`:

```bash
#!/bin/bash
# Read input text
INPUT=$(cat)

# Generate timestamp for unique filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S_%N)
FILENAME="text_${TIMESTAMP}.txt"

# Write to inbox
echo "$INPUT" > "$HOME/.claude_text_editor/inbox/$FILENAME"

# Notify user
osascript -e 'display notification "Text sent to Claude for editing" with title "Claude Text Editor"'
```

Make it executable:
```bash
chmod +x ~/claude-text-editor/claude_text_shortcut.sh
```

#### Step 2: Create macOS Shortcut

1. Open **Shortcuts** app
2. Click **+** to create new shortcut
3. Add these actions:
   - **Receive Text**: From "Quick Actions"
   - **Run Shell Script**: 
     - Shell: `/bin/bash`
     - Pass Input: "to stdin"
     - Script: `~/claude-text-editor/claude_text_shortcut.sh`
4. Settings (⚙️):
   - ✅ Use as Quick Action
   - ✅ Services Menu
   - Name: "Edit with Claude"

#### Step 3: Add Keyboard Shortcut

1. System Settings → Keyboard → Keyboard Shortcuts → Services
2. Find "Edit with Claude" under "Text"
3. Add shortcut: ⌘⇧E (or your preference)

#### Step 4: Start Monitoring in Claude Desktop

1. Open Claude Desktop
2. Create/open a chat
3. Type: `Please check the edit queue and process any waiting files`

Now you can select text anywhere → ⌘⇧E → Claude processes it → Find result in `~/.claude_text_editor/outbox/`

## Architecture

The system consists of several components:

- **MCP Server** (`text-editor-server-minimal.py`): Integrates with Claude Desktop
- **File Monitor**: Watches `~/.claude_text_editor/inbox/` for new files
- **Client Script** (`claude_text_client.py`): Command-line interface for text editing
- **Wrapper Script** (`mcp-server-wrapper.sh`): Manages Python environment

### File Flow

```
User Input → inbox/ → Claude processes → outbox/ → User receives output
```

## Troubleshooting

### Server won't connect
1. Check the logs: `tail -100 ~/Library/Logs/Claude/mcp-server-text-editor.log`
2. Verify conda environment: `conda activate claude-text-editor && which python`
3. Test the server directly: `~/claude-text-editor/mcp-server-wrapper.sh`

### Tools not available in Claude Desktop
1. Ensure Claude Desktop was restarted after configuration
2. Check that the config file path is correct for your username
3. Verify the wrapper script is executable
4. Look for error messages in the logs

### Permission errors
```bash
chmod +x ~/claude-text-editor/mcp-server-wrapper.sh
chmod +x ~/claude-text-editor/claude_text_client.py
```

### Python or module not found
1. Ensure conda is properly initialized in your shell
2. Verify the environment is activated: `conda activate claude-text-editor`
3. Check that MCP is installed: `pip list | grep mcp`

## Development

### Project Structure
```
~/claude-text-editor/
├── text-editor-server-minimal.py    # MCP server implementation
├── mcp-server-wrapper.sh           # Environment wrapper
├── claude_text_client.py           # Command-line client
└── ~/.claude_text_editor/
    ├── inbox/                      # Drop text files here
    ├── outbox/                     # Receive edited files here
    └── claude_prompt.txt           # Editing instructions
```

### Extending the System

You can extend the system by:
1. Adding new tools to the MCP server
2. Creating additional client scripts for specific workflows
3. Integrating with other applications via AppleScript or shell scripts

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Powered by [Claude Desktop](https://claude.ai/)
- Python environment management by [Miniforge](https://github.com/conda-forge/miniforge)