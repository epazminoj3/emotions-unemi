// Script para seleccionar permisos básicos por modelo y globalmente

document.addEventListener('DOMContentLoaded', function() {
    // Botón por modelo
    document.querySelectorAll('.select-basic-perms').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var model = btn.getAttribute('data-model');
            var checkboxes = document.querySelectorAll('.basic-perm-checkbox[data-model="' + model + '"]');
            checkboxes.forEach(function(cb) {
                var codename = cb.getAttribute('data-codename');
                if (
                    codename.startsWith('view_') ||
                    codename.startsWith('add_') ||
                    codename.startsWith('change_') ||
                    codename.startsWith('delete_')
                ) {
                    cb.checked = true;
                }
            });
        });
    });

    // Botones globales
    document.querySelectorAll('.select-all-perms').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var action = btn.getAttribute('data-action');
            var checkboxes = document.querySelectorAll('.basic-perm-checkbox');
            checkboxes.forEach(function(cb) {
                var codename = cb.getAttribute('data-codename');
                if (codename.startsWith(action + '_')) {
                    cb.checked = true;
                }
            });
        });
    });
});