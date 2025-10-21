 function vaciarFormulario() {
      // selecciona todos los inputs dentro del formulario
      document.querySelectorAll("#miFormulario input").forEach(input => {
        // borra lo que el usuario escribió
        input.value = "";
      });
    

       document.querySelectorAll("#miFormulario select").forEach(select => {
        // borra lo que el usuario escribió
        select.value = 0;
      });

      document.querySelectorAll("#miFormulario textarea").forEach(textarea => {
        // borra lo que el usuario escribió
        textarea.value = "";
      });

      $(".select-multiple").val(null).trigger("change");
    }

//-----------------------------------------------------------------------------------------------

function validar() {
  let especie = document.getElementById('idEspecie').value.trim();
  let usuario = document.getElementById('idUsuario').value.trim();
  let habitat = document.getElementById('habitat').value.trim();
  let tipo = document.getElementById('tipo').value.trim();
  let duracion = document.getElementById('duracion').value.trim();
  let realizacion = document.getElementById('realizacion').value.trim();
  let detalles = document.getElementById('detalles').value.trim();

  // Validar campos obligatorios
  if (especie === '' || usuario === '' || habitat === '' || tipo === '' || duracion === '' || realizacion === '' || detalles === '') {
    Swal.fire({
      icon: 'error',
      title: 'Campos incompletos',
      text: 'Por favor, completa todos los campos obligatorios marcados con *',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#d33'
    });
    return;
  }
  
  document.getElementById('miFormulario').submit();

}


//-----------------------------------------------------------------------------------------------

$('.select-multiple').select2({
  createTag: function (params) {
    var term = $.trim(params.term);

    if (term === '') {
      return null;
    }

    return {
      id: term,
      text: term,
      newTag: false // add additional parameters
    }
  }
});

//-----------------------------------------------------------------------------------------------

const hoy = new Date(). toISOString().split("T")[0];
document.getElementById("realizacion").setAttribute("min", hoy);