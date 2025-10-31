document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modal');
    const openModal = document.getElementById('open_modal');
    const closeModal = document.getElementById('close_modal');
    const body = document.getElementById('body');
    
    // Función para abrir el modal con animación
    function openModalWithAnimation() {
        modal.classList.remove('closing');
        modal.style.display = 'flex';
        body.style.overflow = 'hidden';
        
        // Forzar reflow para asegurar que la clase se aplique
        modal.offsetHeight;
        
        // Agregar clase de entrada con un pequeño delay
        requestAnimationFrame(() => {
            modal.classList.add('show');
        });
    }
    
    // Función para cerrar el modal con animación
    function closeModalWithAnimation() {
        modal.classList.remove('show');
        modal.classList.add('closing');
        body.style.overflow = 'auto';
        
        // Esperar a que termine la animación antes de ocultar
        setTimeout(() => {
            modal.style.display = 'none';
            modal.classList.remove('closing');
        }, 200);
    }
    
    // Event listeners
    if (openModal) {
        openModal.addEventListener('click', function(e) {
            e.preventDefault();
            openModalWithAnimation();
        });
    }
    
    if (closeModal) {
        closeModal.addEventListener('click', function(e) {
            e.preventDefault();
            closeModalWithAnimation();
        });
    }
    
    // Cerrar modal al hacer clic en el backdrop
    modal.addEventListener('click', function(e) {
        if (e.target === modal && modal.classList.contains('show')) {
            closeModalWithAnimation();
        }
    });
    
    // Cerrar modal con tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            closeModalWithAnimation();
        }
    });
    
    // Prevenir scroll del body cuando el modal está abierto
    modal.addEventListener('wheel', function(e) {
        e.preventDefault();
    }, { passive: false });
    
    // Manejar el enfoque para accesibilidad
    modal.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstFocusable = focusableElements[0];
            const lastFocusable = focusableElements[focusableElements.length - 1];
            
            if (e.shiftKey) {
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        }
    });
    
    // Focus automático en el botón de cerrar cuando se abre el modal
    modal.addEventListener('transitionend', function(e) {
        if (e.target === modal && modal.classList.contains('show')) {
            closeModal.focus();
        }
    });
});