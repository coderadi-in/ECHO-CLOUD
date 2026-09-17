// ==================================================
// REFERENCES
// ==================================================

// ? ELEMENT REFERENCES
const growthChart = document.getElementById('growthChart').getContext('2d');
const contributionChart = document.getElementById('contributionChart').getContext('2d');

// ? AUXILIARY REFERENCES
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
function renderGrowthChart() {
    const root = document.body;
    const rootStyle = getComputedStyle(root);

    const chart = new Chart(growthChart, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [
                {
                    label: "Orders",
                    data: [
                        34, 143, 134, 232, 345, 234,
                        435, 345, 423, 523, 587, 712
                    ],
                    backgroundColor: rootStyle.getPropertyValue('--color-chart-secondary'),
                    borderRadius: 16,
                    yAxisID: 'y'
                },
                {
                    label: "Sales",
                    data: [
                        44534, 30944, 30941, 49586, 89303, 348503,
                        85900, 94390, 193405, 234912, 234902, 209809
                    ],
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
function renderContributionChart() {
    const chart = new Chart(contributionChart, {
        type: 'doughnut',
        data: {
            labels: ["Plastic Visiting Card", "Aluminum Visiting Card", "Gold-Plated Visiting Card", "Titanium Visiting Card"],
            datasets: [{
                label: "Contribution in Revenue",
                data: [195, 108, 68, 18],
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

// ==================================================
// EVENT LISTENERS
// ==================================================

// & INITIAL DISPLAY SETTINGS
document.addEventListener('DOMContentLoaded', () => {
    renderGrowthChart();
    renderContributionChart();
});