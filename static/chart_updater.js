/**
 * Chart Updater
 *
 * Fetches test ratio data from the API and updates the pie chart
 * and legend on the dashboard.
 */

document.addEventListener('DOMContentLoaded', function() {
    updatePieChart();
});

async function updatePieChart() {
    try {
        // Get the company ID from the data attribute
        const chartContainer = document.querySelector('.chart-container');
        const companyId = chartContainer.dataset.companyId;

        if (!companyId) {
            console.warn('Company ID not found');
            return;
        }

        // Fetch data from the API
        const response = await fetch(`/api/test-ratios/${companyId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch test ratios');
        }

        const data = await response.json();

        // Update the pie chart
        updatePieChartStyles(data.winning_percent, data.losing_percent, data.other_percent);

        // Update the legend
        updateLegend(data.winning_percent, data.losing_percent, data.other_percent);

    } catch (error) {
        console.error('Error updating pie chart:', error);
        // Keep the default values if there's an error
    }
}

function updatePieChartStyles(winningPercent, losingPercent, otherPercent) {
    const pieElement = document.querySelector('.pie.hollow');

    if (!pieElement) {
        console.warn('Pie chart element not found');
        return;
    }

    // Calculate the gradient stops based on percentages
    // The colors are: accent (winner), primary (loser), secondary (other)
    const winningEnd = winningPercent;
    const losingEnd = winningPercent + losingPercent;

    // Update the conic-gradient
    const gradient = `conic-gradient(
        var(--accent) 0% ${winningEnd}%,
        var(--primary) ${winningEnd}% ${losingEnd}%,
        var(--secondary) ${losingEnd}% 100%
    )`;

    pieElement.style.background = gradient;
}

function updateLegend(winningPercent, losingPercent, otherPercent) {
    // Find all legend items
    const legendItems = document.querySelectorAll('.legend-item');

    if (legendItems.length < 3) {
        console.warn('Not enough legend items found');
        return;
    }

    // Update Winner percentage (first legend item)
    const winnerSpans = legendItems[0].querySelectorAll('span');
    if (winnerSpans.length >= 2) {
        winnerSpans[1].textContent = `${winningPercent} %`;
    }

    // Update Loser percentage (second legend item)
    const loserSpans = legendItems[1].querySelectorAll('span');
    if (loserSpans.length >= 2) {
        loserSpans[1].textContent = `${losingPercent} %`;
    }

    // Update Other percentage (third legend item)
    const otherSpans = legendItems[2].querySelectorAll('span');
    if (otherSpans.length >= 2) {
        otherSpans[1].textContent = `${otherPercent} %`;
    }
}