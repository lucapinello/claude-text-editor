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
        
        Args:
            text: The text to process
            timeout: Maximum time to wait for response (seconds)
        
        Returns:
            The processed text from Claude
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
    
    def show_notification(self, title: str, message: str):
        """Show macOS notification"""
        try:
            script = f'''
            display notification "{message}" with title "{title}"
            '''
            subprocess.run(['osascript', '-e', script], check=True)
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Claude Text Editor Client")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default: 30)")
    parser.add_argument("--no-clipboard", action="store_true", help="Don't copy result to clipboard")
    parser.add_argument("--no-notification", action="store_true", help="Don't show notification")
    
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
    
    # Show notification if requested
    if not args.no_notification:
        if result.startswith("Error:"):
            client.show_notification("Claude Text Editor", "Error processing text")
        else:
            client.show_notification("Claude Text Editor", "Text processed and copied to clipboard")
    
    # Exit with appropriate code
    sys.exit(0 if not result.startswith("Error:") else 1)

if __name__ == "__main__":
    main()