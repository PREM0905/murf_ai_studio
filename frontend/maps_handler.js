// frontend/maps_handler.js

function handleMapsResponse(response) {
    /**
     * Handle maps-related responses and auto-redirect to Google Maps
     */
    
    // Check if response contains a Google Maps URL
    const urlPattern = /https:\/\/www\.google\.com\/maps[^\s]*/;
    const match = response.match(urlPattern);
    
    if (match) {
        const mapsUrl = match[0];
        
        // Show confirmation dialog
        const userConfirm = confirm(
            `Would you like to open Google Maps for real-time navigation?\n\n` +
            `Click OK to open maps, or Cancel to stay here.`
        );
        
        if (userConfirm) {
            // Open Google Maps in new tab
            window.open(mapsUrl, '_blank');
            
            // Update the response to show it opened
            return response.replace(mapsUrl, '[Google Maps opened in new tab]');
        }
    }
    
    return response;
}

function createMapsButton(mapsUrl, buttonText = "Open in Google Maps") {
    /**
     * Create a clickable button for maps URLs
     */
    const button = document.createElement('button');
    button.textContent = buttonText;
    button.style.cssText = `
        background: #4285f4;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        margin: 5px 0;
        font-size: 14px;
    `;
    
    button.onclick = function() {
        window.open(mapsUrl, '_blank');
    };
    
    return button;
}

function enhanceMapMessages() {
    /**
     * Enhance messages with maps functionality
     */
    const messages = document.querySelectorAll('.message.msg-bot');
    
    messages.forEach(message => {
        const text = message.textContent;
        const urlPattern = /https:\/\/www\.google\.com\/maps[^\s]*/;
        const match = text.match(urlPattern);
        
        if (match) {
            const mapsUrl = match[0];
            
            // Create button
            const button = createMapsButton(mapsUrl);
            
            // Replace URL with button
            message.innerHTML = text.replace(mapsUrl, '');
            message.appendChild(document.createElement('br'));
            message.appendChild(button);
        }
    });
}

// Auto-enhance messages when they're added
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
            enhanceMapMessages();
        }
    });
});

// Start observing when page loads
document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.getElementById('messages');
    if (messagesContainer) {
        observer.observe(messagesContainer, { childList: true });
    }
});