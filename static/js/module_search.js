/**
 * Module Search - Búsqueda de módulos en tiempo real
 * 
 * Este script maneja la funcionalidad de búsqueda de módulos
 * mostrando resultados en tiempo real mientras el usuario escribe
 */

document.addEventListener('DOMContentLoaded', function() {
    // Seleccionamos todos los buscadores de módulos que puedan existir
    const moduleSearchInputs = document.querySelectorAll('[id$="-module-search"]');
    
    moduleSearchInputs.forEach(searchInput => {
        if (!searchInput) return;
        
        const searchContainer = searchInput.closest('.module-search-container');
        const resultsContainer = searchContainer.querySelector('.module-results');
        const moduleItems = searchContainer.querySelectorAll('.module-item');
        const noResultsElement = searchContainer.querySelector('.module-no-results');
        const resultsInfoElement = searchContainer.querySelector('.module-results-info');
        
        // Función para filtrar módulos
        function filterModules(query) {
            query = query.toLowerCase().trim();
            let matchCount = 0;
            
            moduleItems.forEach(item => {
                const moduleName = item.dataset.moduleName.toLowerCase();
                const moduleDescription = item.querySelector('p').textContent.toLowerCase();
                
                // Verificamos si el nombre o la descripción contienen la consulta
                if (moduleName.includes(query) || moduleDescription.includes(query)) {
                    item.classList.remove('hidden');
                    matchCount++;
                } else {
                    item.classList.add('hidden');
                }
            });
            
            // Actualizamos el estado de "no hay resultados"
            if (matchCount === 0 && query !== '') {
                noResultsElement.classList.remove('hidden');
                resultsInfoElement.classList.add('hidden');
            } else {
                noResultsElement.classList.add('hidden');
                
                if (query === '') {
                    resultsInfoElement.classList.remove('hidden');
                } else {
                    resultsInfoElement.classList.add('hidden');
                }
            }
            
            // Mostramos u ocultamos el contenedor de resultados
            if (query === '') {
                resultsContainer.classList.add('hidden');
            } else {
                resultsContainer.classList.remove('hidden');
            }
        }
        
        // Event listeners para el input de búsqueda
        searchInput.addEventListener('input', function() {
            filterModules(this.value);
        });
        
        searchInput.addEventListener('focus', function() {
            if (this.value.trim() !== '') {
                resultsContainer.classList.remove('hidden');
            }
        });
        
        // Cerrar el dropdown al hacer click fuera
        document.addEventListener('click', function(event) {
            if (!searchContainer.contains(event.target)) {
                resultsContainer.classList.add('hidden');
            }
        });
        
        // Prevenir que el click dentro del contenedor de resultados cierre el dropdown
        resultsContainer.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    });
});
