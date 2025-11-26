const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// Generate or retrieve session ID
let sessionId = localStorage.getItem('rti_session_id');
if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('rti_session_id', sessionId);
}

function appendMessage(content, isUser = false) {
    const wrapperDiv = document.createElement('div');
    wrapperDiv.className = `flex items-start gap-4 ${isUser ? 'justify-end' : ''} mb-6`;

    // Avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = `flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-slate-200 order-2' : 'bg-blue-100'}`;
    avatarDiv.innerHTML = `<span class="material-icons text-sm ${isUser ? 'text-slate-600' : 'text-blue-600'}">${isUser ? 'person' : 'smart_toy'}</span>`;

    // Message Bubble
    const contentDiv = document.createElement('div');
    // User: Blue bubble, White text. AI: White card, Dark text, Shadow.
    contentDiv.className = `${isUser ? 'bg-blue-600 text-white' : 'bg-white text-slate-800 border border-slate-100'} rounded-2xl p-5 max-w-2xl shadow-sm ${isUser ? 'order-1' : ''}`;

    const textP = document.createElement('div');
    // Add 'prose' class for Markdown styling in AI messages
    textP.className = isUser ? 'text-sm leading-relaxed' : 'prose prose-slate prose-sm max-w-none leading-relaxed';

    if (isUser) {
        textP.textContent = content;
    } else {
        // Parse Markdown for bot responses
        textP.innerHTML = marked.parse(content);
    }

    contentDiv.appendChild(textP);
    wrapperDiv.appendChild(avatarDiv);
    wrapperDiv.appendChild(contentDiv);
    messagesContainer.appendChild(wrapperDiv);

    // Scroll to bottom
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

    // Add user message
    appendMessage(message, true);
    userInput.value = '';

    // Show loading
    appendLoading();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });

        const data = await response.json();
        removeLoading();

        if (response.ok) {
            appendMessage(data.reply);

            // If there's a draft, show a download button (simplified for now)
            if (data.rti_draft) {
                const draftDiv = document.createElement('div');
                draftDiv.className = 'flex flex-col items-center justify-center pt-4 text-center space-y-6';
                draftDiv.innerHTML = `
                    <div class="bg-white dark:bg-slate-700 rounded-lg p-4 max-w-lg shadow-sm text-left w-full">
                        <h3 class="font-bold mb-2">RTI Draft Generated</h3>
                        <pre class="whitespace-pre-wrap text-xs bg-slate-100 dark:bg-slate-800 p-2 rounded">${data.rti_draft}</pre>
                    </div>
                    <button onclick="downloadDraft(this)" data-draft="${encodeURIComponent(data.rti_draft)}" class="bg-primary hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-full inline-flex items-center gap-2 transition-colors shadow-lg cursor-pointer">
                        <span class="material-icons">download</span>
                        Download Draft
                    </button>
                `;
                messagesContainer.appendChild(draftDiv);
            }
        } else {
            appendMessage("Sorry, something went wrong. Please try again.");
        }
    } catch (error) {
        removeLoading();
        appendMessage("Error connecting to the server.");
        console.error(error);
    }
}

// Handle Enter key
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

// Download helper
window.downloadDraft = function (btn) {
    const text = decodeURIComponent(btn.getAttribute('data-draft'));
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'RTI_Draft.txt';
    a.click();
    window.URL.revokeObjectURL(url);
};
