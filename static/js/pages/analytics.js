// ==================================================
// REFERENCES
// ==================================================

// ? ELEMENT REFERENCES
const fromDate = document.getElementById('fromDate');
const toDate = document.getElementById('toDate');
const analyticsTableBody = document.querySelector('.analytics-table .analytics-body');
const productSearch = document.getElementById('searchProduct');

// ? API REFERENCES
const ORDER_API_ENDPOINT = `${window.location.origin}/api/orders/fetch/prod-qty/by-range`;

// ==================================================
// IMPORTS
// ==================================================

import { socket, sendMessage } from '../base/socket_listeners.js';
import { sendToastNotification } from '../components/toast.js';

// ==================================================
// FUNCTIONS
// ==================================================

// * FUNCTION TO FORMAT DATE
function formatDate(date) {
    const dateObj = new Date(date);
    const yyyy = dateObj.getFullYear();
    const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
    const dd = String(dateObj.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}

// * FUNCTION TO GET START AND END DATE OF CURRENT MONTH
function _getCurrentMonthRange() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();

    // 1. Get the first day of the current month
    const firstDay = new Date(year, month, 1);

    // 2. Get the last day of the current month (day 0 of the next month)
    const lastDay = new Date(year, month + 1, 0);

    return {
        start: formatDate(firstDay),
        end: formatDate(lastDay)
    };
}

// * FUNCTION TO FILL DEFAULT VALUES IN DATA RANGE INPUT
function fillDefaultDateRange() {
    const dateRange = _getCurrentMonthRange();
    fromDate.value = dateRange.start;
    toDate.value = dateRange.end;
}

// * FUNCTION TO FETCH ORDERS FROM SPECIFIC DATE RANGES
async function _getOrdersByDateRange(startDate, endDate) {
    // FORMAT DATE
    const formattedStart = formatDate(startDate);
    const formattedEnd = formatDate(endDate);

    // FETCH ORDERS
    const response = await fetch(ORDER_API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            start: formattedStart,
            end: formattedEnd
        }),
    });

    // CHECK FOR API RESPONSE
    if (!response.ok) {
        sendToastNotification("Can't fetch orders. You can retry.", "error", "var(--color-state-red)");
        return;
    }

    // RETURN OUTPUT
    const output = await response.json();
    return output.output;
}

// * FUNCTION TO CREATE A NEW ORDER ROW
function _createOrderRow(orderObject) {
    // DEFINE A POPOVER CREATOR FUNCTION
    const _popoverCreator = (class_, id) => {
        const popover = document.createElement('div');
        popover.classList.add(class_, 'popover');
        popover.id = id;
        popover.setAttribute('popover', '');
        popover.addEventListener('beforetoggle', (event) => {
            setTimeout(() => {
                popover.classList.toggle('open', event.newState === 'open');
            }, 100);
        });

        const innerPopover = document.createElement('div');
        innerPopover.classList.add(`${class_}__inner`, 'popover__inner');

        return {
            outer: popover,
            inner: innerPopover,
        };
    }

    // DEFINE AN ELEMENT CREATOR FUNCTION
    const _elementCreator = (textContent, class_, elementTag = 'span', popoverTarget) => {
        const element = document.createElement(elementTag);

        if (elementTag == 'button') { element.setAttribute('popovertarget', popoverTarget); }

        element.classList.add(...class_);
        element.textContent = textContent;
        return element
    }

    // DEFINE AN ORDER STATUS UPDATER CREATOR FUNCTION
    const _updaterCreator = (textContent, class_) => {
        const element = document.createElement('span');
        element.classList.add(...class_);
        element.textContent = textContent;

        element.addEventListener('click', () => {
            sendMessage('order-status-update-sys', {
                orderId: orderObject.id,
                newStatus: textContent
            });
            const statusShower = document.querySelector('.order-status');
            statusShower.textContent = textContent;
            statusShower.classList.remove('status-rejected', 'status-unrecognized', 'status-accepted');
            statusShower.classList.add(`status-${textContent}`);
        });

        return element;
    }

    // INITIATE WRAPPERS
    const wrapper = document.createElement('div')
    wrapper.classList.add('analytics-row', 'row-body', 'grid', 'cols-4', 'p-12', 'v-center');
    const idPopover = _popoverCreator('id-popover', `order-${orderObject.id}`);
    const statusPopover = _popoverCreator('status-popover', `status-${orderObject.id}`);

    // INITIATE ELEMENTS
    const idElement = _elementCreator(`#${orderObject.id}`, ['btn', 'ulink', 'order-id'], 'button', `order-${orderObject.id}`);
    const dateElement = _elementCreator(orderObject.ordered_on, ['text']);
    const amountElement = _elementCreator(orderObject.amount, ['text']);
    const statusElement = _elementCreator(orderObject.status || 'unrecognized', ['btn', 'text', 'order-status', `status-${orderObject.status}`], 'button', `status-${orderObject.id}`);
    
    const productTitle = _elementCreator(orderObject.product, ['text']);
    const productQty = _elementCreator(`QTY: ${orderObject.qty}`, ['text']);

    const statusAccepted = _updaterCreator('accepted', ['link', 'status-updater']);
    const statusRejected = _updaterCreator('rejected', ['link', 'status-updater']);
    const statusUnrecognized = _updaterCreator('unrecognized', ['link', 'status-updater']);

    // APPEND ELEMENTS
    wrapper.appendChild(idElement);
    wrapper.appendChild(dateElement);
    wrapper.appendChild(amountElement);
    wrapper.appendChild(statusElement);

    idPopover.inner.appendChild(productTitle);
    idPopover.inner.appendChild(productQty);
    idPopover.outer.appendChild(idPopover.inner);
    wrapper.appendChild(idPopover.outer);

    statusPopover.inner.appendChild(statusAccepted);
    statusPopover.inner.appendChild(statusRejected);
    statusPopover.inner.appendChild(statusUnrecognized);
    statusPopover.outer.appendChild(statusPopover.inner);
    wrapper.appendChild(statusPopover.outer);

    return wrapper;
}

// * FUNCTION TO UPDATE ORDERS TABLE
async function updateOrderTable() {
    // INITIATE DATE RANGE
    const startRange = fromDate.value || _getCurrentMonthRange().start;
    const endRange = toDate.value || _getCurrentMonthRange().end;

    // FETCH ORDERS FROM API
    const output = await _getOrdersByDateRange(startRange, endRange);

    // REMOVE PREVIOUS ELEMENTS
    document.querySelectorAll('.analytics-row.row-body').forEach(elem => {
        elem.remove();
    });

    // ADD NEW ELEMENTS
    output.forEach(object => {
        const orderRow = _createOrderRow(object);
        analyticsTableBody.appendChild(orderRow);
    });
}

// * FUNCTION TO SEARCH FOR PRODUCTS BY KEYWORD
function searchProducts(keyword) {
    const products = document.querySelectorAll('.product-info');

    if (keyword.trim() === '') {
        products.forEach(product => { product.style.display = 'flex'; })    
    }

    products.forEach(product => {
        const productTitle = product.querySelector('.product-title');
        if (!productTitle.textContent.includes(keyword)) { product.style.display = 'none'; }
    });
}

// ==================================================
// EVENT LISTENERS
// ==================================================

// & INITIAL DISPLAY LOAD
document.addEventListener('DOMContentLoaded', () => {
    fillDefaultDateRange();
    updateOrderTable();
});

// & EVENT LISTENER FOR DATE MODIFICATION
fromDate.addEventListener('change', updateOrderTable);
toDate.addEventListener('change', updateOrderTable);

// & EVENT LISTENER FOR PRODUCT SEARCH
productSearch.addEventListener('input', () => { searchProducts(productSearch.value); })

// ==================================================
// SOCKET LISTENERS
// ==================================================

// | ORDER STATUS UPDATER
socket.on('order-status-update-cl', (data) => {
    if (data === 200) { sendToastNotification('Order status has been updated.', 'check', 'var(--color-state-green)'); }
    else { sendToastNotification("Can't update order status.", 'check', 'var(--color-state-green)'); }
});