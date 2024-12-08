const apiUrl = "http://localhost:5000"; // Base API URL for backend

// Static Data Containers
let chatsData = [];
let settingsData = {};
let archivedData = [];

// DOM Elements
const chatList = document.querySelector('#chats .chat-list');
const archivedList = document.querySelector('#archived .archived-list');
const settingsContainer = document.getElementById('settings-content');
const chatWindow = document.querySelector('.chat-window');
const sidebarItems = document.querySelectorAll('.sidebar li');
const sections = document.querySelectorAll('.section');
const searchInput = document.getElementById('search');

// Utility: Fetch data from API
async function fetchStaticData() {
  try {
    const contactsResponse = await fetch(`${apiUrl}/contacts`);
    chatsData = await contactsResponse.json();

    const settingsResponse = await fetch(`${apiUrl}/settings`);
    settingsData = await settingsResponse.json();

    const callsResponse = await fetch(`${apiUrl}/calls`);
    archivedData = await callsResponse.json();
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

// Show specific section
function showSection(sectionId) {
  sections.forEach(section => section.classList.remove('active'));
  document.getElementById(sectionId).classList.add('active');
  chatWindow.style.display = 'none'; // Hide chat window when switching sections
}

// Populate chat list
function populateChatList(data, listElement) {
  listElement.innerHTML = ''; // Clear existing items

  if (data.length === 0) {
    listElement.innerHTML = '<li class="chat-item">No chats available.</li>';
    return;
  }

  data.forEach(chat => {
    const chatItem = document.createElement('li');
    chatItem.classList.add('chat-item');
    chatItem.dataset.chatId = chat.id;
    chatItem.innerHTML = `
            <img src="${chat.avatar || 'default-avatar.png'}" alt="${chat.name}'s Avatar">
            <div class="chat-details">
                <span class="name">${chat.name}</span>
                <span class="preview">${chat.phone || ''}</span>
            </div>
        `;
    chatList.appendChild(chatItem);

    // Add click event to open chat window
    chatItem.addEventListener('click', () => {
      showMessages(chat.name);
    });
  });
}

// Show chat window with messages from database
async function showMessages(contactName) {
  const messages = await fetch(`${apiUrl}/sms/${contactName}`)
    .then(response => response.json())
    .catch(error => {
      console.error("Error fetching messages:", error);
      return [];
    });

  chatWindow.innerHTML = ''; // Clear chat window

  // Chat header
  const chatHeader = document.createElement('div');
  chatHeader.classList.add('chat-header');
  chatHeader.innerHTML = `
        <button class="back-button" onclick="showSection('chats')">&lt;</button>
        <div class="chat-header-details">
            <h3>${contactName}</h3>
        </div>
    `;
  chatWindow.appendChild(chatHeader);

  // Display messages
  if (messages.length === 0) {
    chatWindow.innerHTML += '<p>No messages available for this contact.</p>';
  } else {
    messages.forEach(msg => {
      const messageElement = document.createElement('div');
      messageElement.classList.add('message', msg.type === 'sent' ? 'sent' : 'received');
      messageElement.innerHTML = `
                <p>${msg.text}</p>
                <span class="timestamp">${msg.time}</span>
            `;
      chatWindow.appendChild(messageElement);
    });
  }

  // Show chat window and hide other sections
  chatWindow.style.display = 'flex';
  sections.forEach(section => section.classList.remove('active'));
}

// Populate settings
function populateSettings(data) {
  settingsContainer.innerHTML = `
        <img src="${data.account.avatar || 'default-avatar.png'}" alt="Profile Picture">
        <h3>${data.account.name}</h3>
        <p>Active Status: ${data.activeStatus ? 'ON' : 'OFF'}</p>
        <p>Notifications: ${data.notifications.notificationSounds ? 'ON' : 'OFF'}</p>
        <p>Dark Mode: ${data.darkMode}</p>
    `;
}

// Populate archived call history
function populateArchivedList(data) {
  archivedList.innerHTML = ''; // Clear existing items

  if (data.length === 0) {
    archivedList.innerHTML = '<li class="call-item">No call history available.</li>';
    return;
  }

  data.forEach(call => {
    const callItem = document.createElement('li');
    callItem.classList.add('call-item');
    callItem.innerHTML = `
            <span class="call-type">${call.type}</span>
            <span class="call-time">${call.time}</span>
            <span class="call-duration">${call.duration || '0'} min</span>
        `;
    archivedList.appendChild(callItem);
  });
}

// Sidebar navigation
function setupSidebar() {
  sidebarItems.forEach(item => {
    item.addEventListener('click', () => {
      const sectionId = item.dataset.section;
      showSection(sectionId);

      // Populate respective sections
      if (sectionId === 'chats') populateChatList(chatsData, chatList);
      else if (sectionId === 'archived') populateArchivedList(archivedData);
      else if (sectionId === 'settings') populateSettings(settingsData);
    });
  });
}

// Search functionality
function setupSearch() {
  searchInput.addEventListener('input', () => {
    const searchTerm = searchInput.value.toLowerCase();
    const filteredChats = chatsData.filter(chat =>
      chat.name.toLowerCase().includes(searchTerm) ||
      (chat.phone && chat.phone.toLowerCase().includes(searchTerm))
    );
    populateChatList(filteredChats, chatList);
  });
}

// Initialize Application
async function initializeApp() {
  await fetchStaticData(); // Fetch all data from backend once
  populateChatList(chatsData, chatList); // Populate contacts
  setupSidebar(); // Setup sidebar navigation
  setupSearch(); // Setup search functionality
}

// Start the app
initializeApp();