// Modal Elemente
const modal_test = document.getElementById('testModal');
const addTestBtn = document.getElementById('addTestBtn');
const closeTestBtn = document.querySelector('.close');
const cancelTestBtn = document.getElementById('cancelTestBtn');

// Modal öffnen
addTestBtn.addEventListener('click', () => {
    modal_test.style.display = 'block';
});

// Modal schließen
closeTestBtn.addEventListener('click', () => {
    modal_test.style.display = 'none';
});

cancelTestBtn.addEventListener('click', () => {
    modal_test.style.display = 'none';
});

// Modal schließen bei Klick außerhalb
window.addEventListener('click', (event) => {
    if (event.target === modal_test) {
        modal_test.style.display = 'none';
    }
});