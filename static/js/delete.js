// Función para abrir el modal de eliminación
function openDeleteModal(url, title, details) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const modalDetails = document.getElementById('modalDetails');
    
    // Configurar la URL del formulario
    form.action = url;
    
    // Actualizar el título si se proporciona
    if (title) {
        document.querySelector('.modal-message').textContent = title;
    }
    
    // Actualizar los detalles si se proporcionan
    if (details && details.length > 0) {
        modalDetails.innerHTML = details.map(detail => `
            <div class="detail-item">
                <i class="${detail.icon}"></i>
                <span class="detail-label">${detail.label}:</span>
                <span class="detail-value">${detail.value}</span>
            </div>
        `).join('');
    } else {
        modalDetails.innerHTML = '';
    }
    
    // Mostrar el modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

// Función para cerrar el modal
function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

// Cerrar modal con Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeDeleteModal();
    }
});

// Función global para configurar botones de eliminación
function setupDeleteButtons() {
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.href;
            const title = this.dataset.title || '¿Estás seguro de que deseas eliminar este elemento?';
            const details = this.dataset.details ? JSON.parse(this.dataset.details) : [];
            
            openDeleteModal(url, title, details);
        });
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    setupDeleteButtons();
});