document.addEventListener('DOMContentLoaded', function() {
    loadChats();
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

async function loadChats() {
    try {
        const response = await fetch('/api/chats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const chats = await response.json();
        if (!chats || chats.length === 0) {
            console.warn("No chat data received");
            return;
        }
        console.log("Received chat data:", chats);
        displayChats(chats);
    } catch (error) {
        console.error('Error loading chats:', error);
        // Show error message to user
        const chatList = document.querySelector('.chat-list');
        if (chatList) {
            chatList.innerHTML = '<div class="error-message">Unable to load chats. Please try again later.</div>';
        }
    }
}

function displayChats(chats) {
    const chatList = document.querySelector('.chat-list');
    if (!chatList) {
        console.error('Chat list container not found');
        return;
    }
    
    chatList.innerHTML = chats.map(chat => `
        <div class="chat-item" data-sender="${chat.name}">
            <img src="/static/images/${chat.avatar}" 
                 alt="${chat.name}'s avatar" 
                 onerror="this.src='/static/images/avatar.png'">
            <div class="chat-info">
                <h3>${chat.name}</h3>
                <p class="last-message">${chat.last_message || 'No messages'}</p>
            </div>
            ${chat.unread ? '<span class="unread-badge"></span>' : ''}
        </div>
    `).join('');

    // Add click handlers for chat items
    document.querySelectorAll('.chat-item').forEach(item => {
        item.addEventListener('click', () => {
            const sender = item.dataset.sender;
            const name = item.querySelector('h3').textContent;
            loadChatMessages(sender, name);
        });
    });
}

async function loadChatMessages(sender, contactName) {
    try {
        const chatView = document.querySelector('.chat-view');
        const chatListSection = document.querySelector('.chat-list-section');
        const contactNameElement = chatView.querySelector('.chat-contact-name');
        const messagesContainer = document.querySelector('.messages-container');
        
        if (!chatView || !chatListSection || !contactNameElement || !messagesContainer) {
            console.error('Required DOM elements not found');
            return;
        }

        // Clear previous messages
        messagesContainer.innerHTML = '';
        
        // Update contact info
        contactNameElement.textContent = contactName;
        
        // Show chat view, hide chat list
        chatListSection.style.display = 'none';
        chatView.classList.remove('hidden');
        
        const response = await fetch(`/api/messages/${encodeURIComponent(sender)}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        if (!Array.isArray(data)) {
            throw new Error('Invalid message data received');
        }
        
        displayMessages(data);
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
    
    messagesContainer.innerHTML = messages.map(message => `
        <div class="message ${message.message_type}">
            <div class="message-content">
                <p>${message.text}</p>
                <span class="message-time">${message.formatted_time}</span>
            </div>
        </div>
    `).join('');
    
    // Clear any existing scroll position and scroll to bottom after a short delay
    messagesContainer.scrollTop = 0;
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
}
