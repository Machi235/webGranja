// =====================
// Vaciar formulario
// =====================
function vaciarFormulario() {
  document.querySelectorAll("#miFormulario input").forEach(input => {
    input.value = "";
  });

  document.querySelectorAll("#miFormulario select").forEach(select => {
    select.selectedIndex = 0;
  });
}

// =====================
// Validación y envío
// =====================
function validar() {
  let nombreHabitat = document.getElementById('nombreHabitat').value.trim();
  let estado = document.getElementById('estado').value.trim();
  let tipo = document.getElementById('tipo').value.trim();
  let capacidad = document.getElementById('capacidad').value.trim();
  let max_temp = document.getElementById('maxTemperatura').value.trim();
  let min_temp = document.getElementById('minTemperatura').value.trim();

  // Validar campos obligatorios
  if (nombreHabitat === '' || estado === '' || tipo === '' || capacidad === '') {
    Swal.fire({
      icon: 'error',
      title: 'Campos incompletos',
      text: 'Por favor, completa todos los campos obligatorios marcados con *',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#d33'
    });
    return;
  }

 if (min_temp >= max_temp){
    Swal.fire({
      icon: 'error',
      title: 'La temperatura minima no puede ser superior a la temperatura maxima',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#d33'
    });
    return;

  }

  document.getElementById('miFormulario').submit();
}

// =====================
// Agregar mt² a tamaño
// =====================
const tamaño = document.getElementById("tamaño");

tamaño.addEventListener("blur", () => {
  let valor = tamaño.value.trim();
  if (valor !== "" && !valor.endsWith("mt²")) {
    tamaño.value = valor + " mt²";
  }
});

// =====================
// Formato en temperatura
// =====================
document.querySelectorAll(".temperatura").forEach(input => {
  input.addEventListener("blur", () => {
    let valor = input.value.trim();
    if (valor !== "" && !valor.endsWith("°C")) {
      input.value = valor + "°C";
    }
  });
});

// Solo permitir números en campos de temperatura
document.querySelectorAll('.temperatura').forEach(input => {
  input.addEventListener('keydown', (event) => {
    if (['Backspace', 'Tab', 'Enter', 'Delete', '-', 'ArrowRight', 'ArrowLeft'].includes(event.key)) {
      return;
    }
    if (event.key < '0' || event.key > '9') {
      event.preventDefault();
    }
  });
});
