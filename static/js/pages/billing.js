// ==================================================
// ELEMENT REFERENCE
// ==================================================

const upgradeProBtn = document.getElementById('upgradePro');
const upgradeUltraBtn = document.getElementById('upgradeUltra');

const renewalDate = document.getElementById('renewalDate');
const paymentRows = document.querySelectorAll('.payment-row');

// ==================================================
// IMPORTS
// ==================================================

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

// * FUNCTION TO CREATE AN INTERSECTION OBSERVER FOR SIMPLIFYING DATE IN PAYMENTS TABLE
function startSimpler() {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const dateElement = entry.target.querySelector('.date-text');

                if (dateElement) {
                    const processableString = dateElement.textContent.slice(2);
                    const dateText = processableString.split('-').reverse().join('/');
                    dateElement.textContent = dateText;
                    observer.unobserve(entry.target);
                }
            }
        });
    });

    paymentRows.forEach(row => { observer.observe(row); });
}

// * FUNCTION TO SEND AN ORDER REQUEST
async function _sendOrderRequest(planName, note) {
    const response = await fetch('/billing/create-order', {
        method: "POST",
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify({ planName: planName, }),
    });

    if (!response.ok) {
        sendToastNotification("Something went wrong while processing your order!", "error", "var(--color-state-red)");
        return;
    }

    const data = await response.json();    

    if (!data.success) {
        sendToastNotification("Something went wrong while processing your order!", "error", "var(--color-state-red)");
        return;
    }

    const options = {
        key: data.key,
        order_id: data.order_id,
        amount: data.amount,
        currency: data.currency,
        name: "AUVORA ECHO",
        description: note,
        handler: function (response) {
            window.location =
                `/billing/payments?order_id=${response.razorpay_order_id}&payment_id=${response.razorpay_payment_id}&signature=${response.razorpay_signature}`;
        },
        modal: {
            ondismiss: function () {
                sendToastNotification("Payment cancelled by user.", "cancel", "var(--color-state-red)");
            }
        }
    };

    const razorpay = new Razorpay(options);
    razorpay.open();
}

// ==================================================
// EVENT LISTENERS
// ==================================================

// & INITIAL DISPLAY SETTINGS
document.addEventListener('DOMContentLoaded', () => {
    formatDate();
    startSimpler();
});

// & EVENT LISTENER FOR UPGRADE-BUTTON CLICK
if (upgradeProBtn) {
    upgradeProBtn.addEventListener('click', async () => {
        await _sendOrderRequest('Pro', 'Pro Plan');
    });
}

if (upgradeUltraBtn) {
    upgradeUltraBtn.addEventListener('click', async () => {
        await _sendOrderRequest('Ultra', 'Ultra Plan');
    });
}