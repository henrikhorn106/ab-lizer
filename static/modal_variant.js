// Modal Elemente
const modal_variant = document.getElementById('variantModal');
const addVariantBtn = document.getElementById('addVariantBtn');
const closeVariantBtn = document.querySelector('.close');
const cancelVariantBtn = document.getElementById('cancelBtn');

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