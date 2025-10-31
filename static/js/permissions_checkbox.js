document.addEventListener('DOMContentLoaded', function() {
    const filterInput = document.getElementById('perm-filter');
    const permItems = document.querySelectorAll('.perm-item');
    filterInput.addEventListener('input', function() {
        const val = filterInput.value.toLowerCase();
        permItems.forEach(function(item) {
            const text = item.innerText.toLowerCase();
            item.style.display = text.includes(val) ? '' : 'none';
        });
    });
});