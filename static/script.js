// Initialize feather icons
document.addEventListener('DOMContentLoaded', function() {
    feather.replace();
    loadChats();
});

async function loadChats() {
    try {
        const response = await fetch('/api/chats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const chats = await response.json();
        displayChats(chats);
    } catch (error) {
        console.error('Error loading chats:', error);
    }
}

function displayChats(chats) {
    const chatList = document.querySelector('.chat-list');
    chatList.innerHTML = chats.map(chat => `
        <div class="chat-item" data-conversation-id="${chat.conversation_id}">
            <img src="${chat.avatar}" 
                 alt="${chat.name}'s avatar" 
                 onerror="this.src='/static/images/avatar.png'; this.classList.add('error');">
            <div class="chat-info">
                <h3>${chat.name}</h3>
                <p>${chat.last_message || 'No messages yet'}</p>
                ${chat.unread ? '<span class="unread-badge"></span>' : ''}
            </div>
        </div>
    `).join('');

    // Add click handlers for chat items
    document.querySelectorAll('.chat-item').forEach(item => {
        item.addEventListener('click', () => {
            const conversationId = item.dataset.conversationId;
            loadChatMessages(conversationId);
            // Mark as read
            item.querySelector('.unread-badge')?.remove();
        });
    });
}

function switchSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.remove('hidden');
    
    // Update active state in sidebar
    document.querySelectorAll('.sidebar li').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === sectionId) {
            item.classList.add('active');
        }
    });
}

// Add click handlers for sidebar items
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.sidebar li').forEach(item => {
        item.addEventListener('click', () => {
            const section = item.dataset.section;
            switchSection(section);
        });
    });
});

async function loadChatMessages(conversationId) {
    try {
        const response = await fetch(`/api/messages/${conversationId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const messages = await response.json();
        displayMessages(messages, conversationId);
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function displayMessages(messages, conversationId) {
    const chatSection = document.getElementById('chats');
    const messageContainer = document.createElement('div');
    messageContainer.className = 'message-container';
    
    messageContainer.innerHTML = messages.map(message => `
        <div class="message ${message.sender === 'user' ? 'sent' : 'received'}">
            <div class="message-content">
                <p>${message.text}</p>
                <span class="message-time">${message.time}</span>
            </div>
        </div>
    `).join('');
    
    // Clear previous messages if any
    const existingContainer = chatSection.querySelector('.message-container');
    if (existingContainer) {
        existingContainer.remove();
    }
    
    chatSection.appendChild(messageContainer);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

const handleSearch = debounce((event) => {
    const searchTerm = event.target.value.toLowerCase();
    const chatItems = document.querySelectorAll('.chat-item');
    
    chatItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(searchTerm) ? 'flex' : 'none';
    });
}, 300);

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
});

function closeSettings() {
    switchSection('chats');
}
