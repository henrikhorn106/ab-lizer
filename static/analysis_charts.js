/**
 * Analysis Charts
 *
 * Creates interactive Chart.js visualizations for AB test analysis
 */

document.addEventListener('DOMContentLoaded', function() {
    if (!variantData || variantData.length < 2) {
        console.warn('Insufficient variant data for charts');
        return;
    }

    // Chart colors matching the theme
    const colors = {
        primary: '#2E3E4A',
        accent: '#317AAE',
        gradient: 'rgba(49, 122, 174, 0.8)',
        gradientLight: 'rgba(49, 122, 174, 0.2)',
        secondary: '#F7F7F7',
        success: 'rgba(16, 185, 129, 0.8)',
        successLight: 'rgba(16, 185, 129, 0.2)'
    };

    // Conversion Rate Comparison Chart
    createConversionRateChart();

    // Sample Size Distribution Chart
    createSampleSizeChart();

    // Normal Distribution Chart
    if (analysisData && analysisData.distribution_data) {
        createNormalDistributionChart();
        createQQPlot();
    }
});

function createConversionRateChart() {
    const ctx = document.getElementById('conversionRateChart');
    if (!ctx) return;

    const labels = variantData.map(v => v.name);
    const conversionRates = variantData.map(v => v.conversion_rate);

    // Determine bar colors based on performance
    const backgroundColor = conversionRates.map((rate, index) => {
        if (index === 0) return 'rgba(46, 62, 74, 0.8)'; // Variant A - primary color
        return rate > conversionRates[0] ? 'rgba(16, 185, 129, 0.8)' : 'rgba(239, 68, 68, 0.8)'; // Winner (green) or Loser (red)
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Conversion Rate (%)',
                data: conversionRates,
                backgroundColor: backgroundColor,
                borderColor: backgroundColor.map(c => c.replace('0.8', '1')),
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return `Conversion Rate: ${context.parsed.y.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createSampleSizeChart() {
    const ctx = document.getElementById('sampleSizeChart');
    if (!ctx) return;

    const labels = variantData.map(v => v.name);
    const impressions = variantData.map(v => v.impressions);
    const conversions = variantData.map(v => v.conversions);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Sessions',
                    data: impressions,
                    backgroundColor: 'rgba(49, 122, 174, 0.6)',
                    borderColor: 'rgba(49, 122, 174, 1)',
                    borderWidth: 2,
                    borderRadius: 8
                },
                {
                    label: 'Conversions',
                    data: conversions,
                    backgroundColor: 'rgba(16, 185, 129, 0.6)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2,
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 13
                        },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y.toLocaleString();
                            return `${label}: ${value}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        },
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createNormalDistributionChart() {
    const ctx = document.getElementById('normalDistributionChart');
    if (!ctx) return;

    const distData = analysisData.distribution_data;
    const variantA = distData.variant_a;
    const variantB = distData.variant_b;

    // Calculate normal distribution for both variants
    function normalDistribution(x, mean, stdError) {
        const variance = stdError * stdError;
        return (1 / Math.sqrt(2 * Math.PI * variance)) *
               Math.exp(-Math.pow(x - mean, 2) / (2 * variance));
    }

    // Generate x values (conversion rates from 0 to max + buffer)
    const maxRate = Math.max(variantA.ci_upper, variantB.ci_upper);
    const minRate = Math.min(variantA.ci_lower, variantB.ci_lower);
    const buffer = (maxRate - minRate) * 0.3;
    const xMin = Math.max(0, minRate - buffer);
    const xMax = Math.min(1, maxRate + buffer);
    const numPoints = 200;
    const step = (xMax - xMin) / numPoints;

    // Generate data points for Variant A
    const dataA = [];
    const ciDataA = [];
    for (let i = 0; i <= numPoints; i++) {
        const x = xMin + i * step;
        const y = normalDistribution(x, variantA.mean, variantA.std_error);
        dataA.push({ x: x * 100, y: y }); // Convert to percentage

        // Add to confidence interval data if within CI
        if (x >= variantA.ci_lower && x <= variantA.ci_upper) {
            ciDataA.push({ x: x * 100, y: y });
        }
    }

    // Generate data points for Variant B
    const dataB = [];
    const ciDataB = [];
    for (let i = 0; i <= numPoints; i++) {
        const x = xMin + i * step;
        const y = normalDistribution(x, variantB.mean, variantB.std_error);
        dataB.push({ x: x * 100, y: y }); // Convert to percentage

        // Add to confidence interval data if within CI
        if (x >= variantB.ci_lower && x <= variantB.ci_upper) {
            ciDataB.push({ x: x * 100, y: y });
        }
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Variant A Distribution',
                    data: dataA,
                    borderColor: 'rgba(46, 62, 74, 1)',
                    backgroundColor: 'rgba(46, 62, 74, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                },
                {
                    label: 'Variant A 95% CI',
                    data: ciDataA,
                    borderColor: 'rgba(46, 62, 74, 0.3)',
                    backgroundColor: 'rgba(46, 62, 74, 0.2)',
                    borderWidth: 0,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: 'Variant B Distribution',
                    data: dataB,
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                },
                {
                    label: 'Variant B 95% CI',
                    data: ciDataB,
                    borderColor: 'rgba(16, 185, 129, 0.3)',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderWidth: 0,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 15,
                        usePointStyle: true,
                        filter: function(item) {
                            // Only show distribution lines in legend, not CI
                            return !item.text.includes('CI');
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        title: function(context) {
                            return `Conversion Rate: ${context[0].parsed.x.toFixed(2)}%`;
                        },
                        label: function(context) {
                            if (context.dataset.label.includes('CI')) {
                                return null; // Don't show CI in tooltip
                            }
                            return `Probability Density: ${context.parsed.y.toFixed(4)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Conversion Rate (%)',
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(2) + '%';
                        },
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Probability Density',
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

function createQQPlot() {
    const ctx = document.getElementById('qqPlotChart');
    if (!ctx) return;

    const distData = analysisData.distribution_data;
    const variantA = distData.variant_a;
    const variantB = distData.variant_b;

    // Helper function to calculate inverse normal CDF (approximation)
    function inverseNormalCDF(p) {
        // Approximation of inverse normal CDF for p between 0 and 1
        if (p <= 0 || p >= 1) return 0;

        const a1 = -3.969683028665376e+01;
        const a2 = 2.209460984245205e+02;
        const a3 = -2.759285104469687e+02;
        const a4 = 1.383577518672690e+02;
        const a5 = -3.066479806614716e+01;
        const a6 = 2.506628277459239e+00;

        const b1 = -5.447609879822406e+01;
        const b2 = 1.615858368580409e+02;
        const b3 = -1.556989798598866e+02;
        const b4 = 6.680131188771972e+01;
        const b5 = -1.328068155288572e+01;

        const c1 = -7.784894002430293e-03;
        const c2 = -3.223964580411365e-01;
        const c3 = -2.400758277161838e+00;
        const c4 = -2.549732539343734e+00;
        const c5 = 4.374664141464968e+00;
        const c6 = 2.938163982698783e+00;

        const d1 = 7.784695709041462e-03;
        const d2 = 3.224671290700398e-01;
        const d3 = 2.445134137142996e+00;
        const d4 = 3.754408661907416e+00;

        const pLow = 0.02425;
        const pHigh = 1 - pLow;

        let q, r, x;

        if (p < pLow) {
            q = Math.sqrt(-2 * Math.log(p));
            x = (((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) /
                ((((d1 * q + d2) * q + d3) * q + d4) * q + 1);
        } else if (p <= pHigh) {
            q = p - 0.5;
            r = q * q;
            x = (((((a1 * r + a2) * r + a3) * r + a4) * r + a5) * r + a6) * q /
                (((((b1 * r + b2) * r + b3) * r + b4) * r + b5) * r + 1);
        } else {
            q = Math.sqrt(-2 * Math.log(1 - p));
            x = -(((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) /
                ((((d1 * q + d2) * q + d3) * q + d4) * q + 1);
        }

        return x;
    }

    // Generate sample quantiles from the normal distribution
    function generateQuantiles(mean, stdError, numPoints) {
        const quantiles = [];
        for (let i = 1; i < numPoints; i++) {
            const p = i / numPoints;
            const theoreticalQuantile = inverseNormalCDF(p);
            const sampleQuantile = (inverseNormalCDF(p) * stdError + mean) * 100; // Convert to percentage
            quantiles.push({
                x: theoreticalQuantile,
                y: sampleQuantile
            });
        }
        return quantiles;
    }

    const numPoints = 50;
    const quantilesA = generateQuantiles(variantA.mean, variantA.std_error, numPoints);
    const quantilesB = generateQuantiles(variantB.mean, variantB.std_error, numPoints);

    // Generate reference line (y = x transformed to match scale)
    const minTheoreticalQ = -3;
    const maxTheoreticalQ = 3;
    const referenceLine = [
        { x: minTheoreticalQ, y: (minTheoreticalQ * Math.max(variantA.std_error, variantB.std_error) + Math.min(variantA.mean, variantB.mean)) * 100 },
        { x: maxTheoreticalQ, y: (maxTheoreticalQ * Math.max(variantA.std_error, variantB.std_error) + Math.max(variantA.mean, variantB.mean)) * 100 }
    ];

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Variant A',
                    data: quantilesA,
                    backgroundColor: 'rgba(46, 62, 74, 0.6)',
                    borderColor: 'rgba(46, 62, 74, 1)',
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'Variant B',
                    data: quantilesB,
                    backgroundColor: 'rgba(16, 185, 129, 0.6)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'Reference Line (Perfect Normal)',
                    data: referenceLine,
                    borderColor: 'rgba(239, 68, 68, 0.8)',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    type: 'line',
                    showLine: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            if (context.dataset.label.includes('Reference')) {
                                return null;
                            }
                            return [
                                `${context.dataset.label}`,
                                `Theoretical: ${context.parsed.x.toFixed(2)}`,
                                `Sample: ${context.parsed.y.toFixed(2)}%`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Theoretical Quantiles (Standard Normal)',
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Sample Quantiles (Conversion Rate %)',
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(2) + '%';
                        },
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}