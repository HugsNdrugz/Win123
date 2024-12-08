document.addEventListener('DOMContentLoaded', () => {
    console.log('Application initialized');
    loadContent('chat'); // Load chat messages by default
    
    // Set up navigation switching
    document.querySelectorAll('.nav-button').forEach(button => {
        button.addEventListener('click', () => {
            // Update active state
            document.querySelectorAll('.nav-button').forEach(btn => 
                btn.classList.toggle('active', btn === button)
            );
            loadContent(button.dataset.tab);
        });
    });
});

async function loadContent(tabName) {
    // Update active tab
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.toggle('active', button.dataset.tab === tabName);
    });
    
    try {
        const response = await fetch(`/api/${tabName === 'chat' ? 'chat_messages' : tabName}`);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Failed to load data');
        }
        
        const contentDiv = document.getElementById('content');
        contentDiv.innerHTML = formatContent(tabName, result.data);
    } catch (error) {
        console.error(`Error loading ${tabName}:`, error);
        showError(`Failed to load ${tabName}`);
    }
}

async function loadContent(tabName) {
    // Update active state
    document.querySelectorAll('.nav-button').forEach(btn => 
        btn.classList.toggle('active', btn.dataset.tab === tabName)
    );

    const contentDiv = document.getElementById('content');
    
    if (tabName === 'chat' || tabName === 'sms') {
        try {
            const response = await fetch('/api/contacts');
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to load contacts');
            }
            
            contentDiv.innerHTML = `
                <div class="contacts-list">
                    ${result.data.map(contact => `
                        <div class="contact-item" data-contact="${contact.contact_name}">
                            <div class="contact-header">
                                <span class="contact-name">${contact.contact_name}</span>
                                <span class="contact-time">${formatDate(contact.last_time)}</span>
                            </div>
                            <div class="contact-preview">${contact.last_message}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="messages-view">
                    <div class="no-contact-selected">
                        Select a contact to view messages
                    </div>
                </div>
            `;

            // Add click handlers for contacts
            document.querySelectorAll('.contact-item').forEach(item => {
                item.addEventListener('click', () => loadMessages(item.dataset.contact));
            });
        } catch (error) {
            console.error(`Error loading ${tabName}:`, error);
            showError(`Failed to load ${tabName}`);
        }
    } else {
        contentDiv.innerHTML = `<div class="messages-view">Coming soon...</div>`;
    }
}

async function loadMessages(contact) {
    const messagesView = document.querySelector('.messages-view');
    
    // Update active contact
    document.querySelectorAll('.contact-item').forEach(item => 
        item.classList.toggle('active', item.dataset.contact === contact)
    );
    
    try {
        const response = await fetch(`/api/messages/${encodeURIComponent(contact)}`);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Failed to load messages');
        }
        
        messagesView.innerHTML = `
            <div class="messages-container">
                ${result.data.map(msg => `
                    <div class="message-item ${msg.type.toLowerCase()}">
                        <div class="message-header">
                            <strong>${msg.from_to}</strong>
                            <small>${formatDate(msg.time)}</small>
                        </div>
                        <div class="message-content">${msg.text}</div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Error loading messages:', error);
        messagesView.innerHTML = `<div class="error-message">Failed to load messages</div>`;
    }
}

function formatChatMessages(messages) {
    return `
        <div class="messages-container">
            ${messages.map(msg => `
                <div class="message-item">
                    <div class="message-header">
                        <strong>${msg.sender || 'Unknown'}</strong>
                        <small>${formatDate(msg.time)}</small>
                    </div>
                    <div class="message-content">${msg.last_message}</div>
                    <div class="message-platform">${msg.platform}</div>
                </div>
            `).join('')}
        </div>
    `;
}

function formatSMS(messages) {
    return `
        <div class="messages-container">
            ${messages.map(msg => `
                <div class="message-item ${msg.sms_type.toLowerCase()}">
                    <div class="message-header">
                        <strong>${msg.from_to || 'Unknown'}</strong>
                        <small>${formatDate(msg.time)}</small>
                    </div>
                    <div class="message-content">${msg.text}</div>
                    <div class="message-location">${msg.location || 'No location'}</div>
                </div>
            `).join('')}
        </div>
    `;
}

function formatCalls(calls) {
    return `
        <div class="calls-container">
            ${calls.map(call => `
                <div class="call-item ${call.call_type.toLowerCase()}">
                    <div class="call-header">
                        <strong>${call.from_to || 'Unknown'}</strong>
                        <small>${formatDate(call.time)}</small>
                    </div>
                    <div class="call-details">
                        <span>Duration: ${formatDuration(call.duration)}</span>
                        <span>Type: ${call.call_type}</span>
                    </div>
                    <div class="call-location">${call.location || 'No location'}</div>
                </div>
            `).join('')}
        </div>
    `;
}

function formatApps(apps) {
    return `
        <div class="apps-container">
            ${apps.map(app => `
                <div class="app-item">
                    <div class="app-header">
                        <strong>${app.application_name}</strong>
                    </div>
                    <div class="app-details">
                        <div>Package: ${app.package_name}</div>
                        <small>Installed: ${formatDate(app.install_date)}</small>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function formatDate(timestamp) {
    if (!timestamp) return 'Unknown date';
    return new Date(timestamp * 1000).toLocaleString();
}

function formatDuration(seconds) {
    if (!seconds) return 'Unknown duration';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function showError(message) {
    const contentDiv = document.getElementById('content');
    contentDiv.innerHTML = `<div class="error-message">${message}</div>`;
}
