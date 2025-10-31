// Configuración del botón de recarga con efecto de loading
    document.addEventListener('DOMContentLoaded', function() {
        // Seleccionar todos los botones de recarga (para manejar múltiples vistas)
        const reloadBtns = document.querySelectorAll('[id^=btn-recargar]');
        
        reloadBtns.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Mostrar el loading
                loading.show({ theme: 'light', customClass: 'table-reload-loading' });
                
                // Simular recarga y refrescar la página
                setTimeout(function() {
                    window.location.reload();
                }, 500);
            });
        });
        
        // Detectar si se necesita scroll horizontal y añadir indicador visual
        const tableContainers = document.querySelectorAll('.responsive-table');
        tableContainers.forEach(function(container) {
            if (container.scrollWidth > container.clientWidth) {
                container.classList.add('has-horizontal-scroll');
            }
        });
    });