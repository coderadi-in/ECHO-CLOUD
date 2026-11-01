// ==================================================
// ELEMENT REFERENCE
// ==================================================

const products = document.querySelectorAll('.product');
const colors = [ '#FE938C', '#6CD4FF', '#5D576B', '#D496A7', '#A49694' ];

const capGenBtns = document.querySelectorAll('.cap-gen-btn');
const HeadGenBtns = document.querySelectorAll('.hed-gen-btn');

const startSync = document.getElementById('startSync')
const syncingAnimation = document.querySelector('.syncing-animation');
const animationLine = document.querySelector('.syncing-animation .line');

// ==================================================
// FUNCTIONS
// ==================================================

// * FUNCTION TO APPLY RANDOM BACKGROUND COLOR TO EACH CARD
export function applyRandomBackgroundColor() {
    products.forEach(product => {
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        product.style.backgroundColor = randomColor;
    });
}

// * FUNCTION TO GET PRODUCT DATA FROM PRODUCT CARD'S BUTTON
function getProductData(btn) {
    const productCard = btn.closest('.product');

    const title = productCard.querySelector('.product-title').textContent;
    const price = productCard.querySelector('.product-price').textContent;
    const desc = productCard.querySelector('.product-desc').textContent;

    return { title: title, price: price, desc: desc };
}

// * FUNCTION TO START SYNCING ANIMATION
function startSyncingAnimation() {
    animationLine.style.transformOrigin = 'left';
    animationLine.style.transform = 'scaleX(1)';

    setTimeout(() => {
        animationLine.style.transformOrigin = 'right';
        animationLine.style.transform = 'scaleX(0)';
    }, 1000);

    setTimeout(() => { startSyncingAnimation(); }, 2000);
}

// ==================================================
// EVENT LISTENERS
// ==================================================

// & EVENT LISTENER FOR DOM-CONTENT-LOAD
document.addEventListener('DOMContentLoaded', applyRandomBackgroundColor);

// & EVENT LISTENER FOR CAP-GEN-BUTTONS CLICK
capGenBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const message = getProductData(btn);
        localStorage.setItem('pending_generation', JSON.stringify(message));             
        window.location.href = '/app/captions?refer=store';
    });
});

// & EVENT LISTENER FOR HEAD-GEN-BUTTONS CLICK
HeadGenBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const message = getProductData(btn);
        localStorage.setItem('pending_generation', JSON.stringify(message));             
        window.location.href = '/app/headlines?refer=store';
    });
});

// & EVENT LISTENER FOR START-SYNC-BTN CLICK
startSync.addEventListener('click', () => {
    syncingAnimation.style.display = 'flex';
    syncingAnimation.style.opacity = '1';

    setTimeout(() => { startSyncingAnimation() }, 300);
});