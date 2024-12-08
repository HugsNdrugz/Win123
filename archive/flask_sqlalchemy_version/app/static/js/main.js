document.addEventListener('DOMContentLoaded', () => {
    loadChats();
});

async function loadChats() {
    try {
        const response = await fetch('/api/conversations');
        const data = await response.json();
        console.log("Received conversations data:", data);
        displayChats(data);
    } catch (error) {
        console.error("Error loading chats:", error);
    }
}

async function loadMessages(sender) {
    try {
        console.log("Loading messages for:", sender);
        if (!sender) return;
        
        const response = await fetch(`/api/messages/${encodeURIComponent(sender)}`);
        const messages = await response.json();
        displayMessages(messages);
    } catch (error) {
        console.error("Error loading messages:", error);
    }
}

function displayChats(chats) {
    const sidebar = document.querySelector('.sidebar');
    sidebar.innerHTML = '<h2>Conversations</h2>';
    const chatList = document.createElement('ul');
    chatList.className = 'chat-list';
    
    chats.forEach(chat => {
        const chatItem = document.createElement('li');
        chatItem.className = 'chat-item';
        chatItem.innerHTML = `
            <img src="${chat.avatar}" alt="Avatar" class="avatar">
            <div class="chat-info">
                <h3>${chat.sender}</h3>
                <p>${chat.text}</p>
                <span class="time">${new Date(chat.time).toLocaleString()}</span>
            </div>
        `;
        chatItem.addEventListener('click', () => loadMessages(chat.sender));
        chatList.appendChild(chatItem);
    });
    
    sidebar.appendChild(chatList);
}

function displayMessages(messages) {
    const chatArea = document.querySelector('.chat-area');
    chatArea.innerHTML = '<div class="messages"></div>';
    const messagesDiv = chatArea.querySelector('.messages');
    
    messages.forEach(message => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.type.toLowerCase()}`;
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${message.text}</p>
                <span class="time">${new Date(message.time).toLocaleString()}</span>
            </div>
        `;
        messagesDiv.appendChild(messageDiv);
    });
}
