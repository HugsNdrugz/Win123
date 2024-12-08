document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    setupBackButton();
});

function setupBackButton() {
    const backButton = document.querySelector('.back-button');
    if (backButton) {
        backButton.addEventListener('click', () => {
            const chatView = document.querySelector('.chat-view');
            const chatListSection = document.querySelector('.chat-list-section');
            
            chatView.classList.add('hidden');
            chatListSection.style.display = 'block';
        });
    }
}

async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const conversations = await response.json();
        if (!conversations || conversations.length === 0) {
            console.warn("No conversations data received");
            return;
        }
        console.log("Received conversations data:", conversations);
        displayChats(conversations);
    } catch (error) {
        console.error('Error loading conversations:', error);
        const chatList = document.querySelector('.chat-list');
        if (chatList) {
            chatList.innerHTML = '<div class="error-message">Unable to load conversations. Please try again later.</div>';
        }
    }
}

function displayChats(conversations) {
    const chatList = document.querySelector('.chat-list');
    if (!chatList) {
        console.error('Chat list container not found');
        return;
    }
    
    chatList.innerHTML = conversations.map(chat => `
        <div class="chat-item" data-sender="${chat.sender}">
            <img src="/static/images/avatar.png" 
                 alt="${chat.sender}'s avatar">
            <div class="chat-info">
                <h3>${chat.sender}</h3>
                <p class="last-message">${chat.last_message || 'No messages'}</p>
                <small>${new Date(chat.time).toLocaleString()}</small>
            </div>
        </div>
    `).join('');

    document.querySelectorAll('.chat-item').forEach(item => {
        item.addEventListener('click', () => {
            const sender = item.dataset.sender;
            loadChatMessages(sender, sender);
        });
    });
}

async function loadChatMessages(sender, contactName) {
    if (!sender) {
        console.error('No sender provided to loadChatMessages');
        return;
    }

    try {
        const chatView = document.querySelector('.chat-view');
        const chatListSection = document.querySelector('.chat-list-section');
        const contactNameElement = chatView.querySelector('.chat-contact-name');
        const messagesContainer = document.querySelector('.messages-container');
        
        console.log('Loading messages for:', sender);
        
        // Update contact info
        contactNameElement.textContent = contactName;
        
        // Show chat view, hide chat list
        chatListSection.style.display = 'none';
        chatView.classList.remove('hidden');
        
        // Show loading state
        messagesContainer.innerHTML = '<div class="loading">Loading messages...</div>';
        
        const response = await fetch(`/api/messages/${encodeURIComponent(sender)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const messages = await response.json();
        console.log('Received messages:', messages);
        
        if (!Array.isArray(messages)) {
            throw new TypeError('Expected messages to be an array');
        }
        
        if (messages.length === 0) {
            messagesContainer.innerHTML = '<div class="no-messages">No messages found</div>';
            return;
        }
        
        displayMessages(messages);
    } catch (error) {
        console.error('Error loading messages:', error);
        const messagesContainer = document.querySelector('.messages-container');
        if (messagesContainer) {
            messagesContainer.innerHTML = '<div class="error-message">Failed to load messages. Please try again.</div>';
        }
    }
}

function displayMessages(messages) {
    const messagesContainer = document.querySelector('.messages-container');
    if (!messagesContainer) {
        console.error('Messages container not found');
        return;
    }
    
    const formatTime = (timeStr) => {
        if (!timeStr) return '';
        try {
            const date = new Date(timeStr);
            return isNaN(date.getTime()) ? timeStr : date.toLocaleString();
        } catch (e) {
            console.warn('Error formatting time:', e);
            return timeStr;
        }
    };

    messagesContainer.innerHTML = messages.map(message => {
        const messageType = message.type === 'SMS' ? 
            (message.sender === 'Sent' ? 'sent' : 'received') : 
            'chat';
            
        return `
            <div class="message ${messageType}">
                <div class="message-content">
                    <p>${message.text || ''}</p>
                    <span class="message-time">${formatTime(message.time)}</span>
                    ${message.location ? `<small class="location">(${message.location})</small>` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
