// ==================================================
// ELEMENT REFERENCE
// ==================================================

const toastContainer = document.querySelector('.toast-container');

// ==================================================
// FUNCTIONS
// ==================================================

// * FUNCTION TO CREATE A TOAST NOTIFICATION
export function sendToastNotification(message, iconContent, accent) {
    // CREATE NOTIFICATION WRAP
    const notificationRow = document.createElement('div');
    notificationRow.classList.add('notification-row', 'row', 'gap-12', 'ph-12', 'pv-8', 'rounded-12', accent);
    
    // CREATE & APPEND NOTIFICATION ICON
    const notificationIcon = document.createElement('span');
    notificationIcon.classList.add('symbol');
    notificationIcon.setAttribute('aria-label', 'Notification Icon');
    notificationIcon.style.color = accent;
    notificationIcon.textContent = iconContent;

    // CREATE & APPEND NOTIFICATION TEXT
    const notificationText = document.createElement('span');
    notificationText.classList.add('text');
    notificationText.setAttribute('aria-label', 'Notification Text');
    notificationText.textContent = message;

    // APPEND NOTIFICATION IN CONTAINER
    notificationRow.appendChild(notificationIcon);
    notificationRow.appendChild(notificationText);
    toastContainer.appendChild(notificationRow);

    // NOTIFY ON THE SCREEN
    setTimeout(() => {
        notificationRow.classList.add('show');
    }, 100);
    setTimeout(() => {
        notificationRow.classList.remove('show');
    }, 3100);
    setTimeout(() => {
        toastContainer.removeChild(notificationRow);
    }, 3700);
}