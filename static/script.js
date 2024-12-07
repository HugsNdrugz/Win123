document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    feather.replace();

    // Navigation handling
    const sidebarItems = document.querySelectorAll('.sidebar li');
    sidebarItems.forEach(item => {
        item.addEventListener('click', () => {
            const section = item.dataset.section;
            switchSection(section);
        });
    });

    // Initial data load
    loadChats();
    
    // Search functionality
    const searchInput = document.getElementById('search');
    searchInput.addEventListener('input', debounce(handleSearch, 300));
});

function switchSection(sectionId) {
    // Remove active class from all sections and sidebar items
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
        section.classList.add('hidden');
    });
    document.querySelectorAll('.sidebar li').forEach(item => {
        item.classList.remove('active');
    });

    // Add active class to selected section and sidebar item
    document.getElementById(sectionId).classList.remove('hidden');
    document.getElementById(sectionId).classList.add('active');
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
}

async function loadChats() {
    try {
        const response = await fetch('/api/chats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const chats = await response.json();
        console.log('Received chat data:', chats);
        if (chats && chats.length > 0) {
            displayChats(chats);
        } else {
            console.warn('No chat data received');
            document.querySelector('.chat-list').innerHTML = '<p>No chats available</p>';
        }
    } catch (error) {
        console.error('Error loading chats:', error);
        document.querySelector('.chat-list').innerHTML = '<p>Error loading chats</p>';
    }
}

function displayChats(chats) {
    const chatList = document.querySelector('.chat-list');
    chatList.innerHTML = chats.map(chat => `
        <div class="chat-item" data-conversation-id="${chat.conversation_id}">
            <div class="chat-avatar">
                <img src="${chat.avatar}" alt="Chat Avatar">
            </div>
            <div class="chat-info">
                <h3>${chat.name}</h3>
                <p>${chat.last_message || 'No messages yet'}</p>
                <span class="chat-time">${chat.last_message_time || ''}</span>
                ${chat.unread ? '<span class="unread-badge"></span>' : ''}
            </div>
        </div>
    `).join('');

    // Add click handlers for chat items
    document.querySelectorAll('.chat-item').forEach(item => {
        item.addEventListener('click', () => {
            const conversationId = item.dataset.conversationId;
            loadChatMessages(conversationId);
        });
    });
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

function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const chatItems = document.querySelectorAll('.chat-item');
    
    chatItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(searchTerm) ? 'flex' : 'none';
    });
}

function closeSettings() {
    switchSection('chats');
}
