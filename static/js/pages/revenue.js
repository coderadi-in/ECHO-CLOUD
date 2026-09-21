// ==================================================
// REFERENCES
// ==================================================

// ? ELEMENT REFERENCES
const growthChart = document.getElementById('growthChart').getContext('2d');
const contributionChart = document.getElementById('contributionChart').getContext('2d');
const productSearch = document.getElementById('searchProduct');
const exportRevenueBtn = document.getElementById('exportRevenue');

// ? AUXILIARY REFERENCES
const hrefOrigin = window.location.origin;
const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
const colorShades = [
    '#34623F', '#568259', '#F07167', '#E3B5CE',
    '#F6BE9A', '#FFCF9C', '#00A7E1', '#A5A5A5',
    '#8D98A7', '#A15E49', '#947BD3', '#DECBB7',
];

// ? API REFERENCES
const ORDER_API_ENDPOINT = `${window.location.origin}/api/orders/fetch/prod-qty/by-range`;
const QTIME_COMPARE_API_ENDPOINT = `${window.location.origin}/api/matrices/compare/qty/by-time`;
const QSTATUS_COMPARE_API_ENDPOINT = `${window.location.origin}/api/matrices/compare/qty/by-status`;
const ATIME_COMPARE_API_ENDPOINT = `${window.location.origin}/api/matrices/compare/amt/by-time`;
const ASTATUS_COMPARE_API_ENDPOINT = `${window.location.origin}/api/matrices/compare/amt/by-status`;
const PRODUCT_COMPARE_API_ENDPOINT = `${window.location.origin}/api/matrices/compare/product`
const EXPORT_DATA_API_ENDPOINT = `${window.location.origin}/api/data_exporter/revenue`;

// ! TEMPORARY REFERENCES
const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: { grid: { display: false, }, },
        y: { beginAtZero: true, },
    }
}

// ==================================================
// IMPORTS
// ==================================================

import { sendToastNotification } from '../components/toast.js';

// ==================================================
// FUNCTIONS
// ==================================================

// * FUNCTION TO FETCH EXPORT DATA
async function _fetchExportedData() {
    // FETCH DATA
    const response = await fetch(EXPORT_DATA_API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify({
            startRange: null,
            endRange: null,
        }),
    });

    // CHECK RESPONSE
    if (!response.ok) {
        sendToastNotification("Can't export data.", "error", "var(--color-state-red)");
        return;
    }

    // DOWNLOAD RESPONSE
    const blob = await response.blob();
    const dataURL = URL.createObjectURL(blob);
    const downloadLink = document.createElement('a');
    downloadLink.href = dataURL;
    downloadLink.download = "revenue.csv";
    downloadLink.click();
    downloadLink.remove();
}

// * FUNCTION TO FETCH PRODUCT COMPARATIVE VALUE
async function _fetchProductComparativeValue(productId) {
    const response = await fetch(PRODUCT_COMPARE_API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify({ productId: productId, }),
    });

    if (!response.ok) {
        sendToastNotification("Can't fetch matrices!", "error", "var(--color-state-red)");
        return 0;
    }

    const data = await response.json();
    const value = data.output;
    return value;
}

// * FUNCTION TO FETCH TIME COMPARATIVE VALUE
async function _fetchTimeComparativeValue(timeFrame, mode) {
    // FETCH VALUES FROM API
    const endPoint = mode==='qty'?QTIME_COMPARE_API_ENDPOINT:ATIME_COMPARE_API_ENDPOINT
    const response = await fetch(endPoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify({ timePeriod: timeFrame, }),
    });

    if (!response.ok) {
        sendToastNotification("Can't fetch matrices!", "error", "var(--color-state-red)");
        return 0;
    }

    const data = await response.json();
    const value = data.output;
    return value;
}

// * FUNCTION TO FETCH STATUS COMPARATIVE VALUE
async function _fetchStatusComparativeValue(status, mode) {
    // FETCH VALUES FROM API
    const endPoint = mode==='qty'?QSTATUS_COMPARE_API_ENDPOINT:ASTATUS_COMPARE_API_ENDPOINT
    const response = await fetch(endPoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify({ orderStatus: status, }),
    });

    if (!response.ok) {
        sendToastNotification("Can't fetch matrices!", "error", "var(--color-state-red)");
        return 0;
    }

    const data = await response.json();
    const value = data.output;
    return value;
}

// * FUNCTION TO ADD COMPARATIVE VALUES IN PAGE
async function addComparativeValues() {
    const monthlyDeltaElem = document.getElementById('deltaYearly');
    const yearlyDeltaElem = document.getElementById('deltaMonthly');
    const failedDeltaElem = document.getElementById('deltaFailed');
    const totalDeltaElem = document.getElementById('deltaTotal');
    const bestsellerDeltaElem = document.getElementById('deltaBestseller');
    const topRevDeltaElem = document.getElementById('deltaRevenueCont');

    const deltaMonthly = await _fetchTimeComparativeValue('month', 'qty');
    const deltaYearly = await _fetchTimeComparativeValue('year', 'qty');
    const deltaFailed = await _fetchStatusComparativeValue('rejected', 'qty');
    const deltaTotal = await _fetchTimeComparativeValue('month', 'qty');
    const deltaBestseller = await _fetchProductComparativeValue(bestsellerDeltaElem.dataset.productId);
    const deltaTopRev = await _fetchProductComparativeValue(topRevDeltaElem.dataset.productId);

    if (deltaMonthly >= 0) {
        monthlyDeltaElem.textContent = `+ ${Math.abs(deltaMonthly)}%`;
        monthlyDeltaElem.classList.add('status-green');
    } else {
        monthlyDeltaElem.textContent = `- ${Math.abs(deltaMonthly)}%`;
        monthlyDeltaElem.classList.add('status-red');
    }
    
    if (deltaYearly >= 0) {
        yearlyDeltaElem.textContent = `+ ${Math.abs(deltaYearly)}%`;
        yearlyDeltaElem.classList.add('status-green');
    } else {
        yearlyDeltaElem.textContent = `- ${Math.abs(deltaYearly)}%`;
        yearlyDeltaElem.classList.add('status-red');
    }

    if (deltaFailed <= 0) {
        failedDeltaElem.textContent = `- ${Math.abs(deltaFailed)}%`;
        failedDeltaElem.classList.add('status-green');
    } else {
        failedDeltaElem.textContent = `+ ${Math.abs(deltaFailed)}%`;
        failedDeltaElem.classList.add('status-red');
    }

    if (deltaTotal >= 0) {
        totalDeltaElem.textContent = `+ ${deltaTotal}%`;
        totalDeltaElem.classList.add('status-green');
    } else {
        totalDeltaElem.textContent = `- ${deltaTotal}%`;
        totalDeltaElem.classList.add('status-red');
    }

    if (deltaBestseller >= 0) {
        bestsellerDeltaElem.textContent = `+ ${deltaBestseller}%`;
        bestsellerDeltaElem.classList.add('status-green');
    } else {
        bestsellerDeltaElem.textContent = `- ${deltaBestseller}%`;
        bestsellerDeltaElem.classList.add('status-red');
    }

    if (deltaTopRev >= 0) {
        topRevDeltaElem.textContent = `+ ${deltaTopRev}%`;
        topRevDeltaElem.classList.add('status-green');
    } else {
        topRevDeltaElem.textContent = `- ${deltaTopRev}%`;
        topRevDeltaElem.classList.add('status-red');
    }
}

// * FUNCTION TO GENERATE RANDOM HEX
function getRandomHexColor() {
    return `${colorShades[Math.floor(Math.random() * colorShades.length)]}`;
}


//  * FUNCTION TO RENDER GROWTH CHART
async function renderGrowthChart() {
    const root = document.body;
    const rootStyle = getComputedStyle(root);
    
    const fetch_req = await fetch(`${hrefOrigin}/api/orders/fetch/qty-value/by-year`);
    const response = await fetch_req.json();

    const chart = new Chart(growthChart, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [
                {
                    label: "Orders",
                    data: response.output.qty,
                    backgroundColor: rootStyle.getPropertyValue('--color-chart-secondary'),
                    borderRadius: 16,
                    yAxisID: 'y'
                },
                {
                    label: "Sales",
                    data: response.output.amt,
                    backgroundColor: rootStyle.getPropertyValue('--color-chart-secondary'),
                    borderRadius: 16,
                    yAxisID: 'y1'
                },
            ]
        },
        options: barChartOptions
    });

    return chart.destroy;
}

// * FUNCTION TO RENDER CONTRIBUTION CHART
async function renderContributionChart() {
    const fetch_req = await fetch(`${hrefOrigin}/api/orders/fetch/prod-qty/by-month`);
    const response = await fetch_req.json();

    const chart = new Chart(contributionChart, {
        type: 'doughnut',
        data: {
            labels: response.output.products,
            datasets: [{
                label: "Contribution in Revenue",
                data: response.output.qty,
                backgroundColor: Array.from({ length: 4 }, getRandomHexColor),
                hoverOffset: 4,
                borderColor: 'transparent',
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
        },
    });

    return chart.destroy;
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

// & INITIAL DISPLAY SETTINGS
document.addEventListener('DOMContentLoaded', async () => {
    renderGrowthChart();
    renderContributionChart();
    addComparativeValues();
});

// & EVENT LISTENER FOR PRODUCT SEARCH
productSearch.addEventListener('input', () => { searchProducts(productSearch.value); })

// & EVENT LISTENER FOR EXPORT BUTTON CLICK
exportRevenueBtn.addEventListener('click', _fetchExportedData);