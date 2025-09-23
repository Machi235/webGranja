document.addEventListener("DOMContentLoaded", function () {

  const rutas = {
    btnradio2: "{{ url_for('eventos.registro_medicacion') }}",
    btnradio3: "{{ url_for('eventos.registro_vacuna') }}",
    btnradio4: "{{ url_for('eventos.registro_cirugia') }}"
  };


  for (let id in rutas) {
    const radio = document.getElementById(id);
    if (radio) {
      radio.addEventListener("change", function () {
        if (this.checked) {
          window.location.href = rutas[id]; 
        }
      });
    }
  }
});

