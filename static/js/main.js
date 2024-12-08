document.addEventListener('DOMContentLoaded', () => {
    // Initial load
    loadChats();
    
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => switchTab(button.dataset.tab));
    });
});

async function loadChats() {
    try {
        const response = await fetch('/api/conversations');
        const data = await response.json();
        console.log('Received chat data:', data);
        
        const conversationsDiv = document.getElementById('conversations');
        conversationsDiv.innerHTML = data.map(chat => `
            <div class="conversation-item" onclick="loadMessages('${chat.name}')">
                <img src="${chat.avatar}" alt="avatar" style="width: 40px; height: 40px;">
                <div>
                    <strong>${chat.name}</strong>
                    <p>${chat.last_message}</p>
                    <small>${new Date(chat.time).toLocaleString()}</small>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading chats:', error);
    }
}

async function loadMessages(conversation) {
    try {
        console.log('Loading messages for:', conversation);
        const response = await fetch(`/api/messages/${encodeURIComponent(conversation)}`);
        const messages = await response.json();
        
        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = messages.map(msg => `
            <div class="message">
                <strong>${msg.sender}</strong>
                <p>${msg.text}</p>
                <small>${new Date(msg.time).toLocaleString()}</small>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function switchTab(tab) {
    // Update active tab button
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.toggle('active', button.dataset.tab === tab);
    });
    
    // Load appropriate content based on tab
    switch (tab) {
        case 'chats':
            loadChats();
            break;
        // Add other tab handlers as needed
    }
}
