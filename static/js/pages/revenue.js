// ==================================================
// REFERENCES
// ==================================================

// ? ELEMENT REFERENCES
const growthChart = document.getElementById('growthChart').getContext('2d');
const contributionChart = document.getElementById('contributionChart').getContext('2d');
const productSearch = document.getElementById('searchProduct');

// ? AUXILIARY REFERENCES
const hrefOrigin = window.location.origin;
const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
const colorShades = [
    '#34623F', '#568259', '#FFF689', '#FAF4D3',
    '#F6BE9A', '#FFCF9C', '#00A7E1', '#A5A5A5',
    '#8D98A7', '#A15E49', '#947BD3', '#DECBB7',
];

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
// FUNCTIONS
// ==================================================

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
});

// & EVENT LISTENER FOR PRODUCT SEARCH
productSearch.addEventListener('input', () => { searchProducts(productSearch.value); })