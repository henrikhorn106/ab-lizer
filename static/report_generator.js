/**
 * Report Generator with Drag-and-Drop Presentation Builder
 *
 * Handles stakeholder report generation for AB tests with customizable layouts
 */

document.addEventListener('DOMContentLoaded', function() {
    const testSelector = document.getElementById('testSelector');
    const reportContainer = document.getElementById('reportContainer');
    const builderControls = document.getElementById('builderControls');
    const exportDropdown = document.getElementById('exportDropdown');
    const toggleBuilderBtn = document.getElementById('toggleBuilderBtn');

    // Make current test data globally accessible for export
    window.currentTestData = null;

    let currentCharts = {
        conversion: null,
        sample: null
    };

    let draggedElement = null;

    // Chart colors matching the theme
    const colors = {
        primary: '#2E3E4A',
        accent: '#317AAE',
        gradient: 'rgba(49, 122, 174, 0.8)',
        gradientLight: 'rgba(49, 122, 174, 0.2)',
        secondary: '#F7F7F7',
        success: 'rgba(16, 185, 129, 0.8)',
        successLight: 'rgba(16, 185, 129, 0.2)',
        danger: 'rgba(239, 68, 68, 0.8)',
        dangerLight: 'rgba(239, 68, 68, 0.2)'
    };

    // Test selection handler
    if (testSelector) {
        testSelector.addEventListener('change', function() {
            const testId = parseInt(this.value);
            if (testId) {
                generateReport(testId);
            } else {
                reportContainer.style.display = 'none';
                builderControls.style.display = 'none';
                exportDropdown.style.display = 'none';
                toggleBuilderBtn.style.display = 'none';
            }
        });
    }

    // Toggle builder panel
    if (toggleBuilderBtn) {
        toggleBuilderBtn.addEventListener('click', function() {
            if (builderControls.style.display === 'none') {
                builderControls.style.display = 'block';
                this.textContent = 'Hide Customization';
            } else {
                builderControls.style.display = 'none';
                this.textContent = 'Customize Report';
            }
        });
    }

    // Initialize drag and drop
    function initializeDragAndDrop() {
        const sections = document.querySelectorAll('.report-section-wrapper');

        sections.forEach(section => {
            section.addEventListener('dragstart', handleDragStart);
            section.addEventListener('dragover', handleDragOver);
            section.addEventListener('drop', handleDrop);
            section.addEventListener('dragend', handleDragEnd);
            section.addEventListener('dragenter', handleDragEnter);
            section.addEventListener('dragleave', handleDragLeave);
        });
    }

    function handleDragStart(e) {
        draggedElement = this;
        this.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', this.innerHTML);
    }

    function handleDragOver(e) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        e.dataTransfer.dropEffect = 'move';
        return false;
    }

    function handleDragEnter(e) {
        if (this !== draggedElement) {
            this.classList.add('drag-over');
        }
    }

    function handleDragLeave(e) {
        this.classList.remove('drag-over');
    }

    function handleDrop(e) {
        if (e.stopPropagation) {
            e.stopPropagation();
        }

        if (draggedElement !== this) {
            // Swap the elements
            const allSections = Array.from(document.querySelectorAll('.report-section-wrapper'));
            const draggedIndex = allSections.indexOf(draggedElement);
            const targetIndex = allSections.indexOf(this);

            if (draggedIndex < targetIndex) {
                this.parentNode.insertBefore(draggedElement, this.nextSibling);
            } else {
                this.parentNode.insertBefore(draggedElement, this);
            }
        }

        this.classList.remove('drag-over');
        return false;
    }

    function handleDragEnd(e) {
        this.classList.remove('dragging');

        // Remove drag-over class from all sections
        document.querySelectorAll('.report-section-wrapper').forEach(section => {
            section.classList.remove('drag-over');
        });
    }

    // Initialize section toggles
    function initializeSectionToggles() {
        const toggles = document.querySelectorAll('.section-toggle');

        toggles.forEach(toggle => {
            toggle.addEventListener('change', function() {
                const sectionName = this.getAttribute('data-section');
                const section = document.querySelector(`.report-section-wrapper[data-section="${sectionName}"]`);

                if (section) {
                    if (this.checked) {
                        section.style.display = 'block';
                    } else {
                        section.style.display = 'none';
                    }
                }
            });
        });
    }

    // Reset layout to default
    document.getElementById('resetLayoutBtn')?.addEventListener('click', function() {
        // Reset order
        const container = document.getElementById('reportContainer');
        const sections = Array.from(document.querySelectorAll('.report-section-wrapper'));
        const defaultOrder = ['header', 'keyResults', 'executiveSummary', 'variantPerformance',
                             'conversionFunnel', 'aiRecommendations', 'statisticalDetails', 'charts'];

        sections.sort((a, b) => {
            const aIndex = defaultOrder.indexOf(a.getAttribute('data-section'));
            const bIndex = defaultOrder.indexOf(b.getAttribute('data-section'));
            return aIndex - bIndex;
        });

        sections.forEach(section => container.appendChild(section));

        // Reset visibility
        document.querySelectorAll('.section-toggle').forEach(toggle => {
            toggle.checked = true;
            const sectionName = toggle.getAttribute('data-section');
            const section = document.querySelector(`.report-section-wrapper[data-section="${sectionName}"]`);
            if (section) section.style.display = 'block';
        });

        alert('Layout reset to default!');
    });

    // Save layout
    document.getElementById('saveLayoutBtn')?.addEventListener('click', function() {
        const sections = Array.from(document.querySelectorAll('.report-section-wrapper'));
        const layout = {
            order: sections.map(s => s.getAttribute('data-section')),
            visibility: {}
        };

        document.querySelectorAll('.section-toggle').forEach(toggle => {
            layout.visibility[toggle.getAttribute('data-section')] = toggle.checked;
        });

        localStorage.setItem('reportLayout', JSON.stringify(layout));
        alert('Layout saved successfully!');
    });

    // Load saved layout
    document.getElementById('loadLayoutBtn')?.addEventListener('click', function() {
        const savedLayout = localStorage.getItem('reportLayout');

        if (!savedLayout) {
            alert('No saved layout found!');
            return;
        }

        const layout = JSON.parse(savedLayout);
        const container = document.getElementById('reportContainer');
        const sections = Array.from(document.querySelectorAll('.report-section-wrapper'));

        // Reorder sections
        sections.sort((a, b) => {
            const aIndex = layout.order.indexOf(a.getAttribute('data-section'));
            const bIndex = layout.order.indexOf(b.getAttribute('data-section'));
            return aIndex - bIndex;
        });

        sections.forEach(section => container.appendChild(section));

        // Apply visibility
        document.querySelectorAll('.section-toggle').forEach(toggle => {
            const sectionName = toggle.getAttribute('data-section');
            const visible = layout.visibility[sectionName];
            toggle.checked = visible;

            const section = document.querySelector(`.report-section-wrapper[data-section="${sectionName}"]`);
            if (section) {
                section.style.display = visible ? 'block' : 'none';
            }
        });

        alert('Layout loaded successfully!');
    });

    function generateReport(testId) {
        // Find test data
        const test = testsData.find(t => t.id === testId);
        if (!test) {
            console.error('Test not found');
            return;
        }

        // Find variants for this test
        const testVariants = variantsData.filter(v => v.test_id === testId);
        if (testVariants.length < 2) {
            alert('This test does not have enough variants for a report. Please select a test with at least 2 variants.');
            testSelector.value = '';
            return;
        }

        // Find report for this test
        const report = reportsData.find(r => r.test_id === testId);

        // Populate report
        populateHeader(test);
        populateKeyResults(report);
        populateExecutiveSummary(report);
        populateVariantComparison(testVariants);
        populateFunnelVisualization(testVariants);
        populateAIRecommendations(report);
        populateStatisticalDetails(testVariants, report);
        createReportCharts(testVariants);

        // Store current test data globally for export
        window.currentTestData = {
            test: test,
            variants: testVariants,
            report: report
        };

        // Show report container and controls
        reportContainer.style.display = 'block';
        builderControls.style.display = 'block';
        exportDropdown.style.display = 'inline-block';
        toggleBuilderBtn.style.display = 'inline-block';

        // Initialize drag and drop
        initializeDragAndDrop();
        initializeSectionToggles();

        // Scroll to report
        reportContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function populateHeader(test) {
        document.getElementById('reportTestName').textContent = test.name;
        document.getElementById('reportDate').textContent = `Created: ${test.created_at}`;
        document.getElementById('reportMetric').textContent = `Main Metric: ${test.metric}`;
    }

    function populateKeyResults(report) {
        if (!report) {
            document.getElementById('reportSignificance').textContent = 'No data available';
            document.getElementById('reportPerformance').textContent = 'No data available';
            document.getElementById('reportPValue').textContent = 'No data available';
            return;
        }

        // Statistical Significance
        const significanceEl = document.getElementById('reportSignificance');
        significanceEl.textContent = report.significance ? 'Significant' : 'Not Significant';
        significanceEl.className = 'result-value ' + (report.significance ? 'positive' : 'negative');

        // Performance Change
        const performanceEl = document.getElementById('reportPerformance');
        const performanceValue = report.increase_percent || 0;
        performanceEl.textContent = `${performanceValue > 0 ? '+' : ''}${performanceValue}%`;
        performanceEl.className = 'result-value ' + (performanceValue > 0 ? 'positive' : performanceValue < 0 ? 'negative' : '');

        // p-Value
        const pValueEl = document.getElementById('reportPValue');
        const pValue = parseFloat(report.p_value);
        pValueEl.textContent = `p-value: ${report.p_value}`;
        pValueEl.className = 'result-value ' + (pValue < 0.05 ? 'positive' : 'negative');
    }

    function populateExecutiveSummary(report) {
        const summaryEl = document.getElementById('reportSummary');
        if (report && report.summary) {
            summaryEl.textContent = report.summary;
        } else {
            summaryEl.textContent = 'No executive summary available for this test.';
        }
    }

    function populateVariantComparison(variants) {
        const container = document.getElementById('variantComparison');
        container.innerHTML = '';

        variants.forEach(variant => {
            const variantCard = document.createElement('div');
            variantCard.className = 'metrics-card';
            variantCard.innerHTML = `
                <h4>${variant.name}</h4>
                <div class="metric-row">
                    <span class="metric-label">Total Sessions:</span>
                    <span class="metric-value">${variant.impressions.toLocaleString()}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Total Conversions:</span>
                    <span class="metric-value">${variant.conversions.toLocaleString()}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Conversion Rate:</span>
                    <span class="metric-value highlight">${variant.conversion_rate}%</span>
                </div>
            `;
            container.appendChild(variantCard);
        });
    }

    function populateFunnelVisualization(variants) {
        const container = document.getElementById('funnelVisualization');
        container.innerHTML = '';

        variants.forEach(variant => {
            const funnelCard = document.createElement('div');
            funnelCard.className = 'funnel-container';
            funnelCard.innerHTML = `
                <h4>${variant.name}</h4>
                <div class="funnel">
                    <div class="funnel-stage" style="width: 100%;">
                        <span>Sessions</span>
                        <strong>${variant.impressions.toLocaleString()}</strong>
                    </div>
                    <div class="funnel-stage" style="width: ${variant.conversion_rate}%;">
                        <span>Conversions</span>
                        <strong>${variant.conversions.toLocaleString()}</strong>
                    </div>
                </div>
            `;
            container.appendChild(funnelCard);
        });
    }

    function populateAIRecommendations(report) {
        const container = document.getElementById('aiRecommendations');

        if (!report || !report.ai_recommendation) {
            container.innerHTML = '<p>No AI recommendations available for this test.</p>';
            return;
        }

        const recommendation = report.ai_recommendation;

        // Check if it's structured JSON or plain text
        if (typeof recommendation === 'object' && recommendation.decision) {
            // Structured recommendation
            let html = `<div class="recommendation-decision"><strong>${recommendation.decision}</strong></div>`;
            html += '<div class="recommendation-topics">';

            if (recommendation.topics && Array.isArray(recommendation.topics)) {
                recommendation.topics.forEach(topic => {
                    html += `
                        <div class="recommendation-topic">
                            <h5>${topic.title}</h5>
                            <p>${topic.content}</p>
                        </div>
                    `;
                });
            }

            html += '</div>';
            container.innerHTML = html;
        } else {
            // Plain text recommendation
            const paragraphs = recommendation.split('\n\n');
            let html = '<div class="recommendation-text">';
            paragraphs.forEach(para => {
                if (para.trim()) {
                    html += `<p>${para.trim()}</p>`;
                }
            });
            html += '</div>';
            container.innerHTML = html;
        }
    }

    function populateStatisticalDetails(variants, report) {
        const container = document.getElementById('statisticalDetails');

        if (!variants || variants.length < 2) {
            container.innerHTML = '<p>Insufficient data for statistical analysis.</p>';
            return;
        }

        const totalSessions = variants.reduce((sum, v) => sum + v.impressions, 0);
        const totalConversions = variants.reduce((sum, v) => sum + v.conversions, 0);
        const overallRate = ((totalConversions / totalSessions) * 100).toFixed(2);

        container.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">Total Sessions:</span>
                <span class="stat-value">${totalSessions.toLocaleString()}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Conversions:</span>
                <span class="stat-value">${totalConversions.toLocaleString()}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Overall Conversion Rate:</span>
                <span class="stat-value">${overallRate}%</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Statistical Significance:</span>
                <span class="stat-value">${report && report.significance ? 'Yes (p < 0.05)' : 'No (p ≥ 0.05)'}</span>
            </div>
        `;
    }

    function createReportCharts(variants) {
        // Destroy existing charts
        if (currentCharts.conversion) {
            currentCharts.conversion.destroy();
        }
        if (currentCharts.sample) {
            currentCharts.sample.destroy();
        }

        // Create Conversion Rate Chart
        const conversionCtx = document.getElementById('reportConversionChart');
        if (conversionCtx) {
            const labels = variants.map(v => v.name);
            const conversionRates = variants.map(v => v.conversion_rate);

            const backgroundColor = conversionRates.map((rate, index) => {
                if (index === 0) return colors.primary;
                return rate > conversionRates[0] ? colors.success : colors.danger;
            });

            currentCharts.conversion = new Chart(conversionCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Conversion Rate (%)',
                        data: conversionRates,
                        backgroundColor: backgroundColor,
                        borderColor: backgroundColor,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Conversion Rate (%)'
                            }
                        }
                    }
                }
            });
        }

        // Create Sample Size Chart
        const sampleCtx = document.getElementById('reportSampleChart');
        if (sampleCtx) {
            const labels = variants.map(v => v.name);
            const impressions = variants.map(v => v.impressions);

            currentCharts.sample = new Chart(sampleCtx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Sample Size',
                        data: impressions,
                        backgroundColor: [colors.primary, colors.accent],
                        borderColor: '#ffffff',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        title: {
                            display: false
                        }
                    }
                }
            });
        }
    }
});
