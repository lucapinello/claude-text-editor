// Content script for Google Docs
console.log("Claude Text Editor Helper loaded");

// Listen for our custom keyboard shortcut
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getSelectedText") {
    // Try multiple methods to get selected text
    let selectedText = "";
    
    // Method 1: Standard selection
    selectedText = window.getSelection().toString();
    
    // Method 2: If no selection, try to get from active element
    if (!selectedText && document.activeElement) {
      const elem = document.activeElement;
      if (elem.selectionStart !== undefined) {
        selectedText = elem.value.substring(elem.selectionStart, elem.selectionEnd);
      }
    }
    
    // Method 3: Google Docs specific (uses clipboard)
    if (!selectedText) {
      // Copy to clipboard first
      document.execCommand('copy');
      
      // Read from clipboard
      navigator.clipboard.readText().then(text => {
        sendResponse({text: text});
      }).catch(err => {
        sendResponse({text: "", error: "Could not read clipboard"});
      });
      
      return true; // Will respond asynchronously
    }
    
    sendResponse({text: selectedText});
  }
});