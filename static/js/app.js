const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const historyList = document.getElementById('history-list');
const newChatBtn = document.getElementById('new-chat-btn');

let currentSessionId = null;

// --- Session Management ---

function getSessions() {
    const sessions = localStorage.getItem('rti_sessions');
    return sessions ? JSON.parse(sessions) : [];
}

function saveSession(id, title = "New Chat") {
    let sessions = getSessions();
    // Check if exists
    const existing = sessions.find(s => s.id === id);
    if (!existing) {
        sessions.push({ id, title, timestamp: Date.now() });
        localStorage.setItem('rti_sessions', JSON.stringify(sessions));
    }
}

function createNewChat() {
    const id = crypto.randomUUID();
    saveSession(id);
    loadSession(id);
}

function renderHistory() {
    const sessions = getSessions();
    const now = Date.now();
    const oneDay = 24 * 60 * 60 * 1000;

    // Filter for last 24 hours
    const recentSessions = sessions.filter(s => (now - s.timestamp) < oneDay).sort((a, b) => b.timestamp - a.timestamp);

    historyList.innerHTML = '';

    if (recentSessions.length === 0) {
        historyList.innerHTML = '<div class="text-center text-gray-400 text-sm mt-4">No recent chats</div>';
        return;
    }

    recentSessions.forEach(session => {
        const div = document.createElement('div');
        div.className = `p-2 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-slate-700 text-sm truncate ${session.id === currentSessionId ? 'bg-blue-50 dark:bg-slate-700 text-primary font-medium' : 'text-gray-600 dark:text-gray-300'}`;
        div.textContent = session.title; // Could use timestamp or first message as title later
        div.onclick = () => loadSession(session.id);

        // Format time
        const timeSpan = document.createElement('span');
        timeSpan.className = 'block text-xs text-gray-400';
        const date = new Date(session.timestamp);
        timeSpan.textContent = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        div.appendChild(timeSpan);

        historyList.appendChild(div);
    });
}

async function loadSession(id) {
    currentSessionId = id;
    localStorage.setItem('rti_current_session_id', id);

    // Clear messages (except welcome if needed, but easier to clear all and re-fetch)
    messagesContainer.innerHTML = '';

    // Add Welcome Message
    appendWelcomeMessage();

    // Fetch History
    try {
        const response = await fetch(`/chat/${id}/history`);
        if (response.ok) {
            const history = await response.json();
            history.forEach(msg => {
                appendMessage(msg.content, msg.role === 'user');
            });
        }
    } catch (e) {
        console.error("Failed to load history", e);
    }

    renderHistory(); // Update active state
}

function appendWelcomeMessage() {
    const wrapperDiv = document.createElement('div');
    wrapperDiv.className = 'flex items-start gap-4 mb-6';
    wrapperDiv.innerHTML = `
        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <span class="material-icons text-blue-600 text-sm">smart_toy</span>
        </div>
        <div class="bg-white dark:bg-slate-700 rounded-2xl p-5 max-w-2xl shadow-sm border border-slate-100">
            <p class="text-slate-800 dark:text-slate-200 leading-relaxed">
                Hello! I am RTI Assist AI. I can help you with legal advice regarding RTI.
            </p>
        </div>
    `;
    messagesContainer.appendChild(wrapperDiv);
}

// --- Chat Logic ---

function appendMessage(content, isUser = false) {
    const wrapperDiv = document.createElement('div');
    wrapperDiv.className = `flex items-start gap-4 ${isUser ? 'justify-end' : ''} mb-6`;

    // Avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = `flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-slate-200 order-2' : 'bg-blue-100'}`;
    avatarDiv.innerHTML = `<span class="material-icons text-sm ${isUser ? 'text-slate-600' : 'text-blue-600'}">${isUser ? 'person' : 'smart_toy'}</span>`;

    // Message Bubble
    const contentDiv = document.createElement('div');
    contentDiv.className = `${isUser ? 'bg-blue-600 text-white' : 'bg-white text-slate-800 border border-slate-100'} rounded-2xl p-5 max-w-2xl shadow-sm ${isUser ? 'order-1' : ''}`;

    const textP = document.createElement('div');
    textP.className = isUser ? 'text-sm leading-relaxed' : 'prose prose-slate prose-sm max-w-none leading-relaxed';

    if (isUser) {
        textP.textContent = content;
    } else {
        textP.innerHTML = marked.parse(content);
    }

    contentDiv.appendChild(textP);
    wrapperDiv.appendChild(avatarDiv);
    wrapperDiv.appendChild(contentDiv);
    messagesContainer.appendChild(wrapperDiv);

    const main = document.getElementById('chat-container');
    main.scrollTop = main.scrollHeight;
}

function appendLoading() {
    const wrapperDiv = document.createElement('div');
    wrapperDiv.id = 'loading-indicator';
    wrapperDiv.className = 'flex items-start gap-4 mb-6';
    wrapperDiv.innerHTML = `
        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <span class="material-icons text-blue-600 text-sm">smart_toy</span>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
            <div class="flex space-x-2">
                <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(wrapperDiv);
    const main = document.getElementById('chat-container');
    main.scrollTop = main.scrollHeight;
}

function removeLoading() {
    const loader = document.getElementById('loading-indicator');
    if (loader) loader.remove();
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    if (!currentSessionId) createNewChat();

    appendMessage(message, true);
    userInput.value = '';
    appendLoading();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, session_id: currentSessionId })
        });

        const data = await response.json();
        removeLoading();

        if (response.ok) {
            appendMessage(data.reply);

            // Update session title if it's "New Chat"
            let sessions = getSessions();
            let session = sessions.find(s => s.id === currentSessionId);
            if (session && session.title === "New Chat") {
                session.title = message.substring(0, 30) + (message.length > 30 ? "..." : "");
                localStorage.setItem('rti_sessions', JSON.stringify(sessions));
                renderHistory();
            }
        } else {
            appendMessage("Sorry, something went wrong.");
        }
    } catch (error) {
        removeLoading();
        appendMessage("Error connecting to server.");
    }
}

// --- Initialization ---

// Event Listeners
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
sendBtn.addEventListener('click', sendMessage);
if (newChatBtn) newChatBtn.addEventListener('click', createNewChat);

// Init
const savedId = localStorage.getItem('rti_current_session_id');
if (savedId) {
    loadSession(savedId);
} else {
    createNewChat();
}
renderHistory();
