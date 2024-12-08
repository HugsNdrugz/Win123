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

function formatContent(type, data) {
    switch (type) {
        case 'chat':
            return formatChatMessages(data);
        case 'sms':
            return formatSMS(data);
        case 'calls':
            return formatCalls(data);
        case 'apps':
            return formatApps(data);
        default:
            return '<p>Invalid content type</p>';
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
