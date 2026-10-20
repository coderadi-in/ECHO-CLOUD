// ==================================================
// ELEMENT REFERENCE
// ==================================================

const cards = document.querySelectorAll('.card');

const outputFrame = document.querySelector('.output-frame');
const copyBtn = document.getElementById('copyBtn');
const closeFrameBtn = document.getElementById('closeFrame');
const lines = document.querySelectorAll('.output-frame .line');
let clearAnimation;

const outputHeadline = document.getElementById('outputHeadline');
const outputDesc = document.getElementById('outputDesc');

const titleInput = document.getElementsByName('title')[0];
const priceInput = document.getElementsByName('price')[0];
const descInput = document.getElementsByName('desc')[0];

const sendBtn = document.getElementById('sendBtn');
const colors = [ '#F6DECBA0', '#FCC5D2A0', '#DFDDE3A0', '#CCF5F5A0', '#C2EDFFA0' ];

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
function applyRandomBackgroundColor() {
    cards.forEach(card => {
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        card.style.backgroundColor = randomColor;
    });
}

// * FUNCTION TO COPY OUTPUT RESPONSE TO CLIPBOARD
function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
}

// * FUNCTION TO CLOSE OUTPUT FRAME
function closeOutputFrame() {
    outputFrame.style.opacity = '0';
    setTimeout(() => { outputFrame.style.display = 'none'; }, 500);
}

// * FUNCTION TO HANDLE SEND-BUTTON CLICK
function handleSendButtonClick(event, message, referred=false) {
    // DATA VALIDATION
    if (!referred) {
        if (titleInput.value.trim() === '' || priceInput.value.trim() === '' || descInput.value.trim() === '') {
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
function resetPromptArea() {
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
        handleSendButtonClick('headlines-sys', message, true);
        localStorage.removeItem("pending_generation");
    }
}

// * FUNCTION TO DISPLAY GENERATION SKELETON
function showGenSkeleton() {
    outputFrame.style.display = 'flex';
    lines.forEach(line => { line.style.display = 'inline-block'; });
    outputHeadline.style.display = 'none';
    outputDesc.style.display = 'none';
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
        outputHeadline.style.display = 'inline-block';
        outputDesc.style.display = 'inline-block';

        lines.forEach(line => {
            document.querySelector('.output-frame .head .fs-24').style.display = 'none';
            line.style.display = 'none';
            clearInterval(intervalId);
        })
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
    copyToClipboard(outputHeadline.textContent + "\n" + outputDesc.textContent);
    copyBtn.textContent = 'check';
    sendToastNotification('Headline copied to clipboard!', 'check', 'var(--color-state-green)');
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
    }

    handleSendButtonClick("headlines-sys", message);
});

// ==================================================
// SOCKET EVENTS
// ==================================================

// | EVENT FOR RECEIVING NEW HEADLINE
socket.on('headlines-cl', (data) => {
    clearAnimation();
    
    try {
        outputHeadline.textContent = data.headline;
        outputDesc.textContent = data.desc;    
    } catch (error) {
        outputHeadline.textContent = "Generation Error";
        outputDesc.textContent = data;
    }

    resetPromptArea();
    sendToastNotification('Headline generated successfully!', 'thumb_up', 'var(--color-state-green)');
    showNotification('Headline generated successfully!', 'Your headline has been generated and is ready to use.', 'headline-gen', '/app/headlines');
});