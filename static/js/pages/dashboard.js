// ==================================================
// ELEMENT REFERENCE
// ==================================================

const progressBar = document.querySelector('.progress-done');

const renewalDate = document.getElementById('renewalDate');

const tabBtns = document.querySelectorAll('.tabs .text');
const captionContent = document.querySelector('.recent-gens .body .captions');
const headlineContent = document.querySelector('.recent-gens .body .headlines');
const capCopyBtns = document.querySelectorAll('.caption .copy-btn');
const headCopyBtns = document.querySelectorAll('.headline .copy-btn');

const generationOptions = document.getElementById('generationOptions');
const usageChart = document.getElementById("usageChart").getContext('2d');

const userPrompt = document.getElementById("userPrompt");
const sendPrompt = document.getElementById("sendPrompt");
const chatsContainer = document.querySelector('.chats-container');
const chatWelcome = document.querySelector('.chat-area .h1');

const messagesArray = [
    "Ready when you are!",
    "What to build today?",
    "Let's create something amazing!",
    "Type your prompt to get started.",
    "Your AI assistant is here to help!",
    "What can I do for you today?",
];
const randomMessage = messagesArray[Math.floor(Math.random() * messagesArray.length)];

// ==================================================
// IMPORTS
// ==================================================

import { socket, sendMessage } from '../base/socket_listeners.js';
import { sendToastNotification } from '../components/toast.js';

// ==================================================
// FUNCTIONS
// ==================================================

// * FUNCTION TO CONVERT DATE STRING TO FORMATTED DATE
function formatDate() {
    const date = new Date(renewalDate.textContent);

    const formattedDate = date.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    }).replace(',', '');

    renewalDate.textContent = formattedDate;
}

// * FUNCTION TO SWITCH TABS
function switchTab(e) {
    const target = e.target.id;

    if (target === 'captionsTabBtn') {
        captionContent.style.display = 'flex';
        headlineContent.style.display = 'none';
    } else {
        captionContent.style.display = 'none';
        headlineContent.style.display = 'flex';
    }

    tabBtns.forEach(btn => {
        btn.classList.toggle('selected', btn.id === target);
    });
}

// * FUNCTION TO FETCH CURRENT USER'S MONTHLY CREDITS USAGE
async function fetchMonthlyUsage() {
    const response = await fetch('/api/user/credits/monthly-usage');
    return response.json();
}

// * FUNCTION TO RENDER USAGE CHART
async function renderUsageChart() {
    const root = document.body;
    const rootStyle = getComputedStyle(root);
    const gens = await fetchMonthlyUsage();

    const chart = new Chart(usageChart, {
        type: 'line',
        labels: gens.dates,
        data: {
            labels: gens.dates,
            datasets: [{
                label: 'Usage',
                data: gens.counts,
                fill: true,
                tension: 0.4,
                borderColor: rootStyle.getPropertyValue('--color-chart-border'),
                backgroundColor: rootStyle.getPropertyValue('--color-chart-background'),
            }]
        },
        options: {
            scales: {
                x: { grid: { display: false } },
                y: { grid: { display: false } },
            }
        }
    });
}

// * FUNCTION TO RENDER PROMPT IN CHATS-CONTAINER
function renderPrompt(prompt) {
    // CREATE PROMPT PARA ELEMENT
    const para = document.createElement('p');
    para.classList.add('prompt', 'para');
    para.textContent = prompt;

    // APPEND TO CHATS CONTAINER
    chatsContainer.appendChild(para);
}

// * FUNCTION TO HANDLE SEND-BUTTON CLICK
export function handleSendButtonClick(event, message) {
    // UPDATE SEND-BTN
    sendPrompt.disabled = true;
    sendPrompt.textContent = 'progress_activity';
    sendPrompt.classList.add('anim-rotate');

    // SEND MESSAGE TO SERVER
    sendMessage(event, message);
}

// ==================================================
// EVENT LISTENERS
// ==================================================

// & INITIAL DISPLAY SETTINGS
document.addEventListener('DOMContentLoaded', () => {
    const progressWidth = progressBar.attributes.style.value.slice(4, -2);
    if (0 <= progressWidth && progressWidth <= 33) { progressBar.style.backgroundColor = 'var(--color-state-green)'; }
    else if (33 <= progressWidth && progressWidth <= 66) { progressBar.style.backgroundColor = 'var(--color-accent-alt)'; }
    else if (66 <= progressWidth && progressWidth <= 100) { progressBar.style.backgroundColor = 'var(--color-state-red)'; }

    formatDate();

    captionContent.style.display = 'flex';
    headlineContent.style.display = 'none';

    renderUsageChart();

    chatWelcome.textContent = randomMessage;
});

// & EVENT LISTENER FOR GENERATION-OPTIONS
generationOptions.addEventListener('beforetoggle', () => {
    setTimeout(() => {
        generationOptions.classList.toggle('open');
    }, 100);
});

// & EVENT LISTENER FOR TAB-BTN CLICK
tabBtns.forEach((btn) => {
    btn.addEventListener('click', switchTab);
});

// & EVENT LISTENER FOR CAPTION COPY-BTN CLICK
capCopyBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
        const captionText = e.target.closest('.caption').querySelector('.para').textContent;
        navigator.clipboard.writeText(captionText);
        btn.textContent = 'check';
        sendToastNotification('Caption copied to clipboard!', 'check', 'var(--color-state-green)');
    });
});

// & EVENT LISTENER FOR HEADLINE COPY-BTN CLICK
headCopyBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
        const headlineText = e.target.closest('.headline').querySelector('.text').textContent;
        const headlineDesc = e.target.closest('.headline').querySelector('.mini').textContent;
        navigator.clipboard.writeText(headlineText + "\n" + headlineDesc);
        btn.textContent = 'check';
        sendToastNotification('Headline copied to clipboard!', 'check', 'var(--color-state-green)');
    });
});

// & EVENT LISTENER FOR SEND-BTN CLICK
sendPrompt.addEventListener('click', () => {
    if (userPrompt.value.trim() === '') { return };

    // REMOVE WELCOME MESSAGE FROM CHAT CONTAINER
    if (chatsContainer.contains(chatWelcome)) {
        chatWelcome.remove();
    }

    renderPrompt(userPrompt.value.trim());
    handleSendButtonClick("response-sys", userPrompt.value.trim());
    userPrompt.value = "";
});

// & EVENT LISTENER TO SEND MESSAGE ON `CTRL+ENTER` KEYPRESS
userPrompt.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        if (userPrompt.value.trim() === '' || sendPrompt.disabled) { return };

        // REMOVE WELCOME MESSAGE FROM CHAT CONTAINER
        if (chatsContainer.contains(chatWelcome)) {
            chatWelcome.remove();
        }

        renderPrompt(userPrompt.value.trim());
        handleSendButtonClick("response-sys", userPrompt.value.trim());
        userPrompt.value = "";
    }
});

// ==================================================
// SOCKET EVENTS
// ==================================================

socket.on('response-cl', (data) => {
    // UPDATE SEND-BTN
    sendPrompt.disabled = false;
    sendPrompt.textContent = 'send';
    sendPrompt.classList.remove('anim-rotate');

    // RENDER RESPONSE IN CHATS-CONTAINER
    const responsePara = document.createElement('pre');
    responsePara.classList.add('response', 'para');
    responsePara.textContent = data.response;
    chatsContainer.appendChild(responsePara);
});
