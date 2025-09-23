 function vaciarFormulario() {
      // selecciona todos los inputs dentro del formulario
      document.querySelectorAll("#miFormulario input").forEach(input => {
        // borra lo que el usuario escribió
        input.value = "";
      });
    

       document.querySelectorAll("#miFormulario select").forEach(select => {
        // borra lo que el usuario escribió
        select.selectedIndex = 0;
      });

      document.querySelectorAll("#miFormulario textarea").forEach(textarea => {
        // borra lo que el usuario escribió
        textarea.value = "";
      });
    }

//-----------------------------------------------------------------------------------------------

function alerta(){
  const camposVacios = document.querySelector("#camposVacios")
    const cerrar = document.querySelector("#volver")
      camposVacios.showModal();
      
    cerrar.addEventListener("click", () => {
      camposVacios.close();
    })
}

function confirmacion(){
  const camposCompletos = document.querySelector("#camposCompletos")
    camposCompletos.showModal();
  setTimeout(() => {
    window.location.href='../moduloAnimal/crearAnimal.html'
  },1000)
}

function validar() {
    let nombre = document.getElementById('nombre').value;
    let habitat = document.getElementById('habitat').value;
    let tipo = document.getElementById('tipo').value;
    let horas= document.getElementById('horas').value;
    let minutos= document.getElementById('minutos').value;
    let detalles= document.getElementById('detalles').value;

    if (nombre === '' || habitat === ''|| tipo === ''|| horas === '' || minutos === '' || detalles === '') {
      alerta();
    } else {
      confirmacion();
    }
}
