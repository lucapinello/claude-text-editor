#!/bin/bash
# Claude Text Editor - Installation Script

echo "Installing Claude Text Editor..."

# Check for conda/mamba
USE_CONDA=false
CONDA_CMD=""

if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
    USE_CONDA=true
    echo "Found mamba, will use it to create environment"
elif command -v conda &> /dev/null; then
    CONDA_CMD="conda"
    USE_CONDA=true
    echo "Found conda, will use it to create environment"
else
    # Check for Python 3.10 or newer
    PYTHON_CMD=""
    for cmd in python3.12 python3.11 python3.10 python3; do
        if command -v $cmd &> /dev/null; then
            VERSION=$($cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
            MAJOR=$(echo $VERSION | cut -d. -f1)
            MINOR=$(echo $VERSION | cut -d. -f2)
            if [ $MAJOR -eq 3 ] && [ $MINOR -ge 10 ]; then
                PYTHON_CMD=$cmd
                echo "Found suitable Python: $cmd (version $VERSION)"
                break
            fi
        fi
    done

    if [ -z "$PYTHON_CMD" ]; then
        echo "Error: Python 3.10 or newer is required for MCP."
        echo "Your current Python 3 version is too old."
        echo ""
        echo "Please install Python 3.10+ using one of these methods:"
        echo "  - Install mamba: curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
        echo "  - Homebrew: brew install python@3.11"
        echo "  - Download from: https://www.python.org/downloads/"
        exit 1
    fi
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create directories
mkdir -p ~/claude-text-editor
mkdir -p ~/.claude_text_editor/inbox
mkdir -p ~/.claude_text_editor/outbox

# Copy files to installation directory
echo "Copying files..."
cp "$SCRIPT_DIR/text-editor-server.py" ~/claude-text-editor/
cp "$SCRIPT_DIR/claude_text_client.py" ~/claude-text-editor/
cp "$SCRIPT_DIR/claude_text_shortcut.sh" ~/claude-text-editor/
cp "$SCRIPT_DIR/environment.yml" ~/claude-text-editor/
if [ -f "$SCRIPT_DIR/send_notification.sh" ]; then
    cp "$SCRIPT_DIR/send_notification.sh" ~/claude-text-editor/
    chmod +x ~/claude-text-editor/send_notification.sh
fi
chmod +x ~/claude-text-editor/claude_text_client.py
chmod +x ~/claude-text-editor/claude_text_shortcut.sh

# Create default prompt if it doesn't exist
if [ ! -f ~/.claude_text_editor/claude_prompt.txt ]; then
    cat > ~/.claude_text_editor/claude_prompt.txt << 'EOL'
Process the following text according to these instructions:

1. Fix any grammar or spelling errors
2. Improve clarity and conciseness
3. Maintain the original tone and intent
4. Return only the processed text without explanations

Text to process:
EOL
    echo "Created default prompt at ~/.claude_text_editor/claude_prompt.txt"
fi

# Create environment
cd ~/claude-text-editor

if [ "$USE_CONDA" = true ]; then
    # Check if environment already exists
    if $CONDA_CMD env list | grep -q "claude-text-editor"; then
        echo "Environment claude-text-editor already exists"
        echo "Updating environment from environment.yml..."
        $CONDA_CMD env update -f "$SCRIPT_DIR/environment.yml" --prune
    else
        # Create conda environment from environment.yml
        echo "Creating conda environment from environment.yml..."
        $CONDA_CMD env create -f "$SCRIPT_DIR/environment.yml"
    fi
    
    # Activate conda environment
    eval "$($CONDA_CMD shell.bash hook)"
    $CONDA_CMD activate claude-text-editor
else
    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    source venv/bin/activate
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install mcp watchdog
fi

# Create MCP server wrapper for the appropriate environment
if [ "$USE_CONDA" = true ]; then
    # Find the full path to conda/mamba
    CONDA_FULL_PATH=$(which $CONDA_CMD)
    CONDA_BASE_DIR=$(dirname $(dirname $CONDA_FULL_PATH))
    
    cat > ~/claude-text-editor/mcp-server-wrapper.sh << EOL
#!/bin/bash
# Initialize conda/mamba for bash
export PATH="$CONDA_BASE_DIR/condabin:\$PATH"
eval "\$($CONDA_BASE_DIR/bin/conda shell.bash hook)"
conda activate claude-text-editor
python ~/claude-text-editor/text-editor-server.py
EOL
else
    cat > ~/claude-text-editor/mcp-server-wrapper.sh << 'EOL'
#!/bin/bash
source ~/claude-text-editor/venv/bin/activate
python ~/claude-text-editor/text-editor-server.py
EOL
fi

chmod +x ~/claude-text-editor/mcp-server-wrapper.sh

# Configure Claude Desktop
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

mkdir -p "$CLAUDE_CONFIG_DIR"

if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "Backing up existing Claude config..."
    cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create or update Claude config
cat > "$CLAUDE_CONFIG_FILE" << EOL
{
  "mcpServers": {
    "text-editor": {
      "command": "/bin/bash",
      "args": ["${HOME}/claude-text-editor/mcp-server-wrapper.sh"]
    }
  }
}
EOL

# Clean up old files if they exist
echo "Cleaning up old files..."
rm -f ~/claude-text-editor/claude-text-editor.py 2>/dev/null
rm -f ~/claude-text-editor/claude-edit-*.sh 2>/dev/null
rm -f ~/claude-text-editor/test-*.py 2>/dev/null
rm -f /usr/local/bin/claude-edit 2>/dev/null
rm -rf ~/.claude-text-editor 2>/dev/null  # Remove old dot directory

echo ""
echo "✅ Installation complete!"
echo ""

# Install terminal-notifier for notifications
echo "Checking for terminal-notifier..."
if ! command -v terminal-notifier &> /dev/null; then
    if command -v brew &> /dev/null; then
        echo "Installing terminal-notifier for desktop notifications..."
        brew install terminal-notifier
        echo "✓ terminal-notifier installed successfully"
    else
        echo "Note: Homebrew not found. For desktop notifications, install terminal-notifier:"
        echo "  1. Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "  2. Then run: brew install terminal-notifier"
        echo "  (The app will still work with audio feedback only)"
    fi
else
    echo "✓ terminal-notifier is already installed"
fi

echo "Next steps:"
echo "1. Restart Claude Desktop app"
echo "2. In Claude Desktop, ask Claude to 'check the edit queue and process any waiting files'"
echo "3. Create the macOS shortcut (see README.md for instructions)"
echo ""
echo "Configuration file: ~/.claude_text_editor/claude_prompt.txt"
echo "Installation directory: ~/claude-text-editor/"