/**
 * AI Description Generator
 *
 * Handles the AI-powered test description generation functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generateDescriptionBtn');
    const testNameInput = document.getElementById('testName');
    const descriptionTextarea = document.getElementById('testDescription');

    if (generateBtn && testNameInput && descriptionTextarea) {
        generateBtn.addEventListener('click', async function() {
            const testName = testNameInput.value.trim();

            // Validate test name
            if (!testName) {
                alert('Please enter a test name first');
                testNameInput.focus();
                return;
            }

            // Disable button and show loading state
            generateBtn.disabled = true;
            const originalText = generateBtn.innerHTML;
            generateBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
                    <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z"/>
                </svg>
                Generating...
            `;

            try {
                // Call the API
                const response = await fetch('/api/generate-description', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        test_name: testName
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Update the description textarea with the generated content
                    descriptionTextarea.value = data.description;

                    // Add a subtle animation to show the change
                    descriptionTextarea.style.transition = 'background-color 0.3s ease';
                    descriptionTextarea.style.backgroundColor = '#e8f5e9';
                    setTimeout(() => {
                        descriptionTextarea.style.backgroundColor = '';
                    }, 1000);
                } else {
                    alert('Failed to generate description: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while generating the description. Please try again.');
            } finally {
                // Re-enable button and restore original text
                generateBtn.disabled = false;
                generateBtn.innerHTML = originalText;
            }
        });
    }
});