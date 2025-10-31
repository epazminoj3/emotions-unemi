document.addEventListener('DOMContentLoaded', function() {
        // Mejorar la experiencia en móviles para selects múltiples
        const multipleSelects = document.querySelectorAll('select[multiple]');
        
        // Ajustar tamaño en móviles
        function adjustSelectSize() {
            if (window.innerWidth < 640) {
                multipleSelects.forEach(select => {
                    select.setAttribute('size', '4');
                });
            } else {
                multipleSelects.forEach(select => {
                    select.setAttribute('size', '6');
                });
            }
        }
        
        // Ejecutar al cargar y al redimensionar
        adjustSelectSize();
        window.addEventListener('resize', adjustSelectSize);
        
        // Mejorar indicadores visuales para campos requeridos
        const requiredInputs = document.querySelectorAll('input[required], select[required], textarea[required]');
        requiredInputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (!this.value.trim()) {
                    this.classList.add('border-danger-300');
                    this.classList.remove('border-gray-300');
                } else {
                    this.classList.remove('border-danger-300');
                    this.classList.add('border-gray-300');
                }
            });
        });
    });