document.getElementById("formCrearDieta").addEventListener("submit", function(event) {
    event.preventDefault(); // Evita que se recargue la página

    const form = event.target;
    const formData = new FormData(form);

    fetch("/crear_dieta", {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        if (data === "OK") {
            Swal.fire({
                icon: "success",
                title: "¡Dieta creada!",
                text: "La dieta se ha guardado correctamente",
                confirmButtonText: "Aceptar"
            }).then(() => {
                // Limpia el formulario después de guardar
                form.reset();

                // Reiniciar los alimentos dejando solo una fila vacía
                const contenedor = document.getElementById("contenedorAlimentos");
                contenedor.innerHTML = `
                    <div class="fila-alimento mb-2 d-flex gap-2">
                        <select name="idAlimento[]" class="form-select alimento-select" required>
                            <option value="">Seleccione un alimento</option>
                        </select>
                        <input type="text" name="cantidadAlimento[]" class="form-control" placeholder="Cantidad" required>
                        <input type="text" name="frecuenciaAlimento[]" class="form-control" placeholder="Frecuencia" required>
                        <button type="button" class="btn btn-danger" onclick="eliminarFila(this)">Eliminar</button>
                    </div>
                `;

                // Recargar los alimentos según el animal seleccionado
                const idAnimal = document.getElementById('idAnimal').value;
                if (idAnimal) {
                    fetch(`/alimentos_por_animal/${idAnimal}`)
                        .then(response => response.json())
                        .then(data => {
                            const select = contenedor.querySelector('.alimento-select');
                            select.innerHTML = '<option value="">Seleccione un alimento</option>';
                            data.forEach(alimento => {
                                select.innerHTML += `<option value="${alimento.idAlimento}">${alimento.origen}</option>`;
                            });
                        });
                }
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "Hubo un problema al guardar la dieta"
            });
        }
    })
    .catch(err => {
        console.error(err);
        Swal.fire({
            icon: "error",
            title: "Error inesperado",
            text: "No se pudo conectar con el servidor"
        });
    });
});




// --- Cargar alimentos por especie al seleccionar animal ---
        document.getElementById('idAnimal').addEventListener('change', function() {
            const idAnimal = this.value;
            if (!idAnimal) return;

            fetch(`/alimentos_por_animal/${idAnimal}`)
                .then(response => response.json())
                .then(data => {
                    // Actualizar TODOS los selects de alimentos
                    document.querySelectorAll('.alimento-select').forEach(select => {
                        select.innerHTML = '<option value="">Seleccione un alimento</option>';
                        data.forEach(alimento => {
                            select.innerHTML += `<option value="${alimento.idAlimento}">${alimento.origen}</option>`;
                        });
                    });
                })
                .catch(err => console.error(err));
        });

        // --- Agregar nueva fila de alimento ---
        function agregarFila() {
            const contenedor = document.getElementById('contenedorAlimentos');
            const nuevaFila = document.createElement('div');
            nuevaFila.classList.add('fila-alimento', 'mb-2', 'd-flex', 'gap-2');

            nuevaFila.innerHTML = `
                <select name="idAlimento[]" class="form-select alimento-select" required>
                    <option value="">Seleccione un alimento</option>
                </select>
                <input type="text" name="cantidadAlimento[]" class="form-control" placeholder="Cantidad" required>
                <input type="text" name="frecuenciaAlimento[]" class="form-control" placeholder="Frecuencia" required>
                <button type="button" class="btn btn-danger" onclick="eliminarFila(this)">Eliminar</button>
            `;

            contenedor.appendChild(nuevaFila);

            // Recargar alimentos para el nuevo select
            const idAnimal = document.getElementById('idAnimal').value;
            if (idAnimal) {
                fetch(`/alimentos_por_animal/${idAnimal}`)
                    .then(response => response.json())
                    .then(data => {
                        const select = nuevaFila.querySelector('.alimento-select');
                        select.innerHTML = '<option value="">Seleccione un alimento</option>';
                        data.forEach(alimento => {
                            select.innerHTML += `<option value="${alimento.idAlimento}">${alimento.origen}</option>`;
                        });
                    });
            }
        }

        // --- Eliminar fila de alimento ---
        function eliminarFila(button) {
            button.parentElement.remove();
        }