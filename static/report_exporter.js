/**
 * Report Exporter
 *
 * Handles PDF, PowerPoint, and other export formats for AB test reports
 */

document.addEventListener('DOMContentLoaded', function() {
    const exportBtn = document.getElementById('exportBtn');
    const exportMenu = document.getElementById('exportMenu');
    const exportOptions = document.querySelectorAll('.export-option');

    // Toggle export dropdown
    if (exportBtn) {
        exportBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            exportMenu.classList.toggle('show');
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (exportMenu && !exportMenu.contains(e.target) && e.target !== exportBtn) {
            exportMenu.classList.remove('show');
        }
    });

    // Handle export option clicks
    exportOptions.forEach(option => {
        option.addEventListener('click', async function(e) {
            e.stopPropagation();
            const format = this.getAttribute('data-format');
            const template = this.getAttribute('data-template');
            const action = this.getAttribute('data-action');

            // Close dropdown
            exportMenu.classList.remove('show');

            // Check if report is loaded
            if (!window.currentTestData) {
                alert('Please select a test first to generate a report.');
                return;
            }

            // Show loading state
            const originalText = this.querySelector('.export-title').textContent;
            this.querySelector('.export-title').textContent = 'Exporting...';
            this.disabled = true;

            try {
                if (action === 'clipboard') {
                    await copyToClipboard();
                } else if (action === 'custom') {
                    showCustomExportModal();
                } else if (format === 'print') {
                    window.print();
                } else if (format === 'pdf') {
                    await exportToPDF(template);
                } else if (format === 'pptx') {
                    await exportToPowerPoint(template);
                }
            } catch (error) {
                console.error('Export error:', error);
                alert('Export failed: ' + error.message);
            } finally {
                // Restore button state
                this.querySelector('.export-title').textContent = originalText;
                this.disabled = false;
            }
        });
    });

    // Export Templates Configuration
    const templates = {
        executive: {
            name: 'Executive Summary',
            sections: ['header', 'keyResults', 'executiveSummary', 'aiRecommendations']
        },
        technical: {
            name: 'Technical Analysis',
            sections: ['header', 'keyResults', 'executiveSummary', 'variantPerformance',
                      'statisticalDetails', 'charts']
        },
        full: {
            name: 'Full Report',
            sections: ['header', 'keyResults', 'executiveSummary', 'variantPerformance',
                      'conversionFunnel', 'aiRecommendations', 'statisticalDetails', 'charts']
        }
    };

    /**
     * Export to PDF using jsPDF
     */
    async function exportToPDF(template) {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('p', 'mm', 'a4');
        const data = window.currentTestData;
        const templateConfig = templates[template] || templates.full;

        let yPos = 20;
        const pageWidth = 210;
        const pageHeight = 297;
        const margin = 20;
        const contentWidth = pageWidth - 2 * margin;

        // Helper function to add new page if needed
        function checkPageBreak(neededHeight) {
            if (yPos + neededHeight > pageHeight - margin) {
                doc.addPage();
                yPos = margin;
                return true;
            }
            return false;
        }

        // Header
        if (templateConfig.sections.includes('header')) {
            doc.setFontSize(24);
            doc.setTextColor(46, 62, 74);
            doc.text(data.test.name, margin, yPos);
            yPos += 10;

            doc.setFontSize(10);
            doc.setTextColor(100, 100, 100);
            doc.text(`Created: ${data.test.created_at}`, margin, yPos);
            yPos += 5;
            doc.text(`Main Metric: ${data.test.metric}`, margin, yPos);
            yPos += 15;
        }

        // Key Results
        if (templateConfig.sections.includes('keyResults') && data.report) {
            checkPageBreak(40);
            doc.setFontSize(16);
            doc.setTextColor(46, 62, 74);
            doc.text('Key Results', margin, yPos);
            yPos += 10;

            doc.setFontSize(12);

            // Significance
            const sigColor = data.report.significance ? [16, 185, 129] : [239, 68, 68];
            doc.setTextColor(...sigColor);
            doc.text(`Statistical Significance: ${data.report.significance ? 'Significant' : 'Not Significant'}`, margin, yPos);
            yPos += 8;

            // Performance
            const perfValue = data.report.increase_percent || 0;
            const perfColor = perfValue > 0 ? [16, 185, 129] : perfValue < 0 ? [239, 68, 68] : [100, 100, 100];
            doc.setTextColor(...perfColor);
            doc.text(`Performance Change: ${perfValue > 0 ? '+' : ''}${perfValue}%`, margin, yPos);
            yPos += 8;

            // p-Value
            doc.setTextColor(46, 62, 74);
            doc.text(`p-value: ${data.report.p_value}`, margin, yPos);
            yPos += 15;
        }

        // Executive Summary
        if (templateConfig.sections.includes('executiveSummary') && data.report) {
            checkPageBreak(30);
            doc.setFontSize(16);
            doc.setTextColor(46, 62, 74);
            doc.text('Executive Summary', margin, yPos);
            yPos += 10;

            doc.setFontSize(11);
            const summaryLines = doc.splitTextToSize(data.report.summary || 'No summary available.', contentWidth);
            summaryLines.forEach(line => {
                checkPageBreak(7);
                doc.text(line, margin, yPos);
                yPos += 7;
            });
            yPos += 10;
        }

        // Variant Performance
        if (templateConfig.sections.includes('variantPerformance') && data.variants) {
            checkPageBreak(40);
            doc.setFontSize(16);
            doc.setTextColor(46, 62, 74);
            doc.text('Variant Performance', margin, yPos);
            yPos += 10;

            data.variants.forEach(variant => {
                checkPageBreak(25);
                doc.setFontSize(12);
                doc.setFont(undefined, 'bold');
                doc.text(variant.name, margin, yPos);
                yPos += 7;

                doc.setFont(undefined, 'normal');
                doc.setFontSize(10);
                doc.text(`Sessions: ${variant.impressions.toLocaleString()}`, margin + 5, yPos);
                yPos += 5;
                doc.text(`Conversions: ${variant.conversions.toLocaleString()}`, margin + 5, yPos);
                yPos += 5;
                doc.text(`Conversion Rate: ${variant.conversion_rate}%`, margin + 5, yPos);
                yPos += 10;
            });
        }

        // AI Recommendations
        if (templateConfig.sections.includes('aiRecommendations') && data.report && data.report.ai_recommendation) {
            checkPageBreak(30);
            doc.setFontSize(16);
            doc.setTextColor(46, 62, 74);
            doc.text('Strategic Recommendations', margin, yPos);
            yPos += 10;

            const recommendation = data.report.ai_recommendation;
            doc.setFontSize(10);

            if (typeof recommendation === 'object' && recommendation.decision) {
                // Structured recommendation
                doc.setFont(undefined, 'bold');
                const decisionLines = doc.splitTextToSize(recommendation.decision, contentWidth);
                decisionLines.forEach(line => {
                    checkPageBreak(6);
                    doc.text(line, margin, yPos);
                    yPos += 6;
                });
                yPos += 5;

                doc.setFont(undefined, 'normal');
                if (recommendation.topics && Array.isArray(recommendation.topics)) {
                    recommendation.topics.forEach(topic => {
                        checkPageBreak(15);
                        doc.setFont(undefined, 'bold');
                        doc.text(`• ${topic.title}`, margin, yPos);
                        yPos += 6;
                        doc.setFont(undefined, 'normal');
                        const contentLines = doc.splitTextToSize(topic.content, contentWidth - 5);
                        contentLines.forEach(line => {
                            checkPageBreak(5);
                            doc.text(line, margin + 5, yPos);
                            yPos += 5;
                        });
                        yPos += 3;
                    });
                }
            } else {
                // Plain text recommendation
                const recLines = doc.splitTextToSize(recommendation, contentWidth);
                recLines.forEach(line => {
                    checkPageBreak(6);
                    doc.text(line, margin, yPos);
                    yPos += 6;
                });
            }
            yPos += 10;
        }

        // Statistical Details
        if (templateConfig.sections.includes('statisticalDetails') && data.variants) {
            checkPageBreak(30);
            doc.setFontSize(16);
            doc.setTextColor(46, 62, 74);
            doc.text('Statistical Details', margin, yPos);
            yPos += 10;

            const totalSessions = data.variants.reduce((sum, v) => sum + v.impressions, 0);
            const totalConversions = data.variants.reduce((sum, v) => sum + v.conversions, 0);
            const overallRate = ((totalConversions / totalSessions) * 100).toFixed(2);

            doc.setFontSize(10);
            doc.text(`Total Sessions: ${totalSessions.toLocaleString()}`, margin, yPos);
            yPos += 6;
            doc.text(`Total Conversions: ${totalConversions.toLocaleString()}`, margin, yPos);
            yPos += 6;
            doc.text(`Overall Conversion Rate: ${overallRate}%`, margin, yPos);
            yPos += 6;
            doc.text(`Statistical Significance: ${data.report && data.report.significance ? 'Yes (p < 0.05)' : 'No (p ≥ 0.05)'}`, margin, yPos);
        }

        // Add footer with page numbers
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.setTextColor(150, 150, 150);
            doc.text(`Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
            doc.text('Generated with AB Lizer', pageWidth - margin, pageHeight - 10, { align: 'right' });
        }

        // Save the PDF
        const filename = `${templateConfig.name}_${data.test.name.replace(/[^a-z0-9]/gi, '_')}.pdf`;
        doc.save(filename);
    }

    /**
     * Export to PowerPoint using PptxGenJS
     */
    async function exportToPowerPoint(template) {
        const pptx = new PptxGenJS();
        const data = window.currentTestData;
        const templateConfig = templates[template] || templates.full;

        // Set presentation properties
        pptx.author = 'AB Lizer';
        pptx.company = 'AB Testing Platform';
        pptx.title = `${data.test.name} - Report`;

        // Color scheme
        const colors = {
            primary: '2E3E4A',
            accent: '317AAE',
            success: '10B981',
            danger: 'EF4444',
            light: 'F7F7F7'
        };

        // Slide 1: Title Slide
        let slide = pptx.addSlide();
        slide.background = { color: colors.primary };
        slide.addText(data.test.name, {
            x: 0.5, y: 2, w: 9, h: 1.5,
            fontSize: 44, bold: true, color: 'FFFFFF', align: 'center'
        });
        slide.addText('A/B Test Results Report', {
            x: 0.5, y: 3.5, w: 9, h: 0.5,
            fontSize: 24, color: 'CCCCCC', align: 'center'
        });
        slide.addText(`Created: ${data.test.created_at}`, {
            x: 0.5, y: 5, w: 9, h: 0.3,
            fontSize: 14, color: 'AAAAAA', align: 'center'
        });

        // Slide 2: Key Results (if included)
        if (templateConfig.sections.includes('keyResults') && data.report) {
            slide = pptx.addSlide();
            slide.addText('Key Results', {
                x: 0.5, y: 0.5, w: 9, h: 0.6,
                fontSize: 32, bold: true, color: colors.primary
            });

            const results = [
                {
                    title: 'Statistical Significance',
                    value: data.report.significance ? 'Significant' : 'Not Significant',
                    color: data.report.significance ? colors.success : colors.danger
                },
                {
                    title: 'Performance Change',
                    value: `${data.report.increase_percent > 0 ? '+' : ''}${data.report.increase_percent}%`,
                    color: data.report.increase_percent > 0 ? colors.success : colors.danger
                },
                {
                    title: 'Confidence Level',
                    value: `p-value: ${data.report.p_value}`,
                    color: colors.primary
                }
            ];

            results.forEach((result, index) => {
                const x = 0.5 + (index * 3.2);
                slide.addShape(pptx.ShapeType.rect, {
                    x: x, y: 2, w: 3, h: 2,
                    fill: { color: colors.light }
                });
                slide.addText(result.title, {
                    x: x, y: 2.2, w: 3, h: 0.4,
                    fontSize: 14, color: '666666', align: 'center'
                });
                slide.addText(result.value, {
                    x: x, y: 2.8, w: 3, h: 0.8,
                    fontSize: 24, bold: true, color: result.color, align: 'center'
                });
            });
        }

        // Slide 3: Executive Summary (if included)
        if (templateConfig.sections.includes('executiveSummary') && data.report) {
            slide = pptx.addSlide();
            slide.addText('Executive Summary', {
                x: 0.5, y: 0.5, w: 9, h: 0.6,
                fontSize: 32, bold: true, color: colors.primary
            });
            slide.addText(data.report.summary || 'No summary available.', {
                x: 0.5, y: 1.5, w: 9, h: 3.5,
                fontSize: 16, color: '333333', valign: 'top'
            });
        }

        // Slide 4: Variant Performance (if included)
        if (templateConfig.sections.includes('variantPerformance') && data.variants) {
            slide = pptx.addSlide();
            slide.addText('Variant Performance', {
                x: 0.5, y: 0.5, w: 9, h: 0.6,
                fontSize: 32, bold: true, color: colors.primary
            });

            data.variants.forEach((variant, index) => {
                const x = 0.5 + (index * 4.7);
                slide.addShape(pptx.ShapeType.rect, {
                    x: x, y: 1.5, w: 4.3, h: 3,
                    fill: { color: colors.light }
                });
                slide.addText(variant.name, {
                    x: x + 0.2, y: 1.7, w: 4, h: 0.5,
                    fontSize: 20, bold: true, color: colors.primary
                });
                slide.addText(`Sessions: ${variant.impressions.toLocaleString()}`, {
                    x: x + 0.2, y: 2.4, w: 4, h: 0.3,
                    fontSize: 14, color: '666666'
                });
                slide.addText(`Conversions: ${variant.conversions.toLocaleString()}`, {
                    x: x + 0.2, y: 2.8, w: 4, h: 0.3,
                    fontSize: 14, color: '666666'
                });
                slide.addText(`Conversion Rate: ${variant.conversion_rate}%`, {
                    x: x + 0.2, y: 3.6, w: 4, h: 0.5,
                    fontSize: 18, bold: true, color: colors.accent
                });
            });
        }

        // Slide 5: AI Recommendations (if included)
        if (templateConfig.sections.includes('aiRecommendations') && data.report && data.report.ai_recommendation) {
            slide = pptx.addSlide();
            slide.addText('Strategic Recommendations', {
                x: 0.5, y: 0.5, w: 9, h: 0.6,
                fontSize: 32, bold: true, color: colors.primary
            });

            const recommendation = data.report.ai_recommendation;
            let yPos = 1.5;

            if (typeof recommendation === 'object' && recommendation.decision) {
                slide.addText(recommendation.decision, {
                    x: 0.5, y: yPos, w: 9, h: 0.8,
                    fontSize: 16, bold: true, color: colors.accent
                });
                yPos += 1;

                if (recommendation.topics && Array.isArray(recommendation.topics)) {
                    recommendation.topics.slice(0, 3).forEach(topic => {
                        slide.addText(`• ${topic.title}`, {
                            x: 0.5, y: yPos, w: 9, h: 0.4,
                            fontSize: 14, bold: true, color: colors.primary
                        });
                        yPos += 0.4;
                        slide.addText(topic.content, {
                            x: 0.8, y: yPos, w: 8.7, h: 0.6,
                            fontSize: 12, color: '666666'
                        });
                        yPos += 0.8;
                    });
                }
            } else {
                slide.addText(recommendation, {
                    x: 0.5, y: yPos, w: 9, h: 3.5,
                    fontSize: 14, color: '333333', valign: 'top'
                });
            }
        }

        // Save the presentation
        const filename = `${templateConfig.name}_${data.test.name.replace(/[^a-z0-9]/gi, '_')}.pptx`;
        await pptx.writeFile({ fileName: filename });
    }

    /**
     * Copy report summary to clipboard
     */
    async function copyToClipboard() {
        const data = window.currentTestData;

        const text = `
A/B Test Results: ${data.test.name}
========================================

Main Metric: ${data.test.metric}
Created: ${data.test.created_at}

KEY RESULTS
-----------
Statistical Significance: ${data.report ? (data.report.significance ? 'Significant ✓' : 'Not Significant ✗') : 'N/A'}
Performance Change: ${data.report ? (data.report.increase_percent > 0 ? '+' : '') + data.report.increase_percent + '%' : 'N/A'}
p-value: ${data.report ? data.report.p_value : 'N/A'}

EXECUTIVE SUMMARY
-----------------
${data.report ? data.report.summary : 'No summary available.'}

VARIANT PERFORMANCE
-------------------
${data.variants.map(v => `
${v.name}:
  Sessions: ${v.impressions.toLocaleString()}
  Conversions: ${v.conversions.toLocaleString()}
  Conversion Rate: ${v.conversion_rate}%
`).join('\n')}

Generated with AB Lizer
        `.trim();

        try {
            await navigator.clipboard.writeText(text);
            alert('Report copied to clipboard!');
        } catch (err) {
            console.error('Failed to copy:', err);
            alert('Failed to copy to clipboard. Please try again.');
        }
    }

    /**
     * Show custom export modal (placeholder for future implementation)
     */
    function showCustomExportModal() {
        alert('Custom export options coming soon!\n\nFor now, use the quick export options above.');
    }
});
