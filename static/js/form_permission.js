document.addEventListener('DOMContentLoaded', function() {
    const moduleSelect = document.getElementById("id_module");
    const permList = document.getElementById("perm-list");

    moduleSelect.addEventListener('change', function() {
        const moduleId = this.value;
        fetch(`/security/ajax/module-permissions/${moduleId}/`)
            .then(response => response.json())
            .then(data => {
                permList.innerHTML = '';
                if (data.length === 0) {
                    permList.innerHTML = '<div class="text-neutral-500 italic">Este módulo no tiene permisos asignados.</div>';
                } else {
                    data.forEach(function(perm) {
                        permList.innerHTML += `
                        <label class="flex items-center space-x-2 bg-white px-3 py-2 rounded-lg border border-neutral-200 shadow-sm hover:shadow-md transition w-full perm-item">
                            <input type="checkbox" name="permissions" value="${perm.id}" class="accent-indigo-500">
                            <span class="text-sm font-medium text-neutral-700">${perm.name}</span>
                            <span class="text-xs text-neutral-400 ml-2">${perm.codename}</span>
                        </label>
                        `;
                    });
                }
            });
    });
});