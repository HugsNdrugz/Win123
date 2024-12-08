document.addEventListener('DOMContentLoaded', () => {
    console.log('Application initialized');
    loadContacts(); // Load contacts by default

    // Set up navigation handling
    const navigationBar = document.querySelector('md-navigation-bar');
    navigationBar.addEventListener('click', (event) => {
        const tab = event.target.closest('md-navigation-tab');
        if (tab) {
            const section = tab.getAttribute('data-tab');
            loadSection(section);
        }
    });
});

async function loadSection(section) {
    const contentDiv = document.getElementById('content');

    switch(section) {
        case 'chat':
        case 'sms':
            await loadContacts(section);
            break;
        case 'calls':
            await loadCalls();
            break;
        case 'apps':
            await loadApps();
            break;
    }
}

async function loadContacts(type = 'chat') {
    try {
        const response = await fetch('/api/contacts');
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to load contacts');
        }

        const contactList = document.querySelector('.contact-list');
        contactList.innerHTML = result.data
            .filter(contact => type === 'chat' ? contact.type === 'Chat' : contact.type === 'SMS')
            .map(contact => `
                <div class="contact-card" data-contact="${contact.contact_name}">
                    <div class="contact-header">
                        <span class="contact-name">${contact.contact_name}</span>
                        <span class="contact-time">${formatDate(contact.last_time)}</span>
                    </div>
                    <div class="contact-preview">${contact.last_message || ''}</div>
                </div>
            `).join('');

        // Add click handlers for contact cards
        document.querySelectorAll('.contact-card').forEach(card => {
            card.addEventListener('click', () => loadMessages(card.dataset.contact));
        });
    } catch (error) {
        console.error('Error loading contacts:', error);
        showError('Failed to load contacts');
    }
}

async function loadMessages(contact) {
    try {
        const response = await fetch(`/api/messages/${encodeURIComponent(contact)}`);
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to load messages');
        }

        const messagesPanel = document.querySelector('.messages-panel');
        messagesPanel.innerHTML = `
            <div class="messages-container">
                ${result.data.map(msg => `
                    <div class="message-bubble ${msg.from_to === contact ? '' : 'outgoing'}">
                        <div class="message-content">${msg.text}</div>
                        <div class="message-time">${formatDate(msg.time)}</div>
                    </div>
                `).join('')}
            </div>
        `;

        // Update mobile view
        document.querySelector('.conversations-view').classList.add('showing-messages');

        // Scroll to bottom of messages
        const container = messagesPanel.querySelector('.messages-container');
        container.scrollTop = container.scrollHeight;
    } catch (error) {
        console.error('Error loading messages:', error);
        showError('Failed to load messages');
    }
}

function formatDate(timestamp) {
    if (!timestamp) return '';

    const date = new Date(timestamp * 1000);
    const now = new Date();
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);

    // Format based on how recent the message is
    if (isSameDay(date, now)) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (isSameDay(date, yesterday)) {
        return 'Yesterday';
    } else if (now.getFullYear() === date.getFullYear()) {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
    return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
}

function isSameDay(d1, d2) {
    return d1.getFullYear() === d2.getFullYear() &&
           d1.getMonth() === d2.getMonth() &&
           d1.getDate() === d2.getDate();
}

function showError(message) {
    const contentDiv = document.getElementById('content');
    contentDiv.innerHTML = `
        <div class="error-message">
            <span class="material-icons">error</span>
            <p>${message}</p>
        </div>
    `;
}

async function loadCalls() {
    //Implementation for loadCalls would go here.  This is omitted from both original and edited code.
}

async function loadApps() {
    //Implementation for loadApps would go here. This is omitted from both original and edited code.
}