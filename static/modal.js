// Modal Elemente
const modal = document.getElementById('testModal');
const addTestBtn = document.getElementById('addTestBtn');
const closeBtn = document.querySelector('.close');
const cancelBtn = document.getElementById('cancelBtn');

// Modal öffnen
addTestBtn.addEventListener('click', () => {
    modal.style.display = 'block';
});

// Modal schließen
closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

cancelBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

// Modal schließen bei Klick außerhalb
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});