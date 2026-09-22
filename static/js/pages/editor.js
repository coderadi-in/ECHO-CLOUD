// ==================================================
// ELEMENT REFERENCE
// ==================================================

const imagePreview = document.getElementById('imagePreview');
const textPreview = document.getElementById('textPreview');
const postHeadline = document.getElementById('postHeadline');
const postDescription = document.getElementById('postDescription');

const imageInput = document.getElementById('photoInput');
const clearCanvasBtn = document.getElementById('clearCanvas');
const increaseTextWidthBtn = document.getElementById('increaseWidth');
const decreaseTextWidthBtn = document.getElementById('decreaseWidth');
const headlineColorInput = document.querySelector('#headlineColor input');
const headlineColorSymbol = document.querySelector('#headlineColor .symbol');
const exportBtn = document.getElementById('exportBtn');

const addBtns = document.querySelectorAll('.add-btn');
const headGenBtns = document.querySelectorAll('.head-gen-btn');

const canvas = document.querySelector('.canvas');
const generateTab = document.querySelector('.generate');
const historyTab = document.querySelector('.history');

const outputFrame = document.querySelector('.output-frame');
const closeFrameBtn = document.getElementById('closeFrame');
const keepBtn = document.getElementById('keepBtn');
const regenBtn = document.getElementById('regenBtn');
const lines = document.querySelectorAll('.output-frame .line');

const outputHeadline = document.getElementById('outputHeadline');
const outputDesc = document.getElementById('outputDesc');

const toggleHistoryTab = document.querySelectorAll('.toggleHistoryTab');
const toggleGenerationTab = document.querySelectorAll('.toggleGenerationTab');

const promptTrigger = document.getElementById('customPrompt');
const promptArea = document.getElementById('promptArea');
const customProductTitle = document.querySelector('.prompt-inputs input');
const customProductDesc = document.querySelector('.prompt-inputs textarea');
const customProductSend = document.getElementById('sendBtn');

// ==================================================
// STATES
// ==================================================

let intervalId = null;
let clearAnimation;
let cachedData;

// ==================================================
// IMPORTS
// ==================================================

import { socket, sendMessage } from '../base/socket_listeners.js';
import { sendToastNotification } from '../components/toast.js';

// ==================================================
// FUNCTIONS
// ==================================================

// * FUNCTION TO GET SCALE FACTOR
function getScaleFactor(targetWidth, targetHeight, baseWidth, baseHeight) {
    // Calculate scale needed to reach target dimensions
    const scaleX = targetWidth / baseWidth;
    const scaleY = targetHeight / baseHeight;
    // Use the smaller scale to maintain aspect ratio
    return Math.min(scaleX, scaleY);
}

// * FUNCTION TO ADD EVENT LISTENER FOR TOGGLING TABS
function toggleTabListener(triggers, tab) {
    triggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            tab.classList.toggle('active');
        });
    });
}

// * FUNCTION TO DISPLAY GENERATION SKELETON
function showGenSkeleton() {
    outputFrame.style.display = 'flex';
    setTimeout(() => { outputFrame.style.opacity = '1'; }, 100);
}

// * FUNCTION TO ANIMATE GENERATION SKELETON
function animateGenSkeleton() {
    generateTab.style.opacity = "0.6";
    generateTab.style.cursor = "wait";
    generateTab.style.pointerEvents = "none";
    historyTab.style.opacity = "0.6";
    historyTab.style.cursor = "wait";
    historyTab.style.pointerEvents = "none";
    
    closeFrameBtn.style.visibility = 'hidden';
    keepBtn.style.visibility = 'hidden';
    regenBtn.style.visibility = 'hidden';

    const intervalId = setInterval(() => {
        lines.forEach(line => {
            const lineWidth = Math.floor(Math.random() * (80 - 20 + 1)) + 20;
            line.style.width = `${lineWidth}%`;
        })
    }, 600);

    return () => {
        generateTab.style.opacity = "1";
        generateTab.style.cursor = "auto";
        generateTab.style.pointerEvents = "auto";
        historyTab.style.opacity = "1";
        historyTab.style.cursor = "auto";
        historyTab.style.pointerEvents = "auto";

        closeFrameBtn.style.visibility = 'visible';
        keepBtn.style.visibility = 'visible';
        regenBtn.style.visibility = 'visible';

        lines.forEach(line => {
            document.querySelector('.output-frame .head .fs-24').style.display = 'none';
            line.style.display = 'none';
            clearInterval(intervalId);
        });
    }
}

// * FUNCTION TO UPDATE IMAGE PREVIEW
function updateImagePreview(event, imagePreview) {
    const file = event.target.files[0];

    if (file) {
        imagePreview.src = URL.createObjectURL(file);
        imagePreview.style.opacity = '1';
        canvas.style.aspectRatio = `${imagePreview.naturalWidth} / ${imagePreview.naturalHeight}`;
    }
}

// * FUNCTION TO CLEAR CANVAS
function clearCanvas() {
    imagePreview.style.opacity = '0';
    imagePreview.src = '';

    postHeadline.textContent = '';
    postDescription.textContent = '';
}

// * FUNCTION TO SELECT TEXT CONTENT
function selectTextContent() {
    textPreview.classList.toggle('selected');
}

// * FUNCTION TO SHOW TEXT-CONTENT [HEADLINE] IN CANVAS
function showHeadline(btn) {
    const headlineElement = btn.closest('.headline');
    const headlineText = headlineElement.querySelector('.text').textContent;
    const headlineMini = headlineElement.querySelector('.mini').textContent;

    postHeadline.textContent = headlineText;
    postDescription.textContent = headlineMini;
    
    let textXCoord = imagePreview.x + 20
    let textYCoord = imagePreview.y + imagePreview.offsetHeight - 20 - textPreview.offsetHeight;
    let textWidth = imagePreview.offsetWidth - 40;

    textPreview.style.left = `${textXCoord}px`;
    textPreview.style.top = `${textYCoord}px`;
    textPreview.style.width = `${textWidth}px`;
    textPreview.style.height = 'fit-content';
}

// * FUNCTION TO UPDATE THE WIDTH OF TEXT-PREVIEW
function updateTextPreviewWidth(width) {
    textPreview.style.width = `${parseInt(textPreview.style.width) + width}px`;
}

// * FUNCTION TO DOWNLOAD THE CANVAS AS AN IMAGE
function downloadElement() {
    // DISABLED EXPORT BTN
    exportBtn.disabled = true;
    exportBtn.style.opacity = '0.6';
    
    // Render the element to a canvas object
    html2canvas(canvas, {
        scale: 2,
        useCORS: true,
    }).then(canvas => {
        const imageURL = canvas.toDataURL("image/png");

        const link = document.createElement("a");
        link.download = "echo-post.png";
        link.href = imageURL;

        link.click();
    });
    
    exportBtn.disabled = false;
    exportBtn.style.opacity = '1';
}

// * FUNCTION TO GET PRODUCT DATA FROM PRODUCT CARD'S BUTTON
function getProductData(btn) {
    const productCard = btn.closest('.product');

    const title = productCard.querySelector('.product-title').textContent;
    const desc = productCard.querySelector('.product-desc').textContent;

    return { title: title, desc: desc };
}

// * FUNCTION TO HANDLE GENERATION DURATION
function handleGenDuration(btn) {
    showGenSkeleton();
    clearAnimation = animateGenSkeleton();

    cachedData = getProductData(btn);
    sendMessage("headlines-sys", cachedData);
}

// * FUNCTION TO CLOSE OUTPUT FRAME
function closeOutputFrame() {
    outputFrame.style.opacity = '0';
    setTimeout(() => { outputFrame.style.display = 'none'; }, 500);
}

// * FUNCTION TO KEEP HEADLINES IN CANVAS
function keepHeadlines() {
    postHeadline.textContent = outputHeadline.textContent;
    postDescription.textContent = outputDesc.textContent;

    let textXCoord = imagePreview.x + 20
    let textYCoord = imagePreview.y + imagePreview.offsetHeight - 20 - textPreview.offsetHeight;
    let textWidth = imagePreview.offsetWidth - 40;

    textPreview.style.left = `${textXCoord}px`;
    textPreview.style.top = `${textYCoord}px`;
    textPreview.style.width = `${textWidth}px`;
    textPreview.style.height = 'fit-content';

    closeOutputFrame();
}

// * FUNCTION TO REGENERATE HEADLINES
function regenerate() {
    document.querySelector('.output-frame .head .fs-24').style.display = 'block';
    lines.forEach(line => {
        line.style.display = 'block';
    });

    outputHeadline.textContent = '';
    outputDesc.textContent = '';

    showGenSkeleton();
    clearAnimation = animateGenSkeleton();

    sendMessage("headlines-sys", cachedData);
}

// * FUNCTION TO UPDATE COLOR VALUE OF HEADLINE
function updateHeadlineColor() {
    const color = headlineColorInput.value;
    
    headlineColorSymbol.style.color = color;
    postHeadline.style.color = color;
    postDescription.style.color = color;
}

// ==================================================
// EVENT LISTENERS
// ==================================================

// & EVENT LISTENER FOR CLEAR CANVAS BUTTON
clearCanvasBtn.addEventListener('click', clearCanvas);

// & EVENT LISTENER FOR IMAGE INPUT
imageInput.addEventListener('change', (event) => {
    updateImagePreview(event, imagePreview);
});

// & EVENT LISTENERS FOR ADD BUTTONS
addBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
        showHeadline(btn);
        document.querySelector(".history").classList.remove('active');
    });
});

// & EVENT LISTENER FOR TEXT PREVIEW
textPreview.addEventListener('click', selectTextContent);

// & EVENT LISTENER FOR INCREASE TEXT-PREVIEW WIDTH BUTTON
increaseTextWidthBtn.addEventListener('pointerdown', () => {
    intervalId = setInterval(() => {
        updateTextPreviewWidth(20);
        textPreview.style.border = '1px dashed var(--color-accent-main)';        
    }, 100);
});

// & EVENT LISTENER FOR DECREASE TEXT-PREVIEW WIDTH BUTTON
decreaseTextWidthBtn.addEventListener('pointerdown', () => {
    intervalId = setInterval(() => {
        updateTextPreviewWidth(-20);
        textPreview.style.border = '1px dashed var(--color-accent-main)';
    }, 100);
});

// & EVENT LISTENER FOR INCREASE TEXT-PREVIEW WIDTH BUTTON
increaseTextWidthBtn.addEventListener('pointerup', () => {
    clearInterval(intervalId);
    textPreview.style.border = 'none';
});

// & EVENT LISTENER FOR DECREASE TEXT-PREVIEW WIDTH BUTTON
decreaseTextWidthBtn.addEventListener('pointerup', () => {
    clearInterval(intervalId);
    textPreview.style.border = 'none';
});

// & EVENT LISTENER FOR HEADLINE COLOR INPUT
headlineColorInput.addEventListener('input', updateHeadlineColor);

// & EVENT LISTENER FOR EXPORT BUTTON
exportBtn.addEventListener('click', downloadElement);

// & EVENT LISTENER FOR HEAD-GEN-BTN CLICK
headGenBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        handleGenDuration(btn);
        document.querySelector('.generate').classList.remove('active');
    });
});

// & EVENT LISTENER FOR CUSTOM PROMPT SEND BUTTON
customProductSend.addEventListener('click', () => {
    const productTitle = customProductTitle.value;
    const productDesc = customProductDesc.value;

    if (productTitle.trim() === '' || productDesc.trim() === '') return;

    showGenSkeleton();
    clearAnimation = animateGenSkeleton();

    const productData = { title: productTitle, desc: productDesc }
    cachedData = { title: productTitle, desc: productDesc }

    sendMessage("headlines-sys", productData);
});

// & EVENT LISTENER FOR KEEP BUTTON
keepBtn.addEventListener('click', keepHeadlines);

// & EVENT LISTENER FOR REGENERATE BUTTON
regenBtn.addEventListener('click', regenerate);

// & EVENT LISTENER FOR CLOSE OUTPUT FRAME BUTTON
closeFrameBtn.addEventListener('click', closeOutputFrame);

// & EVENT LISTENER FOR PROMPT-TRIGGER CLICK
promptTrigger.addEventListener('click', () => {
    promptArea.classList.toggle('active');
})

// & EVENT LISTENER FOR TOGGLING HISTORY & GENERATION TABS
toggleTabListener(toggleHistoryTab, document.querySelector('.history'));
toggleTabListener(toggleGenerationTab, document.querySelector('.generate'));

textPreview.addEventListener('pointerdown', (e) => {
    e.preventDefault(); // Prevent default touch behavior
    textPreview.setPointerCapture(e.pointerId); // Capture the pointer
    
    let shiftX = e.clientX - textPreview.getBoundingClientRect().left;
    let shiftY = e.clientY - textPreview.getBoundingClientRect().top;

    function moveAt(clientX, clientY) {
        textPreview.style.left = clientX - shiftX + 'px';
        textPreview.style.top = clientY - shiftY + 'px';
    }

    function onPointerMove(e) {
        e.preventDefault(); // Prevent scrolling during drag
        moveAt(e.clientX, e.clientY);
    }

    function onPointerUp(e) {
        document.removeEventListener('pointermove', onPointerMove);
        document.removeEventListener('pointerup', onPointerUp);
        document.removeEventListener('pointercancel', onPointerUp);
        textPreview.releasePointerCapture(e.pointerId);
    }

    document.addEventListener('pointermove', onPointerMove);
    document.addEventListener('pointerup', onPointerUp);
    document.addEventListener('pointercancel', onPointerUp); // Handle interruptions
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

    sendToastNotification('Headline generated successfully!', 'thumb_up', 'var(--color-state-green)');
});