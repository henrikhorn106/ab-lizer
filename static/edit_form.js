/**
 * Edit Form Handler
 *
 * Shows loading overlay when the edit form is submitted
 */

document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('edit-form');
    const loadingOverlay = document.getElementById('loadingOverlay');

    if (editForm && loadingOverlay) {
        editForm.addEventListener('submit', function(event) {
            // Show loading overlay
            loadingOverlay.classList.add('active');

            // Let the form submit normally
            // The page will reload with the updated data
        });
    }
});