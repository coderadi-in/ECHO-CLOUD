// ==================================================
// ELEMENT REFERENCE
// ==================================================

const cards = document.querySelectorAll('.card');

const outputFrame = document.querySelector('.output-frame');
const copyBtn = document.getElementById('copyBtn');
const closeFrameBtn = document.getElementById('closeFrame');
const outputResponse = document.getElementById('outputResponse');
const lines = document.querySelectorAll('.output-frame .line');
let clearAnimation;

const titleInput = document.getElementsByName('title')[0];
const priceInput = document.getElementsByName('price')[0];
const descInput = document.getElementsByName('desc')[0];

const sendBtn = document.getElementById('sendBtn');
const colors = ['#F6DECBA0', '#FCC5D2A0', '#DFDDE3A0', '#CCF5F5A0', '#C2EDFFA0'];

// ==================================================
// IMPORTS
// ==================================================

import { socket, sendMessage } from '../base/socket_listeners.js';
import { sendToastNotification } from '../components/toast.js';
import { showNotification } from '../base/notifications.js';

// ==================================================
// FUNCTIONS
// ==================================================

// * FUNCTION TO APPLY RANDOM BACKGROUND COLOR TO EACH CARD
export function applyRandomBackgroundColor() {
    cards.forEach(card => {
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        card.style.backgroundColor = randomColor;
    });
}

// * FUNCTION TO COPY OUTPUT RESPONSE TO CLIPBOARD
export function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
}

// * FUNCTION TO CLOSE OUTPUT FRAME
export function closeOutputFrame() {
    outputFrame.style.opacity = '0';
    setTimeout(() => { outputFrame.style.display = 'none'; }, 500);
}

// * FUNCTION TO HANDLE SEND-BUTTON CLICK
export function handleSendButtonClick(event, message, referred=false) {
    // DATA VALIDATION
    if (!referred) {
        if (titleInput.value.trim() === '' || descInput.value.trim() === '') {
            sendBtn.disabled = false;
            sendBtn.textContent = 'send';
            sendBtn.classList.remove('anim-rotate');
            return;
        }
    }

    showGenSkeleton();
    clearAnimation = animateGenSkeleton();

    // UPDATE SEND-BTN
    sendBtn.disabled = true;
    sendBtn.textContent = 'progress_activity';
    sendBtn.classList.add('anim-rotate');

    // SEND MESSAGE TO SERVER
    sendMessage(event, message);
}

// * FUNCTION TO RESET PROMPT AREA
export function resetPromptArea() {
    // CLEAR INPUT FIELDS
    titleInput.value = '';
    priceInput.value = '';
    descInput.value = '';

    // UPDATE SEND-BTN
    sendBtn.disabled = false;
    sendBtn.textContent = 'send';
    sendBtn.classList.remove('anim-rotate');

    setTimeout(() => { outputFrame.style.opacity = '1'; }, 100);
}

// * FUNCTION TO SEND GENERATION REQUEST TO SERVER IF URL HAS GENERATION PARAMETER
function sendGenParam() {
    const urlParams = new URLSearchParams(window.location.search);
    const refer = urlParams.get("refer");

    if (refer === 'store') {
        const productData = JSON.parse(localStorage.getItem("pending_generation"));
        const message = {
            title: productData.title,
            price: productData.price,
            desc: productData.desc
        };
        handleSendButtonClick('captions-sys', message, true);
        localStorage.removeItem("pending_generation");
    }
}

// * FUNCTION TO DISPLAY GENERATION SKELETON
function showGenSkeleton() {
    outputFrame.style.display = 'flex';
    outputResponse.style.display = "none";
    lines.forEach(line => { line.style.display = 'inline-block'; });
    copyBtn.textContent = "content_copy";
    copyBtn.style.display = "none";
    closeFrameBtn.style.display = "none";

    setTimeout(() => { outputFrame.style.opacity = '1'; }, 100);
}

// * FUNCTION TO ANIMATE GENERATION SKELETON
function animateGenSkeleton() {
    const intervalId = setInterval(() => {
        lines.forEach(line => {
            const lineWidth = Math.floor(Math.random() * (80 - 20 + 1)) + 20;
            line.style.width = `${lineWidth}%`;
        })
    }, 600);

    return () => {
        copyBtn.style.display = "inline";
        closeFrameBtn.style.display = "inline";
        outputResponse.style.display = "inline-block";

        lines.forEach(line => {
            document.querySelector('.output-frame .head .fs-24').style.display = 'none';
            line.style.display = 'none';
            clearInterval(intervalId);
        });
    }
}

// ==================================================
// EVENT LISTENERS
// ==================================================

// & EVENT LISTENER FOR DOM-CONTENT-LOAD
document.addEventListener('DOMContentLoaded', () => {
    applyRandomBackgroundColor();
    sendGenParam();
});

// & EVENT LISTENER FOR COPY-BUTTON CLICK
copyBtn.addEventListener('click', () => {
    copyToClipboard(outputResponse.textContent);
    copyBtn.textContent = 'check';
    sendToastNotification('Caption copied to clipboard!', 'check', 'var(--color-state-green)');
});

// & EVENT LISTENER FOR CLOSE-FRAME-BUTTON CLICK
closeFrameBtn.addEventListener('click', closeOutputFrame);

// & EVENT LISTENER FOR SEND-BUTTON CLICK
sendBtn.addEventListener('click', () => {    
    // CREATE MESSAGE OBJECT
    const message = {
        title: titleInput.value.trim(),
        price: priceInput.value.trim(),
        desc: descInput.value.trim()
    };

    handleSendButtonClick('captions-sys', message);
});

// ==================================================
// SOCKET EVENTS
// ==================================================

// | EVENT FOR RECEIVING NEW CAPTION
socket.on('captions-cl', (data) => {
    outputResponse.textContent = data;
    clearAnimation();
    resetPromptArea();
    sendToastNotification('Caption generated successfully!', 'thumb_up', 'var(--color-state-green)');
    showNotification('Caption generated successfully!', 'Your caption has been generated and is ready to use.', 'caption-gen', '/app/captions');
});
