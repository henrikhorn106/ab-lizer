// Modal Elemente
const modal_variant = document.getElementById('variantModal');
const addVariantBtn = document.getElementById('addVariantBtn');
const closeVariantBtn = document.getElementById('closeVariantBtn');
const cancelVariantBtn = document.getElementById('cancelVariantBtn');
const variantForm = document.getElementById('variantForm');
const loadingOverlay = document.getElementById('loadingOverlay');

// Only add event listeners if elements exist
if (modal_variant && addVariantBtn && closeVariantBtn && cancelVariantBtn) {
    // Modal öffnen
    addVariantBtn.addEventListener('click', () => {
        modal_variant.style.display = 'block';
    });

    // Modal schließen
    closeVariantBtn.addEventListener('click', () => {
        modal_variant.style.display = 'none';
    });

    cancelVariantBtn.addEventListener('click', () => {
        modal_variant.style.display = 'none';
    });

    // Modal schließen bei Klick außerhalb
    window.addEventListener('click', (event) => {
        if (event.target === modal_variant) {
            modal_variant.style.display = 'none';
        }
    });
}

// Show loading overlay when form is submitted
if (variantForm && loadingOverlay) {
    variantForm.addEventListener('submit', (event) => {
        // Show loading overlay
        loadingOverlay.classList.add('active');

        // Close the modal
        if (modal_variant) {
            modal_variant.style.display = 'none';
        }

        // Let the form submit normally
        // The page will reload with the new data
    });
}