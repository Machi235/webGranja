function agregarFila() {
        const contenedor = document.getElementById('contenedorAlimentos');
        const nuevaFila = document.createElement('div');
        nuevaFila.classList.add('fila-alimento');

        nuevaFila.innerHTML = `
            <select name="idAlimento[]" class="select-alimento" required>
                <option value="">-- Seleccionar alimento --</option>
                {% for alimento in alimentos %}
                    <option value="{{ alimento.idAlimento }}">{{ alimento.origen }}</option>
                {% endfor %}
            </select>
            <input type="text" name="cantidadAlimento[]" placeholder="Cantidad" required>
            <input type="text" name="frecuenciaAlimento[]" placeholder="Frecuencia" required>
            <button type="button" class="btn btn-danger" onclick="eliminarFila(this)">Eliminar</button>
        `;
        contenedor.appendChild(nuevaFila);
    }

    function eliminarFila(boton) {
        boton.parentElement.remove();
    }

    document.getElementById('idAnimal').addEventListener('change', function() {
    const idAnimal = this.value;
    const alimentoSelect = document.getElementById('idAlimento');

    if (!idAnimal) return;

    fetch(`/alimentos_por_animal/${idAnimal}`)
        .then(response => response.json())
        .then(data => {
            alimentoSelect.innerHTML = '<option value="">Seleccione un alimento</option>';
            data.forEach(alimento => {
                alimentoSelect.innerHTML += `<option value="${alimento.idAlimento}">${alimento.origen}</option>`;
            });
        });
});
document.getElementById('btnGuardarDieta').addEventListener('click', function() {
    const form = document.getElementById('formCrearDieta');
    const formData = new FormData(form);

    fetch('/crear_dieta', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.status === 200) {
            Swal.fire({
                icon: 'success',
                title: '¡Dieta creada!',
                text: 'La dieta se ha guardado correctamente.',
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'Aceptar'
            }).then(() => {
                form.reset(); // Limpiar formulario después de confirmar
            });
        } else if (response.status === 404) {
            Swal.fire({
                icon: 'error',
                title: 'Animal no encontrado',
                text: 'El animal seleccionado no existe en la base de datos.'
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ocurrió un error al guardar la dieta. Intenta nuevamente.'
            });
        }
    })
    .catch(error => {
        console.error("Error en fetch:", error);
        Swal.fire({
            icon: 'error',
            title: 'Error de conexión',
            text: 'No se pudo conectar con el servidor.'
        });
    });
});