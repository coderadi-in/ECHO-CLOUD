// ==================================================
// ELEMENT REFERENCE
// ==================================================

const growthChart = document.getElementById('growthChart').getContext('2d');
const contributionChart = document.getElementById('contributionChart').getContext('2d');

// ! TEMPORARY REFERENCES
const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
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
    return `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}57`;
}


//  * FUNCTION TO RENDER GROWTH CHART
function renderGrowthChart() {
    const root = document.body;
    const rootStyle = getComputedStyle(root);

    const chart = new Chart(growthChart, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [{
                label: "Sales",
                data: [
                    34, 143, 134, 232, 345, 234,
                    435, 345, 423, 523, 587, 712
                ],
                backgroundColor: rootStyle.getPropertyValue('--color-chart-background'),
                borderRadius: 16
            }]
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