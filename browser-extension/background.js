// Background script to handle keyboard shortcuts
chrome.commands.onCommand.addListener((command) => {
  if (command === "edit-with-claude") {
    // Get the active tab
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      // Send message to content script
      chrome.tabs.sendMessage(tabs[0].id, {action: "getSelectedText"}, (response) => {
        if (response && response.text) {
          // Send to native app via Native Messaging
          // For now, copy to clipboard as workaround
          copyToClipboard(response.text);
          
          // Show notification
          chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icon.png',
            title: 'Claude Text Editor',
            message: 'Text copied! Use ⌥⌘. in any native app to edit.'
          });
        }
      });
    });
  }
});

function copyToClipboard(text) {
  // Create textarea and copy
  const textarea = document.createElement('textarea');
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
}