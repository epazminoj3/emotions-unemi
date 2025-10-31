// Funciones simplificadas para manejar el componente de loading

class LoadingManager {
  constructor() {
    this.defaultLoading = document.getElementById('loading-component');
  }

  // Mostrar loading global
  show(options = {}) {
    const { theme = '', customClass = '' } = options;
    
    // Aplicar clases adicionales si se proporcionan
    if (theme) this.defaultLoading.classList.add(theme);
    if (customClass) this.defaultLoading.classList.add(customClass);
    
    // Mostrar el loading
    this.defaultLoading.classList.remove('hidden');
  }

  // Ocultar loading global
  hide() {
    // Ocultar el loading
    this.defaultLoading.classList.add('hidden');
    
    // Eliminar clases personalizadas
    const classesToKeep = ['loading-overlay', 'hidden'];
    this.defaultLoading.classList.forEach(className => {
      if (!classesToKeep.includes(className)) {
        this.defaultLoading.classList.remove(className);
      }
    });
  }

  // Mostrar loading en un contenedor específico
  showInContainer(container, options = {}) {
    const { theme = 'mini', customClass = '' } = options;
    
    // Crear ID único para este loading
    const loadingId = `loading-${Math.random().toString(36).substring(2, 9)}`;
    
    // Crear HTML del loading simplificado
    const loadingHTML = `
      <div id="${loadingId}" class="loading-overlay ${theme} ${customClass}">
        <img src="/static/img/spinner.gif" alt="Cargando..." class="loading-spinner">
      </div>
    `;
    
    // Añadir al contenedor
    const containerElement = typeof container === 'string' ? document.querySelector(container) : container;
    if (containerElement) {
      const computedStyle = window.getComputedStyle(containerElement);
      if (computedStyle.position === 'static') {
        containerElement.style.position = 'relative';
      }
      
      containerElement.insertAdjacentHTML('beforeend', loadingHTML);
      return loadingId;
    }
    
    return null;
  }

  // Ocultar loading de un contenedor específico
  hideFromContainer(loadingId) {
    const loading = document.getElementById(loadingId);
    if (loading) {
      loading.remove();
    }
  }
}

// Crear instancia global
const loading = new LoadingManager();

// Activar loading automático para formularios con data-loading="true"
document.addEventListener('DOMContentLoaded', function() {
  const loadingForms = document.querySelectorAll('form[data-loading="true"]');
  
  loadingForms.forEach(form => {
    form.addEventListener('submit', function() {
      // Obtener clase personalizada si existe
      const loadingClass = this.getAttribute('data-loading-class') || '';
      const loadingTheme = this.getAttribute('data-loading-theme') || '';
      
      // Mostrar loading
      loading.show({
        theme: loadingTheme,
        customClass: loadingClass
      });
    });
  });
});
