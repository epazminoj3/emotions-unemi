document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  const sidebarClose = document.getElementById('sidebar-close');
  const body = document.body;
  const dropdownButtons = document.querySelectorAll('.dropdown-toggle');

  // Función para abrir sidebar
  function openSidebar() {
    sidebar.classList.remove('-translate-x-full');
    backdrop.classList.remove('hidden');
    body.classList.add('sidebar-open');
  }

  // Función para cerrar sidebar
  function closeSidebar() {
    sidebar.classList.add('-translate-x-full');
    backdrop.classList.add('hidden');
    body.classList.remove('sidebar-open');
  }

  // Toggle del menú (hamburguesa)
  menuToggle?.addEventListener('click', () => {
    if (sidebar.classList.contains('-translate-x-full')) {
      openSidebar();
    } else {
      closeSidebar();
    }
  });

  // Botón cerrar del sidebar
  sidebarClose?.addEventListener('click', closeSidebar);

  // Cerrar al hacer click en el backdrop
  backdrop?.addEventListener('click', closeSidebar);

  // Cerrar con ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !sidebar.classList.contains('-translate-x-full')) {
      closeSidebar();
    }
  });

  // En móvil, cerrar sidebar al hacer click en enlaces
  if (window.innerWidth < 768) {
    const sidebarLinks = sidebar.querySelectorAll('a:not(.dropdown-toggle)');
    sidebarLinks.forEach(link => {
      link.addEventListener('click', closeSidebar);
    });
  }
  
  // Mejorar la funcionalidad de los menús dropdown
  document.querySelectorAll('.dropdown-toggle').forEach(button => {
    button.addEventListener('click', function() {
      const dropdownId = this.getAttribute('aria-controls') || this.getAttribute('data-target') || 
                        this.nextElementSibling?.id;
      
      if (dropdownId) {
        const dropdownContent = document.getElementById(dropdownId);
        
        // Toggle usando clases para la animación
        if (dropdownContent) {
          dropdownContent.classList.toggle('hidden');
          dropdownContent.classList.toggle('show');
        }
        
        // Rotar la flecha
        const arrow = this.querySelector('.dropdown-arrow');
        if (arrow) {
          arrow.classList.toggle('rotate-180');
        }
      }
    });
  });

  // Manejar cambios de tamaño de ventana
  window.addEventListener('resize', () => {
    // Si cambiamos a móvil, asegurarse de que esté cerrado
    if (window.innerWidth < 768) {
      closeSidebar();
    }
  });
});