document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
});

function initializeChat() {
    try {
        // Initialize UI elements
        const chatView = document.getElementById('chatView');
        const chatListSection = document.getElementById('chatListSection');
        const backButton = document.getElementById('backButton');
        const chatList = document.getElementById('chatList');
        
        // Verify all required elements exist
        const requiredElements = {
            chatView,
            chatListSection,
            backButton,
            chatList
        };

        const missingElements = Object.entries(requiredElements)
            .filter(([_, element]) => !element)
            .map(([name]) => name);

        if (missingElements.length > 0) {
            throw new Error(`Missing required elements: ${missingElements.join(', ')}`);
        }

    // Setup back button
    backButton.addEventListener('click', () => {
        chatView.classList.add('hidden');
        chatListSection.style.display = 'block';
    });

    // Load initial chats
    loadChats().catch(error => {
        console.error('Failed to load initial chats:', error);
        const chatList = document.getElementById('chatList');
        if (chatList) {
            chatList.innerHTML = '<div class="error-message">Failed to load chats. Please refresh the page.</div>';
        }
    });
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
        const chatView = document.getElementById('chatView');
        const chatListSection = document.getElementById('chatListSection');
        const contactNameElement = document.getElementById('contactName');
        const messagesContainer = document.getElementById('messagesContainer');
        
        if (!chatView || !chatListSection || !contactNameElement || !messagesContainer) {
            throw new Error('Required DOM elements not found');
        }

        // Clear previous messages and show loading state
        messagesContainer.innerHTML = '<div class="loading">Loading messages...</div>';
        
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
