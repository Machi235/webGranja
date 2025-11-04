let alimentosDisponibles = [];

        function cargarAlimentos() {
            const idAnimal = document.getElementById('idAnimal').value;
            if (!idAnimal) return;

            fetch(`/dietas/alimentos_por_animal/${idAnimal}`)
                .then(res => res.json())
                .then(data => {
                    alimentosDisponibles = data;
                    // Actualizar selects existentes
                    document.querySelectorAll('.alimento-select').forEach(select => {
                        select.innerHTML = '<option value="">Seleccione un alimento</option>';
                        data.forEach(alimento => {
                            const opt = document.createElement('option');
                            opt.value = alimento.idAlimento;
                            opt.textContent = alimento.Origen;
                            select.appendChild(opt);
                        });
                    });
                })
                .catch(err => console.error('Error cargando alimentos:', err));
        }

        function agregarFila() {
            const contenedor = document.getElementById('contenedorAlimentos');
            const fila = document.createElement('div');
            fila.className = 'fila-alimento mb-2 d-flex gap-2';

            const select = document.createElement('select');
            select.name = 'idAlimento[]';
            select.className = 'form-select alimento-select';
            select.required = true;
            select.innerHTML = '<option value="">Seleccione un alimento</option>';
            alimentosDisponibles.forEach(alimento => {
                const opt = document.createElement('option');
                opt.value = alimento.idAlimento;
                opt.textContent = alimento.Origen;
                select.appendChild(opt);
            });

            const cantidad = document.createElement('input');
            cantidad.name = 'cantidadAlimento[]';
            cantidad.placeholder = 'Cantidad';
            cantidad.className = 'form-control';
            cantidad.required = true;

            const frecuencia = document.createElement('input');
            frecuencia.name = 'frecuenciaAlimento[]';
            frecuencia.placeholder = 'Frecuencia';
            frecuencia.className = 'form-control';
            frecuencia.required = true;

            const btnEliminar = document.createElement('button');
            btnEliminar.type = 'button';
            btnEliminar.className = 'btn btn-danger';
            btnEliminar.textContent = 'Eliminar';
            btnEliminar.onclick = () => eliminarFila(btnEliminar);

            fila.appendChild(select);
            fila.appendChild(cantidad);
            fila.appendChild(frecuencia);
            fila.appendChild(btnEliminar);

            contenedor.appendChild(fila);
        }

        function eliminarFila(btn) {
            btn.parentElement.remove();
        }

        // Envío del formulario con fetch + modal
        document.getElementById("formCrearDieta").addEventListener("submit", function(e) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);

            fetch(form.action, {
                method: "POST",
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: '¡Éxito!',
                        text: 'La dieta se ha creado correctamente.',
                        icon: 'success',
                        showCancelButton: true,
                        confirmButtonText: 'Ver Dietas',
                        cancelButtonText: 'Cerrar'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            window.location.href = "{{ url_for('dietas.ver_dietas') }}";
                        }
                    });

                    // Limpiar formulario
                    form.reset();
                    document.getElementById('contenedorAlimentos').innerHTML = '';
                } else if (data.error) {
                    Swal.fire('Error', data.error, 'error');
                }
            })
            .catch(err => {
                console.error(err);
                Swal.fire('Error', 'Ocurrió un error inesperado.', 'error');
            });
        });

        // Agrega una fila inicial al cargar
        window.onload = () => agregarFila();