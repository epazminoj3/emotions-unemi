document.addEventListener('DOMContentLoaded', function() {
    // Permite solo un menú abierto a la vez
    document.querySelectorAll('[id^="menu-"]').forEach(function(menuDiv) {
      menuDiv.previousElementSibling.addEventListener('click', function() {
        document.querySelectorAll('[id^="menu-"]').forEach(function(otherDiv) {
          if (otherDiv !== menuDiv) {
            otherDiv.classList.add('hidden');
          }
        });
        menuDiv.classList.toggle('hidden');
      });
    });
});