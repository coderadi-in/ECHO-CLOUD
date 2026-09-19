// ==================================================
// REFERENCES
// ==================================================

// ? ELEMENT REFERENCES
const fromDate = document.getElementById('fromDate');
const toDate = document.getElementById('toDate');
const analyticsTableBody = document.querySelector('.analytics-table .analytics-body');

// ? API REFERENCES
const ORDER_API_ENDPOINT = `${window.location.origin}/api/orders/fetch/prod-qty/by-range`;

// ==================================================
// IMPORTS
// ==================================================

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
    // INITIATE WRAPPER
    const wrapper = document.createElement('div')
    wrapper.classList.add('analytics-row', 'row-body', 'grid', 'cols-4', 'p-12', 'v-center');

    // DEFINE AN ELEMENT CREATOR FUNCTION
    const _elementCreator = (textContent, class_) => {
        const element = document.createElement('span');
        element.classList.add(...class_);
        element.textContent = textContent;
        return element
    }

    // INITIATE ELEMENTS
    const idElement = _elementCreator(`#${orderObject.id}`, ['ulink', 'order-id']);
    const dateElement = _elementCreator(orderObject.ordered_on, ['text']);
    const amountElement = _elementCreator(orderObject.amount, ['text']);
    const statusElement = _elementCreator(orderObject.status || 'unrecognized', ['text', 'order-status']);

    // APPEND ELEMENTS
    wrapper.appendChild(idElement);
    wrapper.appendChild(dateElement);
    wrapper.appendChild(amountElement);
    wrapper.appendChild(statusElement);

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